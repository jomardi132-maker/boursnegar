#!/usr/bin/env python3
"""Evidence-gated Local -> Production synchronization orchestrator.

Default mode is read-only planning. Network fetching and Production writes are
separate explicit gates. Existing proven pipelines are reused; no fabricated
facts or unresolved candidates are ever exported.
"""
from __future__ import annotations
import argparse, hashlib, json, re, shlex, sqlite3, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable

def run(cmd, *, cwd=ROOT, timeout=600, capture=False):
    print(json.dumps({'step': ' '.join(map(str, cmd))}, ensure_ascii=False), flush=True)
    return subprocess.run(cmd, cwd=cwd, check=True, timeout=timeout,
                          text=True, capture_output=capture, encoding='utf-8', errors='replace')

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def server_symbols(target):
    sys.path.insert(0, str(ROOT/'data-service'))
    from scripts.ingestion_console import discover_remote
    return discover_remote(target, lambda _: None)

def existing_local_artifacts(artifact_root: Path) -> list[Path]:
    artifact_dirs = []
    for manifest in sorted(artifact_root.rglob('manifest.json')):
        directory = manifest.parent
        if directory.parent.name == 'aggregate':
            continue
        if directory.name not in {'browser', 'normalized', 'events', 'codalpy'}:
            continue
        artifact_dirs.append(directory)
    return artifact_dirs

def imported_artifact_paths(db: Path) -> set[str]:
    con = sqlite3.connect(db)
    try:
        columns = {row[1] for row in con.execute('PRAGMA table_info(runs)')}
        paths = set()
        if 'source_path' not in columns:
            if 'summary' not in columns:
                return set()
            for (summary,) in con.execute("SELECT summary FROM runs WHERE stage='local-artifact-import' AND summary IS NOT NULL"):
                try:
                    source_path = json.loads(summary).get('source_path')
                except (TypeError, json.JSONDecodeError):
                    continue
                if source_path:
                    paths.add(str(Path(source_path).resolve()))
            return paths
        paths.update(str(Path(row[0]).resolve()) for row in con.execute('SELECT source_path FROM runs WHERE source_path IS NOT NULL'))
        if 'summary' in columns:
            for (summary,) in con.execute("SELECT summary FROM runs WHERE stage='local-artifact-import' AND summary IS NOT NULL"):
                try:
                    source_path = json.loads(summary).get('source_path')
                except (TypeError, json.JSONDecodeError):
                    continue
                if source_path:
                    paths.add(str(Path(source_path).resolve()))
        return paths
    except sqlite3.OperationalError:
        return set()

def import_existing_local_artifacts(db: Path, artifact_root: Path) -> int:
    already_imported = imported_artifact_paths(db)
    artifact_dirs = [p for p in existing_local_artifacts(artifact_root) if str(p.resolve()) not in already_imported]
    if not artifact_dirs:
        return 0
    for directory in artifact_dirs:
        run([PYTHON, 'data-service/scripts/build_local_codal_db.py', '--db', str(db), '--artifact', str(directory)], timeout=300)
    return len(artifact_dirs)

def local_symbol_rows(db: Path) -> dict[str, dict[str, object]]:
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    rows = {}
    for row in con.execute(
        """
        SELECT s.symbol,
               s.status,
               COALESCE(s.standard_count, 0) AS standard_count,
               COALESCE(s.period_count, 0) AS period_count,
               COUNT(DISTINCT n.tracing_no) AS notice_count
        FROM symbols s
        LEFT JOIN notices n ON n.symbol = s.symbol
        GROUP BY s.symbol
        """
    ):
        rows[row['symbol']] = dict(row)
    return rows

_DERIVED_SYMBOL_RE = re.compile(r'[\d۰-۹]+$')

def base_symbol(symbol: str) -> str:
    return _DERIVED_SYMBOL_RE.sub('', symbol).strip()

def selection_priority(symbol: str, info: dict[str, object], remote_status: str) -> tuple[int, int, int, str]:
    status_rank = {'comparable': 0, 'incomplete': 1}.get(str(info.get('status') or remote_status), 2)
    derived_rank = 1 if base_symbol(symbol) != symbol else 0
    periods = int(info.get('period_count') or 0)
    facts = int(info.get('standard_count') or 0)
    notices = int(info.get('notice_count') or 0)
    return (status_rank, derived_rank, -periods, -facts - notices, symbol)

def select_symbols(remote: list[dict[str, object]], local_rows: dict[str, dict[str, object]], limit: int) -> list[str]:
    candidates = []
    for row in remote:
        symbol = str(row.get('symbol') or '')
        if not symbol:
            continue
        info = local_rows.get(symbol, {})
        local_status = str(info.get('status') or '')
        remote_status = str(row.get('status') or '')
        if local_status == 'complete' or remote_status == 'complete':
            continue
        candidates.append((selection_priority(symbol, info, remote_status), symbol))
    return [symbol for _, symbol in sorted(candidates)[:limit]]

def aggregate_manifests(run_root, out, kind):
    out.mkdir(parents=True, exist_ok=True); errors=[]; record_count=0
    expected_source = 'codalpy/codal.ir' if kind == 'codalpy' else 'browser/codal.ir'
    target=out/f'{kind}.jsonl'
    temporary=out/f'.{kind}.jsonl.tmp'
    with temporary.open('w', encoding='utf-8') as handle:
        roots = [run_root] if isinstance(run_root, Path) else list(run_root)
        sources = sorted(source for root in roots for source in root.rglob(f'{kind}/*.jsonl'))
        for source in sources:
            if source.parent.parent.name == 'aggregate':
                continue
            with source.open(encoding='utf-8', errors='replace') as input_handle:
                for number, line in enumerate(input_handle, 1):
                    if not line.strip(): continue
                    try: row=json.loads(line)
                    except json.JSONDecodeError as exc:
                        errors.append(f'{source}:{number}: invalid JSON: {exc}'); continue
                    required=('symbol','from_jalali','to_jalali','output_type','payload','source','retrieved_at')
                    missing=[key for key in required if not row.get(key)]
                    if missing or not isinstance(row.get('payload'), dict):
                        errors.append(f'{source}:{number}: invalid record fields={missing or ["payload"]}'); continue
                    if row.get('source') != expected_source:
                        errors.append(f'{source}:{number}: untrusted source={row.get("source")}'); continue
                    handle.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
                    record_count += 1
    if errors:
        temporary.unlink(missing_ok=True)
        raise SystemExit(f'{kind} validation failed: {len(errors)} invalid records')
    temporary.replace(target)
    manifest={'schema':'boursnegar-codalpy-jsonl-v1','source':expected_source,'generated_at':datetime.now(timezone.utc).isoformat(),
              'files':[{'path':target.name,'records':record_count,'sha256':sha256(target)}],'errors':errors}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest

def manifest_kind(manifest):
    if manifest.get('schema') == 'boursnegar-codal-notices-v1':
        return 'events'
    return 'codalpy' if manifest.get('source') == 'codalpy/codal.ir' else 'normalized'

def aggregate_events(run_root, out):
    out.mkdir(parents=True, exist_ok=True); record_count=0
    target=out/'events.jsonl'; temporary=out/'.events.jsonl.tmp'
    with temporary.open('w', encoding='utf-8') as handle:
        roots = [run_root] if isinstance(run_root, Path) else list(run_root)
        sources = sorted(source for root in roots for source in root.rglob('events/notice-events.jsonl'))
        for source in sources:
            if source.parent.parent.name == 'aggregate':
                continue
            with source.open(encoding='utf-8', errors='replace') as input_handle:
                for line in input_handle:
                    if not line.strip(): continue
                    row=json.loads(line)
                    if not row.get('symbol') or not row.get('tracing_no') or not row.get('source'):
                        temporary.unlink(missing_ok=True)
                        raise SystemExit(f'event validation failed: {source}')
                    handle.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
                    record_count += 1
    temporary.replace(target)
    manifest={'schema':'boursnegar-codal-notices-v1','source':'browser/codal.ir','generated_at':datetime.now(timezone.utc).isoformat(),
              'files':[{'path':target.name,'records':record_count,'sha256':sha256(target)}],'errors':[]}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest

def symbol_run_root(run_root: Path, symbol: str) -> Path:
    """Reuse the newest checkpoint for a symbol across interrupted runs."""
    candidates = sorted(
        (p / symbol for p in run_root.iterdir() if p.is_dir() and (p / symbol).is_dir()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else run_root

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',default='artifacts/local-ingestion.sqlite3'); p.add_argument('--ssh-target',default='boursnegar')
    p.add_argument('--from-jalali',default='1404/01/01'); p.add_argument('--to-jalali',required=True)
    p.add_argument('--limit',type=int,default=10); p.add_argument('--run-root',default='artifacts/auto-sync')
    p.add_argument('--apply',action='store_true'); p.add_argument('--allow-download',action='store_true')
    p.add_argument('--skip-local',action='store_true'); p.add_argument('--skip-production',action='store_true')
    p.add_argument('--skip-preimport', action='store_true', help='Skip importing already downloaded local artifacts before planning')
    args=p.parse_args(); db=Path(args.db).resolve(); run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); run_root=Path(args.run_root).resolve()/run_id
    run_base = Path(args.run_root).resolve()
    already_imported = imported_artifact_paths(db) if run_base.exists() else set()
    preimport_pending = len([p for p in existing_local_artifacts(run_base) if str(p.resolve()) not in already_imported]) if run_base.exists() else 0
    imported_dirs = 0
    if args.apply and not args.skip_preimport and run_base.exists():
        imported_dirs = import_existing_local_artifacts(db, run_base)
        if imported_dirs:
            run([PYTHON, 'data-service/scripts/recalculate_local_coverage.py', '--db', str(db)], timeout=300)
    remote=server_symbols(args.ssh_target)
    local_rows=local_symbol_rows(db)
    selected=select_symbols(remote, local_rows, args.limit)
    plan={'run_id':run_id,'server_symbols':len(remote),'selected_symbols':selected,'apply':args.apply,'allow_download':args.allow_download,'preimport_pending_dirs':0 if args.skip_preimport else preimport_pending,'preimported_artifact_dirs':imported_dirs}
    print(json.dumps({'plan':plan},ensure_ascii=False,indent=2))
    if not args.apply:
        print(json.dumps({'status':'dry-run','next':'add --apply; add --allow-download to fetch missing Local data'},ensure_ascii=False)); return
    if args.allow_download is False and not args.skip_local:
        raise SystemExit('Local completion may fetch data; pass --allow-download explicitly')
    if not args.skip_local:
        aggregation_roots=[]
        for symbol in selected:
            target=symbol_run_root(run_base, symbol)/symbol
            if target.parent == run_base:
                target=run_root/symbol
            aggregation_roots.append(target)
            cmd=[PYTHON,'data-service/scripts/daily_local_ingestion.py','--symbol',symbol,'--from-jalali',args.from_jalali,'--to-jalali',args.to_jalali,
                 '--out',str(target),'--local-db',str(db),'--codalpy-first','--download-documents','--professional-documents','--defer-pdf']
            run(cmd,timeout=1800)
        run([PYTHON,'data-service/scripts/recalculate_local_coverage.py','--db',str(db)])
    # Ensure newly fetched Codalpy-first results enter the same local DB before export.
    if not args.skip_local:
        already_imported = imported_artifact_paths(db)
        for codal_dir in run_base.glob('*/*/codalpy'):
            if codal_dir.parent.name == 'aggregate' or str(codal_dir.resolve()) in already_imported:
                continue
            if (codal_dir/'manifest.json').exists():
                run([PYTHON,'data-service/scripts/build_local_codal_db.py','--db',str(db),'--artifact',str(codal_dir)])
    manifests=[]
    # Aggregate only this run; historical runs are already tracked by the local ledger.
    aggregate_root=aggregation_roots if not args.skip_local else run_root
    for kind in ('codalpy','normalized'):
        manifest=aggregate_manifests(aggregate_root,run_root/'aggregate'/kind,kind)
        if manifest['files'][0]['records']: manifests.append(manifest)
    events_manifest=aggregate_events(aggregate_root,run_root/'aggregate/events')
    if events_manifest['files'][0]['records']: manifests.append(events_manifest)
    if not manifests:
        print(json.dumps({'status':'no-new-normalized-records','run_root':str(run_root)},ensure_ascii=False)); return
    if args.skip_production:
        print(json.dumps({'status':'local-complete-production-skipped','manifests':[str(run_root/'aggregate'/manifest_kind(m)/'manifest.json') for m in manifests]},ensure_ascii=False)); return
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); remote_backup=f'/var/backups/boursnegar/{stamp}-auto-local-to-production.dump'
    run(['ssh',args.ssh_target,f"sudo -u postgres pg_dump -Fc -d boursnegar_db | sudo tee {shlex.quote(remote_backup)} >/dev/null"],timeout=900)
    remote_tmp=f'/tmp/boursnegar-auto-sync-{run_id}'
    run(['ssh',args.ssh_target,f'install -d -m 0700 {remote_tmp}'],timeout=60)
    for manifest in manifests:
        kind=manifest_kind(manifest)
        run(['scp',str(run_root/'aggregate'/kind/f'{kind}.jsonl'),f'{args.ssh_target}:{remote_tmp}/{kind}.jsonl'],timeout=300)
        run(['scp',str(run_root/'aggregate'/kind/'manifest.json'),f'{args.ssh_target}:{remote_tmp}/{kind}-manifest.json'],timeout=300)
    remote_dir=f'/var/www/boursnegar-data-current/staging/auto-sync/{run_id}'
    run(['ssh',args.ssh_target,f'sudo install -d -m 0750 {remote_dir}'],timeout=60)
    for manifest in manifests:
        kind=manifest_kind(manifest)
        run(['ssh',args.ssh_target,f'sudo install -m 0640 {remote_tmp}/{kind}.jsonl {remote_dir}/{kind}.jsonl; sudo install -m 0640 {remote_tmp}/{kind}-manifest.json {remote_dir}/{kind}-manifest.json'],timeout=60)
        remote_manifest=f'{remote_dir}/{kind}-manifest.json'
        run(['ssh',args.ssh_target,f'cd /var/www/boursnegar-data-current && sudo env PYTHONPATH=. venv/bin/python scripts/codalpy_remote_import.py --manifest {remote_manifest} --symbol "*" --batch-size 500'],timeout=1800)
        repeat=run(['ssh',args.ssh_target,f'cd /var/www/boursnegar-data-current && sudo env PYTHONPATH=. venv/bin/python scripts/codalpy_remote_import.py --manifest {remote_manifest} --symbol "*" --batch-size 500'],timeout=1800,capture=True)
        if '"inserted": 0' not in repeat.stdout: raise SystemExit(f'idempotency gate failed: {kind}')
    run(['ssh',args.ssh_target,f'rm -rf {remote_tmp}'],timeout=60)
    run(['ssh',args.ssh_target,'curl -fsS http://127.0.0.1:8001/health && curl -fsS http://127.0.0.1:3000/healthz && curl -fsS http://127.0.0.1:3000/readyz'],timeout=60)
    print(json.dumps({'status':'production-synchronized','backup':remote_backup,'manifests':len(manifests),'records':sum(m['files'][0]['records'] for m in manifests)},ensure_ascii=False))

if __name__=='__main__': main()
