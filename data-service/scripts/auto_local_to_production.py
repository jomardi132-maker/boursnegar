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
DEFAULT_RUN_ROOT = ROOT / 'data-service' / 'artifacts' / 'auto-sync'
DEFAULT_ARTIFACT_ROOT = ROOT / 'data-service' / 'artifacts'
DEFAULT_LOCAL_BACKUP_ROOT = DEFAULT_ARTIFACT_ROOT / 'backups'

def run(cmd, *, cwd=ROOT, timeout=600, capture=False):
    rendered = ' '.join(map(str, cmd))
    if len(rendered) > 1200:
        rendered = rendered[:1200] + f' ... [{len(cmd)} arguments]'
    print(json.dumps({'step': rendered}, ensure_ascii=False), flush=True)
    return subprocess.run(cmd, cwd=cwd, check=True, timeout=timeout,
                          text=True, capture_output=capture, encoding='utf-8', errors='replace')

def stream_remote_backup(target: str, destination: Path):
    """Keep the pre-import rollback dump off a full Production filesystem."""
    print(json.dumps({'step': f'ssh {target} pg_dump -> {destination}'}, ensure_ascii=False), flush=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open('wb') as handle:
            subprocess.run(
                ['ssh', target, 'sudo -u postgres pg_dump -Fc -d boursnegar_db'],
                cwd=ROOT, check=True, timeout=900, stdout=handle,
            )
    except Exception:
        destination.unlink(missing_ok=True)
        raise

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def write_report(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

def validate_local_backup(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size <= 0:
        raise SystemExit(f'backup validation failed: {path}')
    run(['pg_restore', '-l', str(path)], timeout=300, capture=True)
    return {'path': str(path), 'size_bytes': path.stat().st_size, 'sha256': sha256(path), 'pg_restore_list': 'PASS'}

def validate_remote_backup(target: str, path: str) -> dict:
    check = run(['ssh', target,
        f"sudo test -s {shlex.quote(path)} && sudo pg_restore -l {shlex.quote(path)} >/dev/null && "
        f"sudo stat -c '%s' {shlex.quote(path)} && sudo sha256sum {shlex.quote(path)}"], timeout=300, capture=True)
    lines=[line.strip() for line in check.stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        raise SystemExit('backup validation output incomplete')
    return {'path': path, 'size_bytes': int(lines[-2]), 'sha256': lines[-1].split()[0], 'pg_restore_list': 'PASS'}

def parse_import_result(output: str) -> dict:
    lines=[line for line in output.splitlines() if line.strip().startswith('{')]
    if not lines:
        raise SystemExit('importer did not return a JSON summary')
    result=json.loads(lines[-1])
    if result.get('validation_errors'):
        raise SystemExit(f"import validation failed: {result['validation_errors'][:3]}")
    return result

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

def attempted_symbols(artifact_root: Path) -> set[str]:
    """Return symbols with a checkpointed attempt; explicit queues may retry them."""
    attempted = set()
    if not artifact_root.exists():
        return attempted
    for run in artifact_root.iterdir():
        if not run.is_dir() or run.name == 'aggregate':
            continue
        attempted.update(child.name for child in run.iterdir() if child.is_dir() and child.name not in {'aggregate'})
    return attempted

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

def validate_artifact_directory(directory: Path) -> list[str]:
    """Validate the files declared by one local manifest before importing it."""
    errors: list[str] = []
    manifest_path = directory / 'manifest.json'
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception as exc:
        return [f'{manifest_path}: invalid manifest: {exc}']
    for item in manifest.get('files') or []:
        name = item.get('path') or item.get('file')
        if not name:
            errors.append(f'{manifest_path}: declared file has no path')
            continue
        path = directory / str(name)
        if not path.is_file():
            errors.append(f'{path}: missing')
            continue
        expected = str(item.get('sha256') or '')
        if expected and sha256(path) != expected:
            errors.append(f'{path}: checksum mismatch')
            continue
        if path.suffix == '.jsonl':
            with path.open(encoding='utf-8', errors='replace') as handle:
                for number, line in enumerate(handle, 1):
                    if not line.strip():
                        continue
                    try:
                        json.loads(line)
                    except json.JSONDecodeError as exc:
                        errors.append(f'{path}:{number}: invalid JSON: {exc}')
                        break
    return errors

def backup_local_sqlite(db: Path, backup_root: Path = DEFAULT_LOCAL_BACKUP_ROOT) -> dict:
    """Create and integrity-check a consistent SQLite backup before mass import."""
    backup_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    destination = backup_root / f'{stamp}-local-ingestion.sqlite3'
    source_connection = sqlite3.connect(db)
    backup_connection = sqlite3.connect(destination)
    try:
        source_connection.backup(backup_connection)
        result = backup_connection.execute('PRAGMA integrity_check').fetchone()
    finally:
        backup_connection.close()
        source_connection.close()
    if not result or result[0] != 'ok':
        destination.unlink(missing_ok=True)
        raise SystemExit('local SQLite backup integrity check failed')
    return {'path': str(destination), 'size_bytes': destination.stat().st_size,
            'sha256': sha256(destination), 'integrity_check': 'ok'}

def pending_local_artifacts(db: Path, artifact_root: Path) -> tuple[list[Path], list[dict]]:
    already_imported = imported_artifact_paths(db)
    artifact_dirs = [p for p in existing_local_artifacts(artifact_root) if str(p.resolve()) not in already_imported]
    valid: list[Path] = []
    failures: list[dict] = []
    for directory in artifact_dirs:
        errors = validate_artifact_directory(directory)
        if errors:
            failures.append({'path': str(directory), 'errors': errors[:3]})
        else:
            valid.append(directory)
    return valid, failures

def import_existing_local_artifacts(db: Path, artifact_root: Path) -> dict:
    valid, failures = pending_local_artifacts(db, artifact_root)
    backup = None
    if valid:
        backup = backup_local_sqlite(db)
        # Import in bounded groups to avoid command-line limits while retaining
        # one ledger entry per artifact directory.
        for start in range(0, len(valid), 100):
            cmd = [PYTHON, 'data-service/scripts/build_local_codal_db.py', '--db', str(db)]
            for directory in valid[start:start + 100]:
                cmd.extend(['--artifact', str(directory)])
            run(cmd, timeout=1800)
    return {'imported_dirs': len(valid), 'invalid_dirs': failures, 'backup': backup}

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

def symbol_failure_exit_code(symbol_failures: list[dict]) -> int:
    """Keep successful imports usable, but make partial local runs fail visibly."""
    return 2 if symbol_failures else 0

def is_derived_symbol(symbol: str) -> bool:
    return base_symbol(symbol) != symbol

def selection_priority(symbol: str, info: dict[str, object], remote_status: str) -> tuple[int, int, int, str]:
    status_rank = {'comparable': 0, 'incomplete': 1}.get(str(info.get('status') or remote_status), 2)
    derived_rank = 1 if is_derived_symbol(symbol) else 0
    periods = int(info.get('period_count') or 0)
    facts = int(info.get('standard_count') or 0)
    notices = int(info.get('notice_count') or 0)
    return (status_rank, derived_rank, -periods, -facts - notices, symbol)

def is_fund_row(row: dict[str, object]) -> bool:
    """Keep ETF/fund instruments out of the company-statement recovery queue."""
    text = " ".join(str(row.get(key) or "") for key in (
        "market_category", "industry", "industry_title", "company_industry"
    )).replace("\u200c", " ")
    return "صندوق سرمایه گذاری قابل معامله" in " ".join(text.split())

def select_symbols(remote: list[dict[str, object]], local_rows: dict[str, dict[str, object]], limit: int, attempted: set[str] | None = None) -> list[str]:
    attempted = attempted or set()
    candidates = []
    for row in remote:
        symbol = str(row.get('symbol') or '')
        if not symbol:
            continue
        if is_fund_row(row):
            continue
        # Suffix instruments have separate ISINs and often no company-level
        # Codal statements; retry them only through an explicit symbol file.
        if is_derived_symbol(symbol):
            continue
        if symbol in attempted:
            continue
        info = local_rows.get(symbol, {})
        local_status = str(info.get('status') or '')
        remote_status = str(row.get('status') or '')
        if local_status == 'complete' or remote_status == 'complete':
            continue
        candidates.append((selection_priority(symbol, info, remote_status), symbol))
    return [symbol for _, symbol in sorted(candidates)[:limit]]

def select_explicit_symbols(path: Path, remote: list[dict[str, object]]) -> list[str]:
    requested = [line.strip() for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    active = {str(row['symbol']) for row in remote}
    unknown = [symbol for symbol in requested if symbol not in active]
    if unknown:
        raise SystemExit(f'Explicit symbols are not active on Production: {", ".join(unknown)}')
    return list(dict.fromkeys(requested))

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
        (p for p in run_root.iterdir() if p.is_dir() and (p / symbol).is_dir()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else run_root

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',default='data-service/artifacts/local-ingestion.sqlite3'); p.add_argument('--ssh-target',default='boursnegar')
    p.add_argument('--from-jalali',default='1404/01/01'); p.add_argument('--to-jalali',required=True)
    p.add_argument('--limit',type=int,default=10); p.add_argument('--run-root',default=str(DEFAULT_RUN_ROOT))
    p.add_argument('--preimport-root', default=str(DEFAULT_ARTIFACT_ROOT),
                   help='Root containing previously downloaded local artifacts')
    p.add_argument('--symbols-file', help='newline-delimited active symbols to process instead of local-priority selection')
    p.add_argument('--apply',action='store_true'); p.add_argument('--allow-download',action='store_true')
    p.add_argument('--skip-local',action='store_true'); p.add_argument('--skip-production',action='store_true')
    p.add_argument('--skip-preimport', action='store_true', help='Skip importing already downloaded local artifacts before planning')
    p.add_argument('--backup-path', help='Write the pre-import rollback dump to this local path instead of Production backups')
    p.add_argument('--report', help='Write a structured end-to-end execution report')
    args=p.parse_args(); db=Path(args.db).resolve(); run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); run_root=Path(args.run_root).resolve()/run_id
    report_path=Path(args.report).resolve() if args.report else run_root/'execution-report.json'
    run_base = Path(args.run_root).resolve()
    run_base.mkdir(parents=True, exist_ok=True)
    preimport_root = Path(args.preimport_root).resolve()
    pending_dirs, pending_invalid = pending_local_artifacts(db, preimport_root) if preimport_root.exists() else ([], [])
    preimport_result = {'imported_dirs': 0, 'invalid_dirs': pending_invalid, 'backup': None}
    if args.apply and not args.skip_preimport and preimport_root.exists():
        preimport_result = import_existing_local_artifacts(db, preimport_root)
        if preimport_result['imported_dirs']:
            run([PYTHON, 'data-service/scripts/recalculate_local_coverage.py', '--db', str(db)], timeout=300)
    remote=server_symbols(args.ssh_target)
    local_rows=local_symbol_rows(db)
    attempted = attempted_symbols(run_base)
    selected=select_explicit_symbols(Path(args.symbols_file).resolve(), remote) if args.symbols_file else select_symbols(remote, local_rows, args.limit, attempted)
    plan={'run_id':run_id,'server_symbols':len(remote),'selected_symbols':selected,'attempted_symbols':len(attempted),'apply':args.apply,'allow_download':args.allow_download,
          'preimport_root':str(preimport_root),'preimport_pending_dirs':0 if args.skip_preimport else len(pending_dirs),
          'preimport_invalid_dirs':[] if args.skip_preimport else pending_invalid,
          'preimported_artifact_dirs':preimport_result['imported_dirs'],'local_backup':preimport_result['backup']}
    execution={'schema':'boursnegar-local-to-production-execution-v1','started_at':datetime.now(timezone.utc).isoformat(),'plan':plan,'report':str(report_path)}
    print(json.dumps({'plan':plan},ensure_ascii=False,indent=2))
    if not args.apply:
        execution.update({'finished_at':datetime.now(timezone.utc).isoformat(),'status':'dry-run'})
        write_report(report_path,execution)
        print(json.dumps({'status':'dry-run','report':str(report_path),'next':'add --apply; add --allow-download to fetch missing Local data'},ensure_ascii=False)); return
    if args.allow_download is False and not args.skip_local:
        raise SystemExit('Local completion may fetch data; pass --allow-download explicitly')
    symbol_failures=[]
    if not args.skip_local:
        aggregation_roots=[]
        for symbol in selected:
            target=symbol_run_root(run_base, symbol)/symbol
            if target.parent == run_base:
                target=run_root/symbol
            aggregation_roots.append(target)
            cmd=[PYTHON,'data-service/scripts/daily_local_ingestion.py','--symbol',symbol,'--from-jalali',args.from_jalali,'--to-jalali',args.to_jalali,
                 '--out',str(target),'--local-db',str(db),'--codalpy-first','--download-documents','--professional-documents','--defer-pdf']
            try:
                run(cmd,timeout=1800)
            except subprocess.CalledProcessError as exc:
                symbol_failures.append({'symbol': symbol, 'error': f'exit={exc.returncode}'})
                print(json.dumps({'symbol_failure': symbol, 'error': f'exit={exc.returncode}'}, ensure_ascii=False), flush=True)
            except subprocess.TimeoutExpired:
                symbol_failures.append({'symbol': symbol, 'error': 'timeout'})
                print(json.dumps({'symbol_failure': symbol, 'error': 'timeout'}, ensure_ascii=False), flush=True)
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
        status = {'status':'no-new-normalized-records','run_root':str(run_root),'symbol_failures':symbol_failures}
        execution.update(status); execution['finished_at']=datetime.now(timezone.utc).isoformat(); write_report(report_path,execution)
        print(json.dumps(status,ensure_ascii=False))
        if symbol_failures:
            raise SystemExit(symbol_failure_exit_code(symbol_failures))
        return
    if args.skip_production:
        status = {'status':'local-complete-production-skipped','manifests':[str(run_root/'aggregate'/manifest_kind(m)/'manifest.json') for m in manifests],'symbol_failures':symbol_failures}
        execution.update(status); execution['finished_at']=datetime.now(timezone.utc).isoformat(); write_report(report_path,execution)
        print(json.dumps(status,ensure_ascii=False))
        if symbol_failures:
            raise SystemExit(symbol_failure_exit_code(symbol_failures))
        return
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    if args.backup_path:
        backup_path=Path(args.backup_path).expanduser().resolve()
        stream_remote_backup(args.ssh_target, backup_path)
        remote_backup=str(backup_path)
        backup_evidence=validate_local_backup(backup_path)
    else:
        remote_backup=f'/var/backups/boursnegar/{stamp}-auto-local-to-production.dump'
        run(['ssh',args.ssh_target,f"sudo -u postgres pg_dump -Fc -d boursnegar_db | sudo tee {shlex.quote(remote_backup)} >/dev/null"],timeout=900)
        backup_evidence=validate_remote_backup(args.ssh_target,remote_backup)
    remote_tmp=f'/tmp/boursnegar-auto-sync-{run_id}'
    run(['ssh',args.ssh_target,f'install -d -m 0700 {remote_tmp}'],timeout=60)
    import_results=[]
    for manifest in manifests:
        kind=manifest_kind(manifest)
        run(['scp',str(run_root/'aggregate'/kind/f'{kind}.jsonl'),f'{args.ssh_target}:{remote_tmp}/{kind}.jsonl'],timeout=300)
        run(['scp',str(run_root/'aggregate'/kind/'manifest.json'),f'{args.ssh_target}:{remote_tmp}/{kind}-manifest.json'],timeout=300)
    remote_dir=f'/var/www/boursnegar-data-current/staging/auto-sync/{run_id}'
    run(['ssh',args.ssh_target,f'sudo install -d -m 0750 {remote_dir}'],timeout=60)
    for manifest in manifests:
        kind=manifest_kind(manifest)
        # /tmp and the data release share the Production filesystem; move avoids
        # needing enough free space for a second full JSONL copy.
        run(['ssh',args.ssh_target,f'sudo mv {remote_tmp}/{kind}.jsonl {remote_dir}/{kind}.jsonl; sudo mv {remote_tmp}/{kind}-manifest.json {remote_dir}/{kind}-manifest.json; sudo chmod 0640 {remote_dir}/{kind}.jsonl {remote_dir}/{kind}-manifest.json'],timeout=60)
        remote_manifest=f'{remote_dir}/{kind}-manifest.json'
        first=run(['ssh',args.ssh_target,f'cd /var/www/boursnegar-data-current && sudo env PYTHONPATH=. /var/www/boursnegar-runtimes/data-venv/bin/python3 scripts/codalpy_remote_import.py --manifest {remote_manifest} --symbol "*" --batch-size 500'],timeout=1800,capture=True)
        repeat=run(['ssh',args.ssh_target,f'cd /var/www/boursnegar-data-current && sudo env PYTHONPATH=. /var/www/boursnegar-runtimes/data-venv/bin/python3 scripts/codalpy_remote_import.py --manifest {remote_manifest} --symbol "*" --batch-size 500'],timeout=1800,capture=True)
        first_result=parse_import_result(first.stdout); repeat_result=parse_import_result(repeat.stdout)
        if repeat_result.get('inserted') != 0: raise SystemExit(f'idempotency gate failed: {kind}')
        import_results.append({'kind':kind,'first':first_result,'replay':repeat_result})
    run(['ssh',args.ssh_target,f'rm -rf {remote_tmp}'],timeout=60)
    run(['ssh',args.ssh_target,'sudo systemctl start --wait boursnegar-snapshot-refresh.service'],timeout=1800)
    health=run(['ssh',args.ssh_target,'curl -fsS http://127.0.0.1:8001/health && curl -fsS http://127.0.0.1:8001/readyz && curl -fsS http://127.0.0.1:3000/healthz && curl -fsS http://127.0.0.1:3000/readyz'],timeout=60,capture=True)
    retention_dry=run(['ssh',args.ssh_target,'sudo /usr/local/sbin/boursnegar-backup-retention'],timeout=300,capture=True)
    retention_apply=run(['ssh',args.ssh_target,'sudo /usr/local/sbin/boursnegar-backup-retention --apply'],timeout=300,capture=True)
    status = {'status':'production-synchronized','backup':backup_evidence,'manifests':len(manifests),'records':sum(m['files'][0]['records'] for m in manifests),'imports':import_results,'snapshot_refresh':'PASS','health':health.stdout.strip(),'retention':{'dry_run':retention_dry.stdout.strip(),'apply':retention_apply.stdout.strip()},'symbol_failures':symbol_failures}
    execution.update(status); execution['finished_at']=datetime.now(timezone.utc).isoformat(); write_report(report_path,execution)
    status['report']=str(report_path)
    print(json.dumps(status,ensure_ascii=False))
    if symbol_failures:
        raise SystemExit(symbol_failure_exit_code(symbol_failures))

if __name__=='__main__': main()
