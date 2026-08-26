#!/usr/bin/env python3
"""Evidence-gated Local -> Production synchronization orchestrator.

Default mode is read-only planning. Network fetching and Production writes are
separate explicit gates. Existing proven pipelines are reused; no fabricated
facts or unresolved candidates are ever exported.
"""
from __future__ import annotations
import argparse, hashlib, json, shlex, sqlite3, subprocess, sys
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

def aggregate_manifests(run_root, out, kind):
    out.mkdir(parents=True, exist_ok=True); records=[]; errors=[]
    for source in sorted(run_root.rglob(f'{kind}/*.jsonl')):
        if source.parent.parent.name == 'aggregate':
            continue
        for number, line in enumerate(source.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
            if not line.strip(): continue
            try: row=json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f'{source}:{number}: invalid JSON: {exc}'); continue
            required=('symbol','from_jalali','to_jalali','output_type','payload','source','retrieved_at')
            missing=[key for key in required if not row.get(key)]
            if missing or not isinstance(row.get('payload'), dict):
                errors.append(f'{source}:{number}: invalid record fields={missing or ["payload"]}'); continue
            if row.get('source') not in ('codal.ir','browser/codal.ir'):
                errors.append(f'{source}:{number}: untrusted source={row.get("source")}'); continue
            records.append(row)
    if errors:
        raise SystemExit(f'{kind} validation failed: {len(errors)} invalid records')
    target=out/f'{kind}.jsonl'
    target.write_text(''.join(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n' for row in records),encoding='utf-8')
    manifest={'schema':'boursnegar-codalpy-jsonl-v1','source':'codal.ir' if kind == 'codalpy' else 'browser/codal.ir','generated_at':datetime.now(timezone.utc).isoformat(),
              'files':[{'path':target.name,'records':len(records),'sha256':sha256(target)}],'errors':errors}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest

def aggregate_events(run_root, out):
    out.mkdir(parents=True, exist_ok=True); records=[]
    for source in sorted(run_root.rglob('events/notice-events.jsonl')):
        if source.parent.parent.name == 'aggregate':
            continue
        for line in source.read_text(encoding='utf-8', errors='replace').splitlines():
            if not line.strip(): continue
            row=json.loads(line)
            if not row.get('symbol') or not row.get('tracing_no') or not row.get('source'):
                raise SystemExit(f'event validation failed: {source}')
            records.append(row)
    target=out/'events.jsonl'; target.write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in records),encoding='utf-8')
    manifest={'schema':'boursnegar-codal-notices-v1','source':'browser/codal.ir','generated_at':datetime.now(timezone.utc).isoformat(),
              'files':[{'path':target.name,'records':len(records),'sha256':sha256(target)}],'errors':[]}
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
    args=p.parse_args(); db=Path(args.db).resolve(); run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); run_root=Path(args.run_root).resolve()/run_id
    remote=server_symbols(args.ssh_target)
    local_status={symbol: status for symbol,status in sqlite3.connect(db).execute('SELECT symbol,status FROM symbols')}
    selected=[r['symbol'] for r in remote if r.get('status')!='complete' and local_status.get(r['symbol'])!='complete'][:args.limit]
    plan={'run_id':run_id,'server_symbols':len(remote),'selected_symbols':selected,'apply':args.apply,'allow_download':args.allow_download}
    print(json.dumps({'plan':plan},ensure_ascii=False,indent=2))
    if not args.apply:
        print(json.dumps({'status':'dry-run','next':'add --apply; add --allow-download to fetch missing Local data'},ensure_ascii=False)); return
    if args.allow_download is False and not args.skip_local:
        raise SystemExit('Local completion may fetch data; pass --allow-download explicitly')
    if not args.skip_local:
        for symbol in selected:
            target=symbol_run_root(Path(args.run_root).resolve(), symbol)/symbol
            if target.parent == Path(args.run_root).resolve():
                target=run_root/symbol
            cmd=[PYTHON,'data-service/scripts/daily_local_ingestion.py','--symbol',symbol,'--from-jalali',args.from_jalali,'--to-jalali',args.to_jalali,
                 '--out',str(target),'--local-db',str(db),'--codalpy-first','--download-documents','--professional-documents','--defer-pdf']
            run(cmd,timeout=1800)
        run([PYTHON,'data-service/scripts/recalculate_local_coverage.py','--db',str(db)])
    # Ensure Codalpy-first results enter the same local DB before export.
    for codal_dir in run_root.glob('*/codalpy'):
        if (codal_dir/'manifest.json').exists():
            run([PYTHON,'data-service/scripts/build_local_codal_db.py','--db',str(db),'--artifact',str(codal_dir)])
    manifests=[]
    aggregate_root=Path(args.run_root).resolve()
    for kind in ('codalpy','normalized'):
        manifest=aggregate_manifests(aggregate_root,run_root/'aggregate'/kind,kind)
        if manifest['files'][0]['records']: manifests.append(manifest)
    events_manifest=aggregate_events(aggregate_root,run_root/'aggregate/events')
    if events_manifest['files'][0]['records']: manifests.append(events_manifest)
    if not manifests:
        print(json.dumps({'status':'no-new-normalized-records','run_root':str(run_root)},ensure_ascii=False)); return
    if args.skip_production:
        print(json.dumps({'status':'local-complete-production-skipped','manifests':[str(run_root/'aggregate'/m['source'].split('.')[0]+'/manifest.json') for m in manifests]},ensure_ascii=False)); return
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); remote_backup=f'/var/backups/boursnegar/{stamp}-auto-local-to-production.dump'
    run(['ssh',args.ssh_target,f"sudo -u postgres pg_dump -Fc -d boursnegar_db | sudo tee {shlex.quote(remote_backup)} >/dev/null"],timeout=900)
    for manifest in manifests:
        kind='codalpy' if manifest['source']=='codal.ir' else ('events' if manifest['schema']=='boursnegar-codal-notices-v1' else 'normalized')
        run(['scp',str(run_root/'aggregate'/kind/f'{kind}.jsonl'),str(run_root/'aggregate'/kind/'manifest.json'),f'{args.ssh_target}:/tmp/{kind}.jsonl'],timeout=300)
    remote_dir=f'/var/www/boursnegar-data-current/staging/auto-sync/{run_id}'
    run(['ssh',args.ssh_target,f'sudo install -d -m 0750 {remote_dir}'],timeout=60)
    for manifest in manifests:
        kind='codalpy' if manifest['source']=='codal.ir' else ('events' if manifest['schema']=='boursnegar-codal-notices-v1' else 'normalized')
        run(['ssh',args.ssh_target,f'sudo install -m 0640 /tmp/{kind}.jsonl {remote_dir}/{kind}.jsonl; sudo install -m 0640 /tmp/manifest.json {remote_dir}/{kind}-manifest.json; sudo rm -f /tmp/{kind}.jsonl /tmp/manifest.json'],timeout=60)
        remote_manifest=f'{remote_dir}/{kind}-manifest.json'
        run(['ssh',args.ssh_target,f'cd /var/www/boursnegar-data-current && sudo env PYTHONPATH=. venv/bin/python scripts/codalpy_remote_import.py --manifest {remote_manifest} --symbol "*" --batch-size 500'],timeout=1800)
        repeat=run(['ssh',args.ssh_target,f'cd /var/www/boursnegar-data-current && sudo env PYTHONPATH=. venv/bin/python scripts/codalpy_remote_import.py --manifest {remote_manifest} --symbol "*" --batch-size 500'],timeout=1800,capture=True)
        if '"inserted": 0' not in repeat.stdout: raise SystemExit(f'idempotency gate failed: {kind}')
    run(['ssh',args.ssh_target,'curl -fsS http://127.0.0.1:8001/health && curl -fsS http://127.0.0.1:3000/healthz && curl -fsS http://127.0.0.1:3000/readyz'],timeout=60)
    print(json.dumps({'status':'production-synchronized','backup':remote_backup,'manifests':len(manifests),'records':sum(m['files'][0]['records'] for m in manifests)},ensure_ascii=False))

if __name__=='__main__': main()
