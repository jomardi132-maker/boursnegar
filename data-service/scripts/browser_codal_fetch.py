#!/usr/bin/env python3
"""Fetch Codal disclosures through a local, user-visible Chrome session.

This is deliberately local-only. It launches Chrome with a separate profile,
lets the user complete login/captcha if needed, and uses the page's own
network context. It writes raw response artifacts plus a resumable manifest;
Production credentials and databases are never accessed.
"""
from __future__ import annotations
import argparse, hashlib, json, os, signal, subprocess, time, urllib.parse, urllib.request
from pathlib import Path

STOP = False
def _stop(*_):
    global STOP
    STOP = True

def cleanup_profile_processes(profile: Path):
    target = f'--user-data-dir={profile.resolve()}'.encode()
    for entry in Path('/proc').glob('[0-9]*'):
        try:
            cmdline = (entry / 'cmdline').read_bytes()
            if target not in cmdline or b'/opt/google/chrome/chrome' not in cmdline:
                continue
            os.kill(int(entry.name), signal.SIGTERM)
        except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError):
            pass
    time.sleep(0.5)
    for entry in Path('/proc').glob('[0-9]*'):
        try:
            cmdline = (entry / 'cmdline').read_bytes()
            if target not in cmdline or b'/opt/google/chrome/chrome' not in cmdline:
                continue
            os.kill(int(entry.name), signal.SIGKILL)
        except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError):
            pass

class ChromeCDP:
    def __init__(self, port: int, profile: Path):
        self.port, self.profile, self.proc, self.ws, self.seq = port, profile, None, None, 0
    def start(self):
        import websocket
        self.profile.mkdir(parents=True, exist_ok=True)
        self.proc = subprocess.Popen([
            "google-chrome", f"--remote-debugging-port={self.port}",
            f"--user-data-dir={self.profile}", "--no-first-run", "--no-default-browser-check",
            "--remote-allow-origins=*",
            "https://codal.ir/"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        for _ in range(60):
            try:
                tabs=json.load(urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json", timeout=2))
                tab=next((x for x in tabs if x.get("type")=="page"), None)
                if tab:
                    self.ws=websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=30, http_proxy_host=None, http_proxy_port=None, http_no_proxy=["127.0.0.1","localhost"])
                    self.call("Page.enable")
                    return
            except Exception: time.sleep(0.5)
        raise RuntimeError("Chrome DevTools connection was not available")
    def call(self, method, params=None):
        self.seq += 1; ident=self.seq
        self.ws.send(json.dumps({"id":ident,"method":method,"params":params or {}}))
        while True:
            msg=json.loads(self.ws.recv())
            if msg.get("id")==ident: return msg
    def eval(self, expression):
        result=self.call("Runtime.evaluate", {"expression":expression,"awaitPromise":True,"returnByValue":True})
        if "exceptionDetails" in result.get("result",{}): raise RuntimeError(str(result["result"]["exceptionDetails"]))
        return result["result"]["result"].get("value")
    def navigate(self, url, wait=1.5):
        self.call("Page.navigate", {"url": url})
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                if self.eval("document.readyState") in ("interactive", "complete"):
                    time.sleep(wait)
                    return
            except Exception:
                pass
            time.sleep(0.25)
        raise RuntimeError(f"browser navigation timeout: {url}")

    def allow_downloads(self, directory: Path):
        self.call("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(directory.resolve())})
    def close(self):
        if self.ws: self.ws.close()
        if self.proc and self.proc.poll() is None:
            try:
                os.killpg(self.proc.pid, signal.SIGTERM)
                self.proc.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try: os.killpg(self.proc.pid, signal.SIGKILL)
                except ProcessLookupError: pass
        cleanup_profile_processes(self.profile)

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(); p.add_argument('--symbol',action='append',required=True)
    p.add_argument('--from-jalali',default='1404/01/01'); p.add_argument('--to-jalali',required=True)
    p.add_argument('--out',default='artifacts/browser-codal'); p.add_argument('--port',type=int,default=9222)
    p.add_argument('--profile',default='.chrome-codal-profile'); p.add_argument('--pause-for-login',action='store_true'); p.add_argument('--download-documents',action='store_true'); p.add_argument('--download-all-documents',action='store_true'); p.add_argument('--professional-documents',action='store_true'); p.add_argument('--excel-only',action='store_true'); p.add_argument('--html-only',action='store_true'); p.add_argument('--defer-pdf',action='store_true'); p.add_argument('--download-timeout',type=float,default=8.0)
    args=p.parse_args(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    cp=out/'checkpoint.json'; checkpoint=json.loads(cp.read_text()) if cp.exists() else {'done':{},'errors':[]}
    chrome=ChromeCDP(args.port,Path(args.profile)); chrome.start()
    chrome.allow_downloads(out)
    signal.signal(signal.SIGINT,_stop); signal.signal(signal.SIGTERM,_stop)
    try:
        if args.pause_for_login:
            input('Chrome باز است. ورود/captcha را در همان پنجره انجام دهید، سپس Enter بزنید... ')
        for symbol in args.symbol:
            if STOP: break
            key=f'{symbol}|{args.from_jalali}|{args.to_jalali}'
            if key in checkpoint['done']: continue
            chrome.navigate('https://search.codal.ir/')
            letters=[]
            no_notices=False
            for page in range(1, 21):
                query=urllib.parse.urlencode({'Symbol':symbol,'FromDate':args.from_jalali,'ToDate':args.to_jalali,'PageNumber':page,'PageSize':100})
                # Bound the page-side request as well as the outer subprocess.
                # Without this, a stalled Codal response can keep an awaited
                # Promise alive for an unbounded time inside Chrome.
                expression=(
                    f"(async()=>{{const c=new AbortController();"
                    f"const t=setTimeout(()=>c.abort(),15000);"
                    f"try{{const r=await fetch('/api/search/v2/q?{query}',{{signal:c.signal}});"
                    f"return await r.text()}}finally{{clearTimeout(t)}}}})()"
                )
                raw=chrome.eval(expression)
                try:
                    payload=json.loads(raw)
                except (TypeError,json.JSONDecodeError) as exc:
                    if symbol.endswith('3'):
                        no_notices=True
                        checkpoint['done'][key]={'file':None,'records':0,'status':'NO_NOTICES','sha256':None}
                    else:
                        checkpoint['errors'].append({'symbol':symbol,'page':page,'error':'non_json_response:'+str(exc)[:300]})
                    cp.write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding='utf-8')
                    break
                batch=payload.get('Letters') or []
                letters.extend(batch)
                time.sleep(1.0)
                if len(batch) < 100: break
            path=out/(symbol.replace('/','_')+f'-{args.from_jalali.replace("/","")}-{args.to_jalali.replace("/","")}.jsonl')
            with path.open('w',encoding='utf-8') as f:
                for letter in letters:
                    if STOP: break
                    row={'source':'browser/codal.ir','symbol':symbol,'from_jalali':args.from_jalali,'to_jalali':args.to_jalali,'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'letter':letter}
                    if args.download_documents or args.download_all_documents or args.professional_documents:
                        title=str(letter.get('Title') or '')
                        financial_notice=any(token in title for token in ('صورت', 'مالی', 'فعالیت ماهانه', 'عملکرد ماهانه','ترازنامه','سود','زیان'))
                        if args.professional_documents:
                            document_kinds=() if args.excel_only else (('html', letter.get('Url'), '.html'),)
                            if financial_notice and not args.html_only: document_kinds += (('excel', letter.get('ExcelUrl'), '.xls'),)
                            if letter.get('PdfUrl') and not args.html_only and not args.defer_pdf: document_kinds += (('pdf', letter.get('PdfUrl'), '.pdf'),)
                        elif not args.download_all_documents and not any(token in title for token in ('صورت', 'مالی', 'فعالیت ماهانه', 'عملکرد ماهانه')):
                            f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
                            continue
                        if not args.professional_documents: document_kinds=(('html', letter.get('Url'), '.html'),) if args.html_only else (('html', letter.get('Url'), '.html'), ('excel', letter.get('ExcelUrl'), '.xls'))
                        for kind, url, suffix in document_kinds:
                            if not url: continue
                            if str(url).startswith('/'): url='https://codal.ir'+url
                            safe=str(letter.get('TracingNo') or hashlib.sha1(str(url).encode()).hexdigest()[:16])
                            target=out/f'{symbol}-{safe}-{kind}{suffix}'
                            try:
                                if target.exists() and target.is_file() and target.stat().st_size > 0:
                                    row.setdefault('documents',[]).append({'kind':kind,'path':target.name,'sha256':sha(target),'status':200,'reused':True,'symbol':symbol,'tracing_no':str(letter.get('TracingNo') or ''),'title':title,'letter_code':letter.get('LetterCode'),'source':'browser/codal.ir'})
                                    continue
                                if kind == 'html':
                                    chrome.navigate(url, wait=0.5)
                                    html=chrome.eval("document.documentElement.outerHTML")
                                    if not html: raise RuntimeError('empty HTML document')
                                    target.write_text(html, encoding='utf-8')
                                    row.setdefault('documents',[]).append({'kind':kind,'path':target.name,'sha256':sha(target),'status':200,'symbol':symbol,'tracing_no':str(letter.get('TracingNo') or ''),'title':title,'letter_code':letter.get('LetterCode'),'source':'browser/codal.ir'})
                                else:
                                    before={p.name for p in out.iterdir()}
                                    chrome.navigate(url, wait=0.2)
                                    deadline=time.time()+args.download_timeout
                                    downloaded=None
                                    while time.time()<deadline:
                                        candidates=[p for p in out.iterdir() if p.name not in before and p.is_file() and not p.name.endswith('.crdownload')]
                                        if candidates:
                                            downloaded=max(candidates,key=lambda p:p.stat().st_mtime)
                                            break
                                        time.sleep(0.25)
                                    if not downloaded: raise RuntimeError('download timeout')
                                    content = downloaded.read_bytes()
                                    if suffix == '.xls' and b'<table' not in content.lower() and b'<html' not in content.lower():
                                        raise RuntimeError('downloaded content is not a Codal HTML-Excel document')
                                    target.write_bytes(content)
                                    downloaded.unlink()
                                    row.setdefault('documents',[]).append({'kind':kind,'path':target.name,'sha256':sha(target),'status':200,'symbol':symbol,'tracing_no':str(letter.get('TracingNo') or ''),'title':title,'letter_code':letter.get('LetterCode'),'source':'browser/codal.ir'})
                            except Exception as exc:
                                row.setdefault('document_errors',[]).append({'kind':kind,'url':url,'error':str(exc)})
                    f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
            if not STOP and not any(e.get('symbol')==symbol for e in checkpoint['errors']):
                if not letters:
                    checkpoint['done'][key]={'file':None,'records':0,'status':'NO_NOTICES','sha256':None}
                elif not no_notices:
                    checkpoint['done'][key]={'file':path.name,'records':len(letters),'sha256':sha(path)}
                cp.write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding='utf-8')
    finally:
        chrome.close()
    manifest_files=[]
    for value in checkpoint['done'].values():
        if not value.get('file'):
            continue
        item=dict(value)
        item['path']=item.pop('file')
        item['source']='browser/codal.ir'
        manifest_files.append(item)
    manifest={'schema':'boursnegar-browser-codal-jsonl-v1','source':'browser/codal.ir','files':manifest_files,'checkpoint':str(cp),'errors':checkpoint['errors']}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'source':manifest['source'],'files':len(manifest['files']),'checkpoint':str(cp),'manifest':str(out/'manifest.json')},ensure_ascii=False))
if __name__=='__main__': main()
