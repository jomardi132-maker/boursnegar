#!/usr/bin/env python3
"""Promote one validated Codal notice-event manifest through safe gates."""
from __future__ import annotations
import argparse, hashlib, json, shlex, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def run(cmd, timeout=1800):
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=timeout)
    if p.returncode: raise RuntimeError(f"command failed: {' '.join(cmd)}\n{p.stderr[-2000:]}")
    return p.stdout
def main():
    p=argparse.ArgumentParser(); p.add_argument('--events-dir',required=True); p.add_argument('--ssh-target',default='boursnegar'); p.add_argument('--remote-dir',required=True); p.add_argument('--report',required=True); a=p.parse_args()
    src=Path(a.events_dir).resolve(); m=json.loads((src/'manifest.json').read_text(encoding='utf-8'))
    if m.get('schema')!='boursnegar-codal-notices-v1' or m.get('source')!='browser/codal.ir' or len(m.get('files',[]))!=1: raise SystemExit('refusing: invalid notice manifest')
    item=m['files'][0]; data=src/item['path']
    if not data.is_file() or hashlib.sha256(data.read_bytes()).hexdigest()!=item.get('sha256'): raise SystemExit('refusing: manifest checksum mismatch')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); backup=f'/var/backups/boursnegar/{stamp}-events-before.dump'
    out=Path(a.report); out.parent.mkdir(parents=True,exist_ok=True)
    stage='validate-manifest'
    def failure(exc):
        report={'schema':'boursnegar-notice-promotion-v1','status':'failure','stage':stage,
                'error':str(exc),'backup':backup,'manifest':str(src/'manifest.json'),
                'finished_at':datetime.now(timezone.utc).isoformat()}
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'status':'failure','stage':stage,'report':str(out)},ensure_ascii=False))
        return 1
    q=lambda s: shlex.quote(s)
    try:
        ssh_opts=['-o','ConnectTimeout=15','-o','ServerAliveInterval=10','-o','ServerAliveCountMax=3']
        stage='backup-and-remote-staging'; run(['ssh',*ssh_opts,a.ssh_target,'bash','-lc',q(f'install -d -m 700 /var/backups/boursnegar && runuser -u postgres -- pg_dump -Fc -d boursnegar_db > {q(backup)} && install -d -m 0750 {q(a.remote_dir)}')],300)
        stage='copy-artifact'; run(['scp',*ssh_opts,str(data),f'{a.ssh_target}:{a.remote_dir}/{item["path"]}'],120); run(['scp',*ssh_opts,str(src/'manifest.json'),f'{a.ssh_target}:{a.remote_dir}/manifest.json'],120)
        cmd=f'cd /var/www/boursnegar-data-current && PYTHONPATH=. /var/www/boursnegar-runtimes/data-venv/bin/python3 scripts/codalpy_remote_import.py --manifest {q(a.remote_dir+"/manifest.json")} --symbol "*" --batch-size 500'
        stage='first-import'; first=run(['ssh',*ssh_opts,a.ssh_target,'bash','-lc',q(cmd)],300)
        stage='idempotent-replay'; replay=run(['ssh',*ssh_opts,a.ssh_target,'bash','-lc',q(cmd)],300)
        stage='snapshot-refresh'; refresh=run(['ssh',*ssh_opts,a.ssh_target,'bash','-lc',q('systemctl start --wait boursnegar-snapshot-refresh.service')],300)
        stage='health-ready'; health=run(['ssh',*ssh_opts,a.ssh_target,'curl','-fsS','http://127.0.0.1:8001/healthz'],30); ready=run(['ssh',*ssh_opts,a.ssh_target,'curl','-fsS','http://127.0.0.1:8001/readyz'],30)
        if '"inserted": 0' not in replay: raise RuntimeError('idempotency gate failed')
    except Exception as exc:
        raise SystemExit(failure(exc))
    report={'schema':'boursnegar-notice-promotion-v1','status':'success','backup':backup,'manifest':a.remote_dir+'/manifest.json','first_import':first,'idempotent_replay':replay,'refresh':refresh,'health':health,'ready':ready}
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps({'status':'success','report':str(out),'backup':backup},ensure_ascii=False))
if __name__=='__main__': main()
