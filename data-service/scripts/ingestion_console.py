#!/usr/bin/env python3
"""Local ingestion console for Boursnegar.

This is the operator-facing coordinator. It owns a local SQLite state database,
uses Chrome for Codal, keeps artifacts/checkpoints locally, and invokes the
existing SSH importer. It never opens a Production database connection.
"""
from __future__ import annotations
import argparse, csv, json, queue, shlex, sqlite3, subprocess, threading, time
from datetime import datetime, timezone
from pathlib import Path
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    import tkinter.font as tkfont
except ModuleNotFoundError:
    tk=ttk=messagebox=None

ROOT=Path(__file__).resolve().parents[2]
DEFAULT_DB=ROOT/'artifacts'/'local-ingestion.sqlite3'
SCHEMA='''
CREATE TABLE IF NOT EXISTS symbols(symbol TEXT PRIMARY KEY, industry TEXT, status TEXT NOT NULL DEFAULT 'unknown', last_remote_count INTEGER, last_local_count INTEGER, standard_count INTEGER NOT NULL DEFAULT 0, period_count INTEGER NOT NULL DEFAULT 0, gap_summary TEXT NOT NULL DEFAULT '', last_error TEXT, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS notices(symbol TEXT NOT NULL, tracing_no TEXT NOT NULL, title TEXT, published_at TEXT, local_path TEXT, checksum TEXT, remote_present INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(symbol,tracing_no));
CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT, status TEXT NOT NULL, stage TEXT NOT NULL, summary TEXT);
'''
def current_jalali():
    import jdatetime
    d=jdatetime.date.today()
    return f'{d.year:04d}/{d.month:02d}/{d.day:02d}'
def now(): return datetime.now(timezone.utc).isoformat()
class State:
    def __init__(self,path):
        self.path=Path(path).resolve(); self.db=sqlite3.connect(self.path,check_same_thread=False); self.db.executescript(SCHEMA)
        for column in ('standard_count','period_count'):
            try: self.db.execute(f'ALTER TABLE symbols ADD COLUMN {column} INTEGER NOT NULL DEFAULT 0')
            except sqlite3.OperationalError: pass
        try: self.db.execute("ALTER TABLE symbols ADD COLUMN gap_summary TEXT NOT NULL DEFAULT ''")
        except sqlite3.OperationalError: pass
        self.db.commit()
    def upsert_symbols(self, rows):
        self.db.executemany('INSERT INTO symbols(symbol,industry,status,last_remote_count,standard_count,period_count,updated_at) VALUES(?,?,?,?,?,?,?) ON CONFLICT(symbol) DO UPDATE SET industry=excluded.industry,status=excluded.status,last_remote_count=excluded.last_remote_count,standard_count=excluded.standard_count,period_count=excluded.period_count,updated_at=excluded.updated_at',[(r['symbol'],r.get('industry'),r.get('status','incomplete'),r.get('raw_count',0),r.get('standard_count',0),r.get('period_count',0),now()) for r in rows]); self.db.commit()
    def rows(self): return self.db.execute('SELECT symbol,industry,status,last_local_count,last_remote_count,gap_summary,last_error FROM symbols ORDER BY symbol').fetchall()
    def artifact_rows(self):
        try:
            return self.db.execute('''SELECT f.path,f.role,f.status,f.size_bytes,f.json_records,f.json_errors,
                f.imported_rows,COALESCE(p.status,''),COALESCE(p.inferred_symbol,'')
                FROM artifact_files f LEFT JOIN artifact_parse_results p ON p.path=f.path ORDER BY f.path''').fetchall()
        except sqlite3.OperationalError:
            try:
                return [tuple(row)+('','') for row in self.db.execute('SELECT path,role,status,size_bytes,json_records,json_errors,imported_rows FROM artifact_files ORDER BY path')]
            except sqlite3.OperationalError:
                return []
    def artifact_summary(self):
        try:
            return dict(self.db.execute('SELECT status,COUNT(*) FROM artifact_files GROUP BY status'))
        except sqlite3.OperationalError:
            return {}
    def parse_summary(self):
        try:
            return dict(self.db.execute('SELECT status,COUNT(*) FROM artifact_parse_results GROUP BY status'))
        except sqlite3.OperationalError:
            return {}
    def candidate_summary(self):
        try:
            return dict(self.db.execute('SELECT status,COUNT(*) FROM orphan_fact_candidates GROUP BY status'))
        except sqlite3.OperationalError:
            return {}
    def run(self,stage,fn):
        cur=self.db.execute('INSERT INTO runs(started_at,status,stage) VALUES(?,?,?)',(now(),'RUNNING',stage)); rid=cur.lastrowid; self.db.commit()
        try: result=fn(); self.db.execute('UPDATE runs SET finished_at=?,status=?,summary=? WHERE id=?',(now(),'PASSED',json.dumps(result,ensure_ascii=False),rid)); self.db.commit(); return result
        except Exception as exc: self.db.execute('UPDATE runs SET finished_at=?,status=?,summary=? WHERE id=?',(now(),'FAILED',str(exc),rid)); self.db.commit(); raise
def command(args, log):
    log('RUN '+ ' '.join(map(str,args))); p=subprocess.Popen(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf8',errors='replace')
    for line in p.stdout: log(line.rstrip())
    if p.wait()!=0: raise RuntimeError('command failed')
def discover_remote(target, log):
    sql="""SELECT COALESCE(ind.title_fa,'نامشخص'),sa.symbol,0,
      count(DISTINCT ff.id) FILTER (WHERE ff.quality_status='VALID'),
      count(DISTINCT fp.end_date) FILTER (WHERE ff.quality_status='VALID')
      FROM symbol_aliases sa JOIN instruments i ON i.id=sa.instrument_id JOIN issuers iss ON iss.id=i.issuer_id
      LEFT JOIN industries ind ON ind.id=iss.industry_id LEFT JOIN financial_periods fp ON fp.issuer_id=iss.id
      LEFT JOIN financial_facts ff ON ff.period_id=fp.id
      WHERE sa.valid_to IS NULL AND i.active GROUP BY ind.title_fa,sa.symbol ORDER BY 1,2;"""
    remote_cmd='sudo -u postgres psql -d boursnegar_db -Atc '+shlex.quote(sql)
    out=subprocess.check_output(['ssh',target,remote_cmd],text=True,encoding='utf8')
    rows=[]
    for line in out.splitlines():
        parts=line.split('|')
        if len(parts)>=5:
            raw,standard,period=map(int,parts[2:5]);
            # Keep the operator state aligned with the evidence-based audit tiers:
            # core facts alone are not a complete comparable history.
            status = 'complete' if standard >= 7 and period >= 2 else ('comparable' if period >= 2 else 'incomplete')
            rows.append({'industry':parts[0],'symbol':parts[1],'raw_count':raw,'standard_count':standard,'period_count':period,'status':status})
    return rows
class App:
    def __init__(self,root,state,target):
        self.root=root; self.state=state; self.target=target; self.events=queue.Queue(); families=tkfont.families(root); family=next((x for x in ('Vazirmatn','Noto Sans Arabic','DejaVu Sans') if x in families),'DejaVu Sans'); self.font=tkfont.Font(root,family=family,size=11); self.bold=tkfont.Font(root,family=family,size=11,weight='bold'); style=ttk.Style(root); style.configure('Persian.Treeview',font=self.font,rowheight=30); style.configure('Persian.Treeview.Heading',font=self.bold)
        self.search_var=tk.StringVar(); self.industry_var=tk.StringVar(value='همه صنایع'); self.status_var=tk.StringVar(value='همه وضعیت‌ها'); self.gap_var=tk.StringVar(value='همه کمبودها'); self.summary_var=tk.StringVar(); self.file_search_var=tk.StringVar(); self.file_role_var=tk.StringVar(value='همه انواع'); self.file_status_var=tk.StringVar(value='همه وضعیت‌ها'); self.file_summary_var=tk.StringVar()
        notebook=ttk.Notebook(root); notebook.pack(fill='both',expand=True,padx=8,pady=8); symbols_tab=ttk.Frame(notebook); files_tab=ttk.Frame(notebook); notebook.add(symbols_tab,text='وضعیت نمادها'); notebook.add(files_tab,text='دفترکل فایل‌های محلی')
        filters=ttk.Frame(symbols_tab); filters.pack(fill='x',padx=8,pady=(8,2)); ttk.Label(filters,text='جست‌وجوی نماد:').pack(side='right'); search=ttk.Entry(filters,textvariable=self.search_var,width=18); search.pack(side='right',padx=5); search.bind('<KeyRelease>',lambda _e:self.refresh()); ttk.Label(filters,text='صنعت:').pack(side='right',padx=(8,2)); self.industry_box=ttk.Combobox(filters,textvariable=self.industry_var,state='readonly',width=20); self.industry_box.pack(side='right'); self.industry_box.bind('<<ComboboxSelected>>',lambda _e:self.refresh()); ttk.Label(filters,text='وضعیت:').pack(side='right',padx=(8,2)); self.status_box=ttk.Combobox(filters,textvariable=self.status_var,state='readonly',values=('همه وضعیت‌ها','کامل','قابل‌مقایسه','ناقص'),width=13); self.status_box.pack(side='right'); self.status_box.bind('<<ComboboxSelected>>',lambda _e:self.refresh()); ttk.Label(filters,text='کمبود:').pack(side='right',padx=(8,2)); self.gap_box=ttk.Combobox(filters,textvariable=self.gap_var,state='readonly',width=18); self.gap_box.pack(side='right'); self.gap_box.bind('<<ComboboxSelected>>',lambda _e:self.refresh()); ttk.Label(symbols_tab,textvariable=self.summary_var,anchor='e',font=self.bold).pack(fill='x',padx=8,pady=3)
        self.tree=ttk.Treeview(symbols_tab,columns=('symbol','industry','status','local','remote','gaps','error'),show='headings',style='Persian.Treeview');
        for c,t,w in zip(self.tree['columns'],('نماد','صنعت','وضعیت','محلی','سرور','کمبودها','خطا'),(120,200,120,90,90,280,300)): self.tree.heading(c,text=t,anchor='e'); self.tree.column(c,anchor='e',width=w)
        self.tree.pack(fill='both',expand=True,padx=8,pady=8); bar=ttk.Frame(symbols_tab); bar.pack(fill='x',padx=8,pady=4); ttk.Button(bar,text='خروجی CSV',command=self.export_rows).pack(side='right'); ttk.Label(bar,text='دریافت و ارسال به سرور تا پایان پالایش محلی متوقف است.').pack(side='right',padx=12)
        file_filters=ttk.Frame(files_tab); file_filters.pack(fill='x',padx=8,pady=8); ttk.Label(file_filters,text='جست‌وجوی مسیر:').pack(side='right'); file_search=ttk.Entry(file_filters,textvariable=self.file_search_var,width=36); file_search.pack(side='right',padx=5); file_search.bind('<KeyRelease>',lambda _e:self.refresh_artifacts()); ttk.Label(file_filters,text='نوع:').pack(side='right'); self.file_role_box=ttk.Combobox(file_filters,textvariable=self.file_role_var,state='readonly',width=14); self.file_role_box.pack(side='right',padx=5); self.file_role_box.bind('<<ComboboxSelected>>',lambda _e:self.refresh_artifacts()); ttk.Label(file_filters,text='وضعیت:').pack(side='right'); self.file_status_box=ttk.Combobox(file_filters,textvariable=self.file_status_var,state='readonly',width=14); self.file_status_box.pack(side='right',padx=5); self.file_status_box.bind('<<ComboboxSelected>>',lambda _e:self.refresh_artifacts()); ttk.Button(file_filters,text='بازخوانی دفترکل',command=self.scan_artifacts).pack(side='left'); ttk.Button(file_filters,text='ممیزی Excelهای بی‌مرجع',command=self.audit_orphans).pack(side='left',padx=5)
        ttk.Label(files_tab,textvariable=self.file_summary_var,anchor='e',font=self.bold).pack(fill='x',padx=8,pady=3); self.file_tree=ttk.Treeview(files_tab,columns=('path','role','status','size','records','errors','imported','parse','symbol'),show='headings',style='Persian.Treeview');
        for c,t,w in zip(self.file_tree['columns'],('مسیر','نوع','وضعیت','حجم','رکورد','خطای JSON','واردشده','نتیجه پردازش','نماد مستند'),(440,90,100,90,80,80,80,150,100)): self.file_tree.heading(c,text=t,anchor='e'); self.file_tree.column(c,anchor='e',width=w)
        self.file_tree.pack(fill='both',expand=True,padx=8,pady=8); self.logbox=tk.Text(root,height=8,font=self.font,wrap='word'); self.logbox.tag_configure('rtl',justify='right'); self.logbox.pack(fill='x',expand=False,padx=8,pady=8); self.refresh(); self.refresh_artifacts(); root.after(250,self.drain)
    def log(self,s): self.events.put(('log',s))
    def refresh(self):
        for x in self.tree.get_children(): self.tree.delete(x)
        rows=self.state.rows(); industries=sorted({r[1] or 'نامشخص' for r in rows}); self.industry_box['values']=['همه صنایع']+industries
        gaps=sorted({g for r in rows for g in (r[5] or '').split('، ') if g and g!='بدون کمبود شناخته‌شده'}); self.gap_box['values']=['همه کمبودها']+gaps
        query=self.search_var.get().strip().casefold(); selected=self.industry_var.get(); selected_status=self.status_var.get(); selected_gap=self.gap_var.get(); visible=[]
        for row in rows:
            if query and query not in (row[0] or '').casefold(): continue
            if selected!='همه صنایع' and (row[1] or 'نامشخص')!=selected: continue
            if selected_status!='همه وضعیت‌ها' and {'کامل':'complete','قابل‌مقایسه':'comparable','ناقص':'incomplete'}.get(selected_status)!=row[2]: continue
            if selected_gap!='همه کمبودها' and selected_gap not in (row[5] or ''): continue
            visible.append(row)
        labels={'complete':'کامل','comparable':'قابل‌مقایسه','incomplete':'ناقص','unknown':'نامشخص'}
        for row in visible:
            values=list(row); values[2]=labels.get(values[2],values[2]); self.tree.insert('', 'end', values=values)
        counts={key:sum(1 for r in rows if r[2]==key) for key in ('complete','comparable','incomplete')}; total=len(rows); pct=(counts['complete']*100/total) if total else 0
        self.summary_var.set(f'کل: {total} | کامل: {counts["complete"]} | قابل‌مقایسه: {counts["comparable"]} | ناقص: {counts["incomplete"]} | تکمیل کامل: {pct:.1f}% | نمایش: {len(visible)}')
    def refresh_artifacts(self):
        for item in self.file_tree.get_children(): self.file_tree.delete(item)
        rows=self.state.artifact_rows(); roles=sorted({r[1] for r in rows}); statuses=sorted({r[2] for r in rows}); self.file_role_box['values']=['همه انواع']+roles; self.file_status_box['values']=['همه وضعیت‌ها']+statuses
        query=self.file_search_var.get().strip().casefold(); selected_role=self.file_role_var.get(); selected_status=self.file_status_var.get(); visible=[]
        for row in rows:
            if query and query not in row[0].casefold(): continue
            if selected_role!='همه انواع' and row[1]!=selected_role: continue
            if selected_status!='همه وضعیت‌ها' and row[2]!=selected_status: continue
            visible.append(row)
        for row in visible[:5000]: self.file_tree.insert('', 'end', values=row)
        counts=self.state.artifact_summary(); parsed=self.state.parse_summary(); candidates=self.state.candidate_summary(); self.file_summary_var.set(f'کل فایل: {len(rows)} | بی‌مرجع: {counts.get("DISCOVERED",0)} | Excel دارای fact: {parsed.get("PARSED_WITH_FACTS",0)} | آماده اتصال: {candidates.get("READY_FOR_LINKAGE",0)} | تکراری: {candidates.get("DUPLICATE_EXISTING",0)} | تعارض: {candidates.get("NEEDS_DISAMBIGUATION",0)} | خطای parse: {parsed.get("PARSE_FAILED",0)} | نمایش: {min(len(visible),5000)}')
    def scan_artifacts(self):
        def work():
            cmd=['python3',str(ROOT/'data-service/scripts/reconcile_local_artifacts.py'),'--db',str(self.state.path)]
            for folder in ('all-symbols-v16','all-symbols-v17','all-symbols-v18'): cmd += ['--root',str(ROOT/'artifacts'/folder)]
            try: command(cmd,self.log); self.events.put(('artifacts',None))
            except Exception as exc: self.log('LEDGER ERROR '+str(exc))
        threading.Thread(target=work,daemon=True).start()
    def audit_orphans(self):
        def work():
            cmd=[str(ROOT/'data-service/venv/bin/python'),str(ROOT/'data-service/scripts/audit_orphan_financial_documents.py'),'--db',str(self.state.path)]
            try: command(cmd,self.log); self.events.put(('artifacts',None))
            except Exception as exc: self.log('ORPHAN AUDIT ERROR '+str(exc))
        threading.Thread(target=work,daemon=True).start()
    def discover(self):
        def work():
            try: rows=discover_remote(self.target,self.log); self.state.upsert_symbols(rows); self.events.put(('refresh',None)); self.log(f'{len(rows)} symbols discovered')
            except Exception as e:self.log('DISCOVER ERROR '+str(e))
        threading.Thread(target=work,daemon=True).start()
    def export_rows(self):
        out=ROOT/'artifacts'/'local-coverage-export.csv'; rows=self.state.rows(); query=self.search_var.get().strip().casefold(); selected=self.industry_var.get()
        with out.open('w',newline='',encoding='utf-8-sig') as handle:
            writer=csv.writer(handle); writer.writerow(('نماد','صنعت','وضعیت','محلی','سرور','کمبودها','خطا'))
            for row in rows:
                if query and query not in (row[0] or '').casefold(): continue
                if selected!='همه صنایع' and (row[1] or 'نامشخص')!=selected: continue
                writer.writerow(row)
        self.log(f'CSV exported: {out}')
    def run(self,do_import,selected_only=False):
        selected={self.tree.item(item,'values')[0] for item in self.tree.selection()} if selected_only else None
        symbols=[r[0] for r in self.state.rows() if r[0] and (selected is None or r[0] in selected)]
        if selected_only and not symbols:
            messagebox.showwarning('نمادها','ابتدا یک یا چند نماد را در جدول انتخاب کنید'); return
        if not symbols: messagebox.showwarning('نمادها','ابتدا بررسی سرور را اجرا کنید'); return
        def work():
            out=ROOT/'artifacts'/'console-run'; cmd=[str(ROOT/'data-service'/'venv'/'bin'/'python'),str(ROOT/'data-service/scripts/daily_local_ingestion.py')]
            symbols=[r[0] for r in self.state.rows() if r[0] and r[2] != 'complete' and (selected is None or r[0] in selected)]
            for s in symbols: cmd += ['--symbol',s]
            cmd += ['--to-jalali',current_jalali(),'--out',str(out)]
            cmd.append('--download-documents')
            if do_import: cmd.append('--import')
            else: cmd.append('--dry-run')
            try: command(cmd,self.log)
            except Exception as e:self.log('RUN ERROR '+str(e))
        threading.Thread(target=work,daemon=True).start()
    def drain(self):
        while not self.events.empty():
            kind,value=self.events.get();
            if kind=='log': self.logbox.insert('end',value+'\n','rtl'); self.logbox.see('end')
            elif kind=='refresh': self.refresh()
            elif kind=='artifacts': self.refresh_artifacts()
        self.root.after(250,self.drain)
def main():
    p=argparse.ArgumentParser(); p.add_argument('--db',default=str(DEFAULT_DB)); p.add_argument('--ssh-target',default='boursnegar'); p.add_argument('--no-gui',action='store_true'); a=p.parse_args()
    state=State(a.db)
    if a.no_gui: print(json.dumps({'db':a.db,'symbols':len(state.rows())},ensure_ascii=False)); return
    if tk is None: raise SystemExit('Tkinter is not installed; install the OS python3-tk package to use the GUI')
    root=tk.Tk(); root.title('Boursnegar Local Ingestion Console'); root.geometry('1100x700'); App(root,state,a.ssh_target); root.mainloop()
if __name__=='__main__': main()
