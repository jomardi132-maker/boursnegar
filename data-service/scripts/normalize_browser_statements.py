#!/usr/bin/env python3
"""Normalize browser-captured Codal financial documents without invented values."""
from __future__ import annotations
import argparse, hashlib, json, sys
import re
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from app.services.codal_excel_parser import parse_financial_statement, extract_period_end_jalali

SOURCE = 'browser/codal.ir'
SCHEMA = 'boursnegar-codalpy-jsonl-v1'

UNIT_PATTERNS = (
    (re.compile(r'میلیارد\s*ری[ااآ]ل'), 'IRR_billion'),
    (re.compile(r'میلیون\s*ری[ااآ]ل'), 'IRR_million'),
    (re.compile(r'هزار\s*ری[ااآ]ل'), 'IRR_thousand'),
    (re.compile(r'ری[ااآ]ل'), 'IRR'),
)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def detect_unit(content: bytes) -> str | None:
    text = content[:2_000_000].decode('utf-8', errors='ignore')
    text = text.replace('ي', 'ی').replace('ك', 'ک')
    for pattern, unit in UNIT_PATTERNS:
        if pattern.search(text):
            return unit
    return None

def statement_metadata(title: str) -> tuple[bool, str]:
    audited = 'حسابرسی شده' in title and 'حسابرسی نشده' not in title
    scope = 'consolidated' if 'تلفیقی' in title else 'separate'
    return audited, scope

def official_url(value: object, host: str) -> str | None:
    value = str(value or '').strip()
    if not value:
        return None
    if value.startswith('/'):
        return f'https://{host}{value}'
    return value if value.startswith('https://') else None

def output_type(title: str) -> str:
    if 'فعالیت ماهانه' in title or 'عملکرد ماهانه' in title:
        return 'monthly_activity'
    if 'ترازنامه' in title or 'وضعیت مالی' in title:
        return 'balance_sheet'
    return 'income_statement'

def fact_output_type(fact_key: str, title: str) -> str:
    if fact_key in {'total_assets', 'total_liabilities', 'total_equity'}:
        return 'balance_sheet'
    return output_type(title)

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--capture', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--bundle', help='Process one JSONL bundle within the capture root')
    args = p.parse_args()
    root, out = Path(args.capture), Path(args.out); out.mkdir(parents=True, exist_ok=True)
    rows, errors, source_files = [], [], set()
    bundles = [root / args.bundle] if args.bundle else sorted(root.rglob('*.jsonl'))
    for bundle in bundles:
        if not bundle.exists():
            errors.append({'file': str(bundle), 'error': 'bundle_missing'})
            continue
        for line_no, line in enumerate(bundle.read_text(encoding='utf8').splitlines(), 1):
            try: record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append({'file': bundle.name, 'line': line_no, 'error': f'json:{exc}'}); continue
            symbol, letter = record.get('symbol'), record.get('letter') or {}
            if not isinstance(letter, dict) or not letter:
                continue
            tracing, title = str(letter.get('TracingNo') or ''), str(letter.get('Title') or '')
            period = extract_period_end_jalali(title)
            if not symbol or not tracing:
                errors.append({'file': bundle.name, 'line': line_no, 'error': 'symbol_or_tracing_missing'}); continue
            kind = output_type(title)
            for doc in record.get('documents') or []:
                if doc.get('kind') not in ('html', 'excel') or not doc.get('path'): continue
                path = bundle.parent / doc['path']
                if not path.exists(): errors.append({'symbol': symbol, 'tracing_no': tracing, 'file': doc['path'], 'error': 'document_missing'}); continue
                checksum = doc.get('sha256') or sha(path)
                if sha(path) != checksum:
                    errors.append({'symbol': symbol, 'tracing_no': tracing, 'file': doc['path'], 'error': 'checksum_mismatch'}); continue
                source_files.add((str(path), checksum))
                content = path.read_bytes()
                unit = detect_unit(content)
                try: parsed = parse_financial_statement(path.read_bytes())
                except Exception as exc:
                    errors.append({'symbol': symbol, 'tracing_no': tracing, 'file': doc['path'], 'error': f'parse:{exc}'}); continue
                for fact_key in parsed['found_items']:
                    value = parsed['metrics'].get(fact_key)
                    if value is None or not period: continue
                    audited, scope = statement_metadata(title)
                    fact_unit = 'IRR' if fact_key == 'eps_basic' else unit
                    rows.append({'source': SOURCE, 'symbol': symbol, 'from_jalali': record.get('from_jalali'), 'to_jalali': record.get('to_jalali'),
                                 'retrieved_at': record.get('retrieved_at'), 'output_type': fact_output_type(fact_key, title), 'source_action_id': f'{tracing}:{fact_key}:{period}',
                                 'tracing_no': tracing, 'period_end_jalali': period, 'fact_key': fact_key, 'source_label': fact_key,
                                 'value': value, 'raw_value': value, 'unit': fact_unit or 'UNKNOWN',
                                 'payload': {'title': title, 'document': doc['path'], 'document_sha256': checksum,
                                             'letter_code': letter.get('LetterCode'), 'parser_found_items': parsed['found_items'],
                                             'detail_url': official_url(letter.get('Url') or letter.get('URL') or letter.get('DetailUrl'), 'codal.ir'),
                                             'excel_url': official_url(letter.get('ExcelUrl'), 'excel.codal.ir'),
                                             'audited': audited, 'scope': scope}})
    target = out / 'normalized.jsonl'; target.write_text(''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in rows), encoding='utf8')
    manifest = {'schema': SCHEMA, 'source': SOURCE, 'files': [{'path': target.name, 'symbol': '*', 'records': len(rows), 'sha256': sha(target)}],
                'source_documents': [{'path': path, 'sha256': checksum} for path, checksum in sorted(source_files)], 'errors': errors}
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({'records': len(rows), 'source_documents': len(source_files), 'errors': len(errors), 'manifest': str(out / 'manifest.json')}, ensure_ascii=False))

if __name__ == '__main__': main()
