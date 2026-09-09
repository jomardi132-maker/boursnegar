#!/usr/bin/env python3
"""Local ingestion console for Boursnegar.

This is the operator-facing coordinator. It owns a local SQLite state database,
uses Chrome for Codal, keeps artifacts/checkpoints locally, and invokes the
existing SSH importer. It never opens a Production database connection.
"""
from __future__ import annotations
import argparse, csv, json, queue, re, shlex, sqlite3, subprocess, threading, time
from datetime import datetime, timezone
from pathlib import Path
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    import tkinter.font as tkfont
except ModuleNotFoundError:
    tk=ttk=messagebox=None
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ModuleNotFoundError:
    arabic_reshaper = None
    get_display = None

def fa(value):
    """Shape Persian text for Tk, which has no Arabic shaping engine."""
    value = '' if value is None else str(value)
    if not any('\u0600' <= ch <= '\u06ff' for ch in value):
        return value
    if arabic_reshaper and get_display:
        return get_display(arabic_reshaper.reshape(value))
    return value

ROOT=Path(__file__).resolve().parents[2]
DEFAULT_DB=ROOT/'data-service'/'artifacts'/'local-ingestion.sqlite3'
DEFAULT_RUN_ROOT=ROOT/'data-service'/'artifacts'/'auto-sync'
PIPELINE_MODES=('plan','local','full')
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

def build_pipeline_command(*, mode, db, ssh_target, from_jalali, to_jalali, limit, run_root=DEFAULT_RUN_ROOT):
    """Build the one canonical Local-to-Production workflow command."""
    if mode not in PIPELINE_MODES:
        raise ValueError(f'unsupported pipeline mode: {mode}')
    date_pattern=r'^\d{4}/\d{2}/\d{2}$'
    if not re.match(date_pattern, from_jalali) or not re.match(date_pattern, to_jalali):
        raise ValueError('تاریخ باید با قالب ۱۴۰۵/۰۶/۱۷ وارد شود')
    limit=int(limit)
    if not 1 <= limit <= 1524:
        raise ValueError('اندازه batch باید بین ۱ و ۱۵۲۴ باشد')
    script = 'complete_local_then_server.py' if mode in {'local','full'} else 'auto_local_to_production.py'
    size_flag = '--batch-size' if mode in {'local','full'} else '--limit'
    cmd=[str(ROOT/'data-service/venv/bin/python'),
         str(ROOT/'data-service/scripts'/script),
         '--db',str(Path(db).resolve()),'--ssh-target',ssh_target,
         '--from-jalali',from_jalali,'--to-jalali',to_jalali,
         size_flag,str(limit),'--run-root',str(Path(run_root).resolve())]
    if mode == 'full':
        cmd.append('--apply-production')
    return cmd
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
    def ensure_symbols(self, rows):
        """Add newly active symbols without overwriting Local coverage with remote counts."""
        self.db.executemany(
            'INSERT OR IGNORE INTO symbols(symbol,industry,status,updated_at) VALUES(?,?,?,?)',
            [(r['symbol'],r.get('industry'),'unknown',now()) for r in rows],
        )
        self.db.commit()
    def rows(self):
        try:
            return self.db.execute('''SELECT s.symbol,s.industry,s.status,s.standard_count,s.period_count,s.gap_summary,s.last_error,
                COALESCE(c.ready,0),COALESCE(c.conflicts,0),COALESCE(c.unlinked,0)
                FROM symbols s LEFT JOIN (
                  SELECT inferred_symbol,
                    SUM(CASE WHEN status='READY_FOR_NORMALIZATION' THEN 1 ELSE 0 END) ready,
                    SUM(CASE WHEN status='NEEDS_DISAMBIGUATION' THEN 1 ELSE 0 END) conflicts,
                    SUM(CASE WHEN status='READY_FOR_LINKAGE' THEN 1 ELSE 0 END) unlinked
                  FROM orphan_fact_candidates GROUP BY inferred_symbol
                ) c ON c.inferred_symbol=s.symbol ORDER BY s.symbol''').fetchall()
        except sqlite3.OperationalError as exc:
            if 'orphan_fact_candidates' not in str(exc):
                raise
            return self.db.execute('''SELECT symbol,industry,status,standard_count,period_count,
                gap_summary,last_error,0,0,0 FROM symbols ORDER BY symbol''').fetchall()
    def artifact_rows(self):
        try:
            return self.db.execute('''SELECT f.path,f.role,f.status,f.size_bytes,f.json_records,f.json_errors,
                f.imported_rows,COALESCE(p.status,''),COALESCE(p.inferred_symbol,'')
                FROM artifact_files f LEFT JOIN artifact_parse_results p ON p.path=f.path ORDER BY f.path LIMIT 5000''').fetchall()
        except sqlite3.OperationalError:
            try:
                return [tuple(row)+('','') for row in self.db.execute('SELECT path,role,status,size_bytes,json_records,json_errors,imported_rows FROM artifact_files ORDER BY path LIMIT 5000')]
            except sqlite3.OperationalError:
                return []
    def artifact_summary(self):
        try:
            summary = dict(self.db.execute('SELECT status,COUNT(*) FROM artifact_files GROUP BY status'))
            for suffix in ('pdf', 'html', 'htm'):
                summary[suffix] = self.db.execute("SELECT COUNT(*) FROM artifact_files WHERE role='DOCUMENT' AND lower(path) LIKE ?", (f'%.{suffix}',)).fetchone()[0]
            return summary
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
    def overview(self):
        symbols=self.db.execute('SELECT COUNT(*), SUM(status="complete"), SUM(status="comparable"), SUM(status="incomplete") FROM symbols').fetchone()
        latest=self.db.execute('SELECT started_at,finished_at,status,stage,summary FROM runs ORDER BY id DESC LIMIT 1').fetchone()
        return {'symbols':int(symbols[0] or 0),'complete':int(symbols[1] or 0),'comparable':int(symbols[2] or 0),
                'incomplete':int(symbols[3] or 0),'latest':latest}
    def recent_runs(self,limit=50):
        return self.db.execute('SELECT id,started_at,finished_at,status,stage,summary FROM runs ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
def command(args, log):
    log('RUN '+ ' '.join(map(str,args))); p=subprocess.Popen(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf8',errors='replace')
    for line in p.stdout: log(line.rstrip())
    code=p.wait()
    if code!=0: raise RuntimeError(f'command failed with exit code {code}')
    return {'exit_code':code,'command':' '.join(map(str,args))}
def discover_remote(target, log):
    sql="""SELECT COALESCE(ind.title_fa,'نامشخص'),sa.symbol,0,
      count(DISTINCT ff.fact_key) FILTER (WHERE ff.quality_status='VALID'),
      count(DISTINCT fp.end_date) FILTER (WHERE ff.quality_status='VALID')
      FROM symbol_aliases sa JOIN instruments i ON i.id=sa.instrument_id JOIN issuers iss ON iss.id=i.issuer_id
      LEFT JOIN industries ind ON ind.id=iss.industry_id LEFT JOIN financial_periods fp ON fp.issuer_id=iss.id
      LEFT JOIN financial_facts ff ON ff.period_id=fp.id
      WHERE sa.valid_to IS NULL AND i.active GROUP BY ind.title_fa,sa.symbol ORDER BY 1,2;"""
    # sudo keeps the SSH account's current directory.  Moving to /tmp first
    # prevents PostgreSQL's harmless but alarming "/root: Permission denied"
    # warning from being shown as an operator error in the GUI log.
    remote_cmd='cd /tmp && sudo -u postgres psql -d boursnegar_db -Atc '+shlex.quote(sql)
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
    @staticmethod
    def shape_static_text(widget):
        """Apply Arabic shaping to Tk widgets while keeping model values logical."""
        try:
            text = widget.cget('text')
            if text and any('\u0600' <= ch <= '\u06ff' for ch in str(text)):
                widget.configure(text=fa(text))
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            App.shape_static_text(child)

    def __init__(self,root,state,target):
        if not arabic_reshaper: raise RuntimeError('برای نمایش صحیح فارسی، وابستگی‌های arabic-reshaper و python-bidi را نصب کنید')
        self.root=root; self.state=state; self.target=target; self.events=queue.Queue(); families=tkfont.families(root); family=next((x for x in ('Vazirmatn','Estedad','Noto Sans Arabic','DejaVu Sans') if x in families),'DejaVu Sans'); self.font=tkfont.Font(root,family=family,size=11); self.bold=tkfont.Font(root,family=family,size=11,weight='bold'); style=ttk.Style(root); style.theme_use('clam'); style.configure('.',font=self.font,background='#111827',foreground='#e5e7eb'); style.configure('TFrame',background='#111827'); style.configure('TLabel',background='#111827',foreground='#e5e7eb'); style.configure('TButton',background='#1f2937',foreground='#f9fafb',padding=(12,7),borderwidth=1,focuscolor='#60a5fa',focusthickness=2); style.map('TButton',background=[('active','#2563eb'),('pressed','#1d4ed8'),('disabled','#334155')]); style.configure('TNotebook',background='#0b1220',borderwidth=0); style.configure('TNotebook.Tab',background='#1f2937',foreground='#cbd5e1',padding=(18,9)); style.map('TNotebook.Tab',background=[('selected','#2563eb')],foreground=[('selected','#ffffff')]); style.configure('TEntry',fieldbackground='#0f172a',foreground='#f8fafc'); style.configure('TCombobox',fieldbackground='#0f172a',background='#1f2937',foreground='#f8fafc'); style.configure('Persian.Treeview',background='#0f172a',fieldbackground='#0f172a',foreground='#e5e7eb',font=self.font,rowheight=32); style.configure('Persian.Treeview.Heading',background='#1e293b',foreground='#f8fafc',font=self.bold); style.map('Persian.Treeview',background=[('selected','#1d4ed8')]); root.option_add('*Font', self.font); root.configure(background='#0b1220'); root.tk.call('tk', 'scaling', 1.15)
        self.search_var=tk.StringVar(); self.industry_var=tk.StringVar(value='همه صنایع'); self.status_var=tk.StringVar(value='همه وضعیت‌ها'); self.gap_var=tk.StringVar(value='همه کمبودها'); self.summary_var=tk.StringVar(); self.file_search_var=tk.StringVar(); self.file_role_var=tk.StringVar(value='همه انواع'); self.file_status_var=tk.StringVar(value='همه وضعیت‌ها'); self.file_summary_var=tk.StringVar()
        self.from_var=tk.StringVar(value='1404/01/01'); self.to_var=tk.StringVar(value=current_jalali()); self.limit_var=tk.IntVar(value=10)
        self.pipeline_status_var=tk.StringVar(value='آماده'); self.local_status_var=tk.StringVar(); self.server_status_var=tk.StringVar(value='بررسی نشده'); self.last_run_var=tk.StringVar(); self.busy=False
        notebook=ttk.Notebook(root); notebook.pack(fill='both',expand=True,padx=8,pady=8); operations_tab=ttk.Frame(notebook); symbols_tab=ttk.Frame(notebook); files_tab=ttk.Frame(notebook); notebook.add(operations_tab,text=fa('مرکز عملیات')); notebook.add(symbols_tab,text=fa('وضعیت نمادها')); notebook.add(files_tab,text=fa('دفترکل فایل‌های محلی'))
        self.build_operations_tab(operations_tab)
        filters=ttk.Frame(symbols_tab); filters.pack(fill='x',padx=8,pady=(8,2)); ttk.Label(filters,text='جست‌وجوی نماد:').pack(side='right'); search=ttk.Entry(filters,textvariable=self.search_var,width=18); search.pack(side='right',padx=5); search.bind('<KeyRelease>',lambda _e:self.refresh()); ttk.Label(filters,text='صنعت:').pack(side='right',padx=(8,2)); self.industry_box=ttk.Combobox(filters,textvariable=self.industry_var,state='readonly',width=20); self.industry_box.pack(side='right'); self.industry_box.bind('<<ComboboxSelected>>',lambda _e:self.refresh()); ttk.Label(filters,text='وضعیت:').pack(side='right',padx=(8,2)); self.status_box=ttk.Combobox(filters,textvariable=self.status_var,state='readonly',values=('همه وضعیت‌ها','کامل','قابل‌مقایسه','ناقص'),width=13); self.status_box.pack(side='right'); self.status_box.bind('<<ComboboxSelected>>',lambda _e:self.refresh()); ttk.Label(filters,text='کمبود:').pack(side='right',padx=(8,2)); self.gap_box=ttk.Combobox(filters,textvariable=self.gap_var,state='readonly',width=18); self.gap_box.pack(side='right'); self.gap_box.bind('<<ComboboxSelected>>',lambda _e:self.refresh()); ttk.Label(symbols_tab,textvariable=self.summary_var,anchor='e',font=self.bold).pack(fill='x',padx=8,pady=3)
        self.tree=ttk.Treeview(symbols_tab,columns=('symbol','industry','status','percent','facts','periods','gaps','error','ready','conflicts','unlinked'),show='headings',style='Persian.Treeview'); self.tree.tag_configure('complete',foreground='#198754'); self.tree.tag_configure('comparable',foreground='#9a6700'); self.tree.tag_configure('incomplete',foreground='#b42318')
        for c,t,w in zip(self.tree['columns'],('نماد','صنعت','وضعیت لوکال','تکمیل','fact معتبر','تعداد دوره','کمبودها','خطا','آماده','تعارض','بی‌اتصال'),(110,180,120,75,90,90,240,260,80,80,80)): self.tree.heading(c,text=fa(t),anchor='e'); self.tree.column(c,anchor='e',width=w)
        self.tree.pack(fill='both',expand=True,padx=8,pady=8); bar=ttk.Frame(symbols_tab); bar.pack(fill='x',padx=8,pady=4); ttk.Button(bar,text='بررسی سرور',command=self.discover).pack(side='right'); ttk.Button(bar,text='تکمیل محلی از کدال',command=lambda:self.run_pipeline('local')).pack(side='right',padx=5); ttk.Button(bar,text='تکمیل و ارسال به سرور',command=lambda:self.run_pipeline('full')).pack(side='right',padx=5); ttk.Button(bar,text='خروجی CSV',command=self.export_rows).pack(side='left'); ttk.Label(bar,text='اطلاعات فقط پس از کنترل کیفیت ارسال می‌شود.').pack(side='left',padx=12)
        file_filters=ttk.Frame(files_tab); file_filters.pack(fill='x',padx=8,pady=8); ttk.Label(file_filters,text='جست‌وجوی مسیر:').pack(side='right'); file_search=ttk.Entry(file_filters,textvariable=self.file_search_var,width=36); file_search.pack(side='right',padx=5); file_search.bind('<KeyRelease>',lambda _e:self.refresh_artifacts()); ttk.Label(file_filters,text='نوع:').pack(side='right'); self.file_role_box=ttk.Combobox(file_filters,textvariable=self.file_role_var,state='readonly',width=14); self.file_role_box.pack(side='right',padx=5); self.file_role_box.bind('<<ComboboxSelected>>',lambda _e:self.refresh_artifacts()); ttk.Label(file_filters,text='وضعیت:').pack(side='right'); self.file_status_box=ttk.Combobox(file_filters,textvariable=self.file_status_var,state='readonly',width=14); self.file_status_box.pack(side='right',padx=5); self.file_status_box.bind('<<ComboboxSelected>>',lambda _e:self.refresh_artifacts()); ttk.Button(file_filters,text='بازخوانی دفترکل',command=self.scan_artifacts).pack(side='left'); ttk.Button(file_filters,text='ممیزی Excelهای بی‌مرجع',command=self.audit_orphans).pack(side='left',padx=5); ttk.Button(file_filters,text='خروجی صف بررسی',command=self.export_candidate_review).pack(side='left',padx=5)
        ttk.Label(files_tab,textvariable=self.file_summary_var,anchor='e',font=self.bold).pack(fill='x',padx=8,pady=3); self.file_tree=ttk.Treeview(files_tab,columns=('path','role','status','size','records','errors','imported','parse','symbol'),show='headings',style='Persian.Treeview');
        for c,t,w in zip(self.file_tree['columns'],('مسیر','نوع','وضعیت','حجم','رکورد','خطای JSON','واردشده','نتیجه پردازش','نماد مستند'),(440,90,100,90,80,80,80,150,100)): self.file_tree.heading(c,text=fa(t),anchor='e'); self.file_tree.column(c,anchor='e',width=w)
        self.file_tree.pack(fill='both',expand=True,padx=8,pady=8); self.logbox=tk.Text(root,height=8,font=self.font,wrap='word',background='#0b1220',foreground='#cbd5e1',insertbackground='#ffffff',relief='flat',padx=12,pady=10); self.logbox.tag_configure('rtl',justify='right',foreground='#cbd5e1'); self.logbox.pack(fill='x',expand=False,padx=8,pady=8); self.shape_static_text(root); self.refresh(); self.refresh_artifacts(); self.refresh_operations(); root.after(250,self.drain)
    def build_operations_tab(self, tab):
        header=ttk.Frame(tab); header.pack(fill='x',padx=16,pady=(16,8))
        ttk.Label(header,text='مرکز کنترل تکمیل دیتابیس',font=self.bold,anchor='e').pack(fill='x')
        ttk.Label(header,text='یک مسیر واحد: ممیزی → تکمیل لوکال → اعتبارسنجی → backup → انتقال → replay → readiness',anchor='e').pack(fill='x',pady=(4,0))
        cards=ttk.Frame(tab); cards.pack(fill='x',padx=16,pady=8)
        for title,var in (('وضعیت لوکال',self.local_status_var),('وضعیت سرور',self.server_status_var),('آخرین اجرا',self.last_run_var)):
            card=ttk.LabelFrame(cards,text=title,padding=12); card.pack(side='right',fill='both',expand=True,padx=4)
            ttk.Label(card,textvariable=var,anchor='e',justify='right',wraplength=360).pack(fill='both',expand=True)
        settings=ttk.LabelFrame(tab,text='محدوده اجرا',padding=12); settings.pack(fill='x',padx=16,pady=8)
        ttk.Label(settings,text='تا تاریخ:').pack(side='right'); ttk.Entry(settings,textvariable=self.to_var,width=13,justify='center').pack(side='right',padx=5)
        ttk.Label(settings,text='از تاریخ:').pack(side='right',padx=(16,0)); ttk.Entry(settings,textvariable=self.from_var,width=13,justify='center').pack(side='right',padx=5)
        ttk.Label(settings,text='تعداد نماد در این batch:').pack(side='right',padx=(16,0)); ttk.Spinbox(settings,from_=1,to=1524,textvariable=self.limit_var,width=8,justify='center').pack(side='right',padx=5)
        ttk.Label(settings,text='پیش‌فرض کوچک است؛ برای کل صف ۱۵۲۴ را وارد کنید.',foreground='#94a3b8').pack(side='left')
        actions=ttk.Frame(tab); actions.pack(fill='x',padx=16,pady=8)
        self.pipeline_buttons=[]
        for text,mode in (('۱. فقط پیش‌بررسی امن','plan'),('۲. تکمیل خودکار دیتابیس لوکال','local'),('۳. تکمیل لوکال و همگام‌سازی سرور','full')):
            button=ttk.Button(actions,text=text,command=lambda m=mode:self.run_pipeline(m)); button.pack(side='right',padx=4); self.pipeline_buttons.append(button)
        archive_button=ttk.Button(actions,text='بازیابی هوشمند آرشیو',command=self.recover_archive); archive_button.pack(side='right',padx=4); self.pipeline_buttons.append(archive_button)
        refresh_button=ttk.Button(actions,text='بازخوانی وضعیت',command=self.refresh_control_status); refresh_button.pack(side='left'); self.pipeline_buttons.append(refresh_button)
        progress=ttk.Frame(tab); progress.pack(fill='x',padx=16,pady=(8,4))
        ttk.Label(progress,textvariable=self.pipeline_status_var,anchor='e',font=self.bold).pack(fill='x')
        self.pipeline_progress=ttk.Progressbar(progress,mode='indeterminate'); self.pipeline_progress.pack(fill='x',pady=(6,0))
        history=ttk.LabelFrame(tab,text='تاریخچه اجرای همین کنترل‌سنتر',padding=8); history.pack(fill='both',expand=True,padx=16,pady=(8,16))
        self.run_tree=ttk.Treeview(history,columns=('id','start','finish','status','stage','summary'),show='headings',style='Persian.Treeview',height=5)
        for c,t,w in zip(self.run_tree['columns'],('شناسه','شروع','پایان','وضعیت','مرحله','خلاصه'),(70,180,180,100,180,520)):
            self.run_tree.heading(c,text=fa(t),anchor='e'); self.run_tree.column(c,anchor='e',width=w)
        self.run_tree.pack(fill='both',expand=True)
    def refresh_operations(self):
        overview=self.state.overview(); total=overview['symbols']; complete=overview['complete']; incomplete=overview['incomplete']
        self.local_status_var.set(fa(f'دیتابیس: {self.state.path}\nنمادها: {total} | کامل: {complete} | ناقص: {incomplete}'))
        latest=overview['latest']
        self.last_run_var.set(fa('هنوز اجرایی ثبت نشده' if not latest else f'{latest[3]} | {latest[2]}\nشروع: {latest[0]}'))
        for item in self.run_tree.get_children(): self.run_tree.delete(item)
        for row in self.state.recent_runs():
            values=list(row); values[-1]=(values[-1] or '')[:240]
            self.run_tree.insert('', 'end', values=tuple(fa(value) for value in values))
    def set_busy(self,busy,status):
        self.busy=busy; self.pipeline_status_var.set(fa(status))
        for button in self.pipeline_buttons: button.configure(state='disabled' if busy else 'normal')
        if busy: self.pipeline_progress.start(12)
        else: self.pipeline_progress.stop()
    def refresh_control_status(self):
        if self.busy: return
        self.set_busy(True,'در حال بررسی اتصال و readiness سرور…')
        def work():
            try:
                out=subprocess.check_output(['ssh',self.target,'curl -fsS http://127.0.0.1:8001/readyz'],text=True,timeout=30).strip()
                self.events.put(('control_status',('ready' in out.lower(),out)))
            except Exception as exc: self.events.put(('control_status',(False,str(exc))))
        threading.Thread(target=work,daemon=True).start()
    def run_pipeline(self,mode):
        if self.busy: return
        try:
            cmd=build_pipeline_command(mode=mode,db=self.state.path,ssh_target=self.target,
                from_jalali=self.from_var.get().strip(),to_jalali=self.to_var.get().strip(),
                limit=self.limit_var.get())
        except Exception as exc:
            messagebox.showerror(fa('تنظیمات نامعتبر'),fa(str(exc))); return
        labels={'plan':'پیش‌بررسی','local':'تکمیل لوکال','full':'تکمیل لوکال و سرور'}
        if mode=='full' and not messagebox.askyesno(fa('تأیید همگام‌سازی Production'),fa(
            f'این اجرا حداکثر {self.limit_var.get()} نماد را پردازش می‌کند و فقط پس از manifest و backup به سرور می‌فرستد. ادامه می‌دهید؟')):
            return
        self.set_busy(True,f'{labels[mode]} در حال اجراست؛ لاگ پایین پنجره زنده است…')
        def work():
            try:
                result=self.state.run(f'control-center:{mode}',lambda:command(cmd,self.log))
                self.events.put(('pipeline_done',(True,labels[mode],result)))
            except Exception as exc:
                self.events.put(('pipeline_done',(False,labels[mode],str(exc))))
        threading.Thread(target=work,daemon=True).start()
    def log(self,s): self.events.put(('log',fa(s)))
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
            status=row[2]; values=list(row); values[2]=labels.get(status,values[2]); standard=max(0,int(row[3] or 0)); periods=max(0,int(row[4] or 0)); values.insert(3,f'{min(100,round(standard*70/7+periods*30/2))}%'); self.tree.insert('', 'end', values=tuple(fa(value) for value in values), tags=(status,))
        counts={key:sum(1 for r in rows if r[2]==key) for key in ('complete','comparable','incomplete')}; total=len(rows); pct=(counts['complete']*100/total) if total else 0
        self.summary_var.set(fa(f'پوشش دیتابیس لوکال — کل: {total}  |  کامل: {counts["complete"]}  |  قابل‌مقایسه: {counts["comparable"]}  |  ناقص: {counts["incomplete"]}  |  تکمیل کامل: {pct:.1f}%  |  نمایش: {len(visible)}'))
    def refresh_artifacts(self):
        for item in self.file_tree.get_children(): self.file_tree.delete(item)
        rows=self.state.artifact_rows(); roles=sorted({r[1] for r in rows}); statuses=sorted({r[2] for r in rows}); self.file_role_box['values']=['همه انواع']+roles; self.file_status_box['values']=['همه وضعیت‌ها']+statuses
        query=self.file_search_var.get().strip().casefold(); selected_role=self.file_role_var.get(); selected_status=self.file_status_var.get(); visible=[]
        for row in rows:
            if query and query not in row[0].casefold(): continue
            if selected_role!='همه انواع' and row[1]!=selected_role: continue
            if selected_status!='همه وضعیت‌ها' and row[2]!=selected_status: continue
            visible.append(row)
        for row in visible[:5000]: self.file_tree.insert('', 'end', values=tuple(fa(value) for value in row))
        counts=self.state.artifact_summary(); parsed=self.state.parse_summary(); candidates=self.state.candidate_summary(); self.file_summary_var.set(fa(f'کل فایل: {len(rows)}  |  PDF: {counts.get("pdf",0)}  |  HTML: {counts.get("html",0)+counts.get("htm",0)}  |  بی‌مرجع: {counts.get("DISCOVERED",0)}  |  Excel دارای fact: {parsed.get("PARSED_WITH_FACTS",0)}  |  آماده نرمال‌سازی: {candidates.get("READY_FOR_NORMALIZATION",0)}  |  منتظر اتصال: {candidates.get("READY_FOR_LINKAGE",0)}  |  تکراری: {candidates.get("DUPLICATE_EXISTING",0)}  |  تعارض: {candidates.get("NEEDS_DISAMBIGUATION",0)}  |  نمایش: {min(len(visible),5000)}'))
    def scan_artifacts(self):
        def work():
            cmd=['python3',str(ROOT/'data-service/scripts/reconcile_local_artifacts.py'),'--db',str(self.state.path)]
            for folder in ('all-symbols-v16','all-symbols-v17','all-symbols-v18'): cmd += ['--root',str(ROOT/'artifacts'/folder)]
            try: command(cmd,self.log); self.events.put(('artifacts',None))
            except Exception as exc: self.log('LEDGER ERROR '+str(exc))
        threading.Thread(target=work,daemon=True).start()
    def recover_archive(self):
        if self.busy: return
        archive=Path('/home/king/Boursnegar-artifacts-archive-20260906')
        if not archive.is_dir():
            messagebox.showerror(fa('آرشیو پیدا نشد'),fa(str(archive))); return
        if not messagebox.askyesno(fa('بازیابی آرشیو'),fa('از دیتابیس فعلی backup گرفته می‌شود؛ فقط شواهد قطعی وارد و موارد مبهم گزارش می‌شوند. ادامه می‌دهید؟')):
            return
        self.set_busy(True,'بازیابی و ممیزی آرشیو در حال اجراست…')
        cmd=[str(ROOT/'data-service/venv/bin/python'),str(ROOT/'data-service/scripts/recover_local_archive.py'),
             '--db',str(self.state.path),'--archive',str(archive),'--apply']
        def work():
            try:
                result=self.state.run('control-center:archive-recovery',lambda:command(cmd,self.log))
                self.events.put(('pipeline_done',(True,'بازیابی آرشیو',result)))
            except Exception as exc:
                self.events.put(('pipeline_done',(False,'بازیابی آرشیو',str(exc))))
        threading.Thread(target=work,daemon=True).start()
    def audit_orphans(self):
        def work():
            cmd=[str(ROOT/'data-service/venv/bin/python'),str(ROOT/'data-service/scripts/audit_orphan_financial_documents.py'),'--db',str(self.state.path)]
            try: command(cmd,self.log); self.events.put(('artifacts',None))
            except Exception as exc: self.log('ORPHAN AUDIT ERROR '+str(exc))
        threading.Thread(target=work,daemon=True).start()
    def export_candidate_review(self):
        out=ROOT/'artifacts'/'candidate-review.csv'
        try:
            command([str(ROOT/'data-service/venv/bin/python'),str(ROOT/'data-service/scripts/export_candidate_review.py'),'--db',str(self.state.path),'--out',str(out)],self.log)
        except Exception as exc: self.log('REVIEW EXPORT ERROR '+str(exc))
    def discover(self):
        def work():
            try:
                rows=discover_remote(self.target,self.log); self.state.ensure_symbols(rows)
                counts={key:sum(1 for row in rows if row.get('status')==key) for key in ('complete','comparable','incomplete')}
                self.events.put(('server_discovery',(len(rows),counts))); self.log(f'{len(rows)} symbols discovered')
            except Exception as e:self.log('DISCOVER ERROR '+str(e))
        threading.Thread(target=work,daemon=True).start()
    def export_rows(self):
        out=ROOT/'artifacts'/'local-coverage-export.csv'; rows=self.state.rows(); query=self.search_var.get().strip().casefold(); selected=self.industry_var.get()
        with out.open('w',newline='',encoding='utf-8-sig') as handle:
            writer=csv.writer(handle); writer.writerow(('نماد','صنعت','وضعیت','محلی','سرور','کمبودها','خطا','آماده','تعارض','بی‌اتصال'))
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
    def run_auto(self, send):
        self.run_pipeline('full' if send else 'local')
    def drain(self):
        while not self.events.empty():
            kind,value=self.events.get();
            if kind=='log': self.logbox.insert('end',value+'\n','rtl'); self.logbox.see('end')
            elif kind=='refresh': self.refresh()
            elif kind=='artifacts': self.refresh_artifacts()
            elif kind=='server_discovery':
                total,counts=value; self.server_status_var.set(fa(f'Production — کل: {total} | کامل: {counts["complete"]} | قابل‌مقایسه: {counts["comparable"]} | ناقص: {counts["incomplete"]}')); self.refresh()
            elif kind=='control_status':
                ready,detail=value; self.server_status_var.set(fa(('آماده | ' if ready else 'خطا | ')+detail)); self.set_busy(False,'بررسی وضعیت پایان یافت'); self.refresh_operations()
            elif kind=='pipeline_done':
                success,label,detail=value; self.set_busy(False,(label+' با موفقیت پایان یافت') if success else (label+' شکست خورد'))
                self.log(('SUCCESS ' if success else 'ERROR ')+str(detail)); self.refresh(); self.refresh_artifacts(); self.refresh_operations()
        self.root.after(250,self.drain)
def main():
    p=argparse.ArgumentParser(); p.add_argument('--db',default=str(DEFAULT_DB)); p.add_argument('--ssh-target',default='boursnegar'); p.add_argument('--no-gui',action='store_true'); a=p.parse_args()
    state=State(a.db)
    if a.no_gui: print(json.dumps({'db':a.db,'symbols':len(state.rows())},ensure_ascii=False)); return
    if tk is None: raise SystemExit('Tkinter is not installed; install the OS python3-tk package to use the GUI')
    root=tk.Tk(); root.title('Boursnegar Local Ingestion Console'); root.geometry('1500x850'); root.minsize(1100,650); App(root,state,a.ssh_target); root.mainloop()
if __name__=='__main__': main()
