#!/usr/bin/env python3
"""Local-only Codalpy fetcher. It produces portable JSONL artifacts; no DB access."""
from __future__ import annotations
import argparse, hashlib, json, signal, time
from pathlib import Path
from datetime import datetime, timezone
from codalpy import Codal
from app.ingestion.codalpy_pipeline import SOURCE, STATEMENTS, current_jalali, ranges, standardize, _call_with_retry

STOP = False
def stop(*_):
    global STOP
    STOP = True
signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--symbol', action='append', required=True)
    p.add_argument('--out', default='artifacts/codalpy')
    p.add_argument('--checkpoint', default='artifacts/codalpy/checkpoint.json')
    p.add_argument('--today', default=None)
    p.add_argument('--retries', type=int, default=3)
    p.add_argument('--rate-limit', type=float, default=2.5)
    args = p.parse_args()
    root, cp_path = Path(args.out), Path(args.checkpoint)
    root.mkdir(parents=True, exist_ok=True); cp_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = json.loads(cp_path.read_text()) if cp_path.exists() else {'completed': {}, 'failures': []}
    manifest = {'schema': 'boursnegar-codalpy-jsonl-v1', 'source': SOURCE, 'generated_at': datetime.now(timezone.utc).isoformat(), 'files': []}
    today = args.today or current_jalali()
    for symbol in args.symbol:
        for start, end in ranges(today):
            for output_type in STATEMENTS:
                key = f'{symbol}|{start}|{end}|{output_type}'
                if checkpoint['completed'].get(key): continue
                if STOP: break
                path = root / f'{symbol.replace("/", "_")}-{start.replace("/", "")}-{end.replace("/", "")}-{output_type}.jsonl'
                try:
                    values = _call_with_retry(getattr(Codal(symbol, start, end), output_type), retries=args.retries)
                    records = standardize(values, output_type)
                    with path.open('w', encoding='utf-8') as f:
                        for record in records:
                            record.update({'symbol': symbol, 'from_jalali': start, 'to_jalali': end, 'retrieved_at': datetime.now(timezone.utc).isoformat()})
                            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + '\n')
                    checkpoint['completed'][key] = {'file': path.name, 'records': len(records), 'sha256': digest(path)}
                    cp_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding='utf-8')
                    manifest['files'].append({'path': str(path), **checkpoint['completed'][key], 'source': SOURCE, 'symbol': symbol, 'from_jalali': start, 'to_jalali': end, 'output_type': output_type})
                    time.sleep(args.rate_limit)
                except Exception as exc:
                    checkpoint['failures'].append({'key': key, 'error': str(exc)[:1000]})
                    cp_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding='utf-8')
            if STOP: break
        if STOP: break
    manifest_path = root / 'manifest.json'
    manifest['checkpoint'] = str(cp_path); manifest['files'] = [v | {'path': v['file']} for v in checkpoint['completed'].values()]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'source': SOURCE, 'files': len(manifest['files']), 'failures': len(checkpoint['failures']), 'checkpoint': str(cp_path), 'manifest': str(manifest_path)}, ensure_ascii=False))
if __name__ == '__main__': main()
