from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models
from app.services import tsetmc_service, codal_service, codal_excel_parser, ratio_engine

# ساخت جدول‌ها در صورت عدم وجود (برای MVP کافیه؛ بعداً می‌تونیم Alembic اضافه کنیم)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Boursnegar Data Service", version="0.1.0")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/tsetmc/live/{symbol}")
def get_live_price(symbol: str, db: Session = Depends(get_db)):
    """
    داده‌ی زنده‌ی قیمت (از BrsApi.ir - چون اتصال مستقیم به تستمسی از این
    سرور بلاک است). نتیجه در جدول price_snapshots هم ذخیره می‌شه تا
    تاریخچه‌ی قیمت برای نمودار بعداً در دسترس باشه.
    """
    try:
        data = tsetmc_service.fetch_live_snapshot(symbol)
    except tsetmc_service.TsetmcNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except tsetmc_service.TsetmcConfigError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except tsetmc_service.TsetmcUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

    company = db.query(models.Company).filter(models.Company.symbol == symbol).first()
    if not company:
        company = models.Company(symbol=symbol, company_name=data.get("full_name", ""))
        db.add(company)
        db.commit()
        db.refresh(company)
    elif not company.company_name and data.get("full_name"):
        company.company_name = data["full_name"]
        db.commit()

    snapshot = models.PriceSnapshot(
        company_id=company.id,
        price=data.get("last_price"),
        close_price=data.get("closing_price"),
        eps=data.get("eps"),
        pe_ratio=data.get("pe_ratio"),
        market_cap=data.get("market_cap"),
        raw_json=data.get("raw"),
    )
    db.add(snapshot)
    db.commit()

    return {"success": True, "data": data}


@app.get("/api/codal/reports/{symbol}")
def get_codal_reports(symbol: str, db: Session = Depends(get_db)):
    """
    اطلاعیه‌های کدال برای یک نماد. نتیجه در دیتابیس هم ذخیره می‌شه
    (idempotent - بر اساس tracing_no، تکراری ذخیره نمی‌شه).
    """
    try:
        letters = codal_service.fetch_all_letters(symbol, max_pages=2)
    except codal_service.CodalUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if not letters:
        return {"success": True, "count": 0, "letters": []}

    # پیدا کردن یا ساختن شرکت
    company = db.query(models.Company).filter(models.Company.symbol == symbol).first()
    if not company:
        first = letters[0]
        company = models.Company(
            symbol=symbol,
            company_name=first.get("CompanyName", ""),
        )
        db.add(company)
        db.commit()
        db.refresh(company)

    inserted = 0
    for rec in letters:
        tracing_no = str(rec.get("TracingNo", ""))
        if not tracing_no:
            continue
        exists = db.query(models.FinancialReport).filter(
            models.FinancialReport.tracing_no == tracing_no
        ).first()
        if exists:
            continue

        title = rec.get("Title") or ""
        # فیلد "Audited" در پاسخ کدال وجود نداره (فقط پارامتر فیلتر درخواسته)؛
        # وضعیت حسابرسی‌شده‌بودن رو از روی متن عنوان تشخیص می‌دیم.
        is_audited = ("حسابرسی شده" in title) and ("حسابرسی نشده" not in title)

        excel_url = rec.get("ExcelUrl") or None
        if excel_url and excel_url.startswith("http") is False:
            excel_url = f"https://excel.codal.ir{excel_url}" if excel_url.startswith("/") else excel_url

        detail_url = rec.get("Url") or None
        if detail_url and detail_url.startswith("/"):
            detail_url = f"https://codal.ir{detail_url}"

        report = models.FinancialReport(
            company_id=company.id,
            tracing_no=tracing_no,
            title=title,
            letter_code=rec.get("LetterCode"),
            publish_datetime=rec.get("PublishDateTime"),
            is_audited=is_audited,
            excel_url=excel_url,
            detail_url=detail_url,
            raw_json=rec,
        )
        db.add(report)
        inserted += 1

    db.commit()

    return {"success": True, "count": len(letters), "new_saved": inserted, "letters": letters}


@app.get("/api/companies")
def list_companies(db: Session = Depends(get_db)):
    companies = db.query(models.Company).all()
    return {
        "success": True,
        "companies": [
            {"symbol": c.symbol, "company_name": c.company_name, "id": c.id}
            for c in companies
        ],
    }


@app.get("/api/analyze/{symbol}")
def analyze_symbol(symbol: str, report_mode: str = "audited", db: Session = Depends(get_db)):
    """
    endpoint اصلی: قیمت زنده + گزارش‌های کدال + پارس واقعی صورت مالی +
    نسبت‌های محاسبه‌شده - همه با هم، برای ساخت کارت سلامت بنیادی.

    قیمت زنده «best effort» است: اگه نماد تعلیق باشه (مثل فولاد در حال
    حاضر)، بقیه‌ی تحلیل بدون قیمت زنده ادامه پیدا می‌کنه، نه اینکه کل
    درخواست fail بشه.
    """
    # ۱. قیمت زنده (best effort)
    live_data = None
    live_error = None
    try:
        live_data = tsetmc_service.fetch_live_snapshot(symbol)
    except tsetmc_service.TsetmcNotFoundError as e:
        live_error = str(e)
    except (tsetmc_service.TsetmcUnavailableError, tsetmc_service.TsetmcConfigError) as e:
        live_error = str(e)

    # ۲. فهرست گزارش‌های کدال
    try:
        letters = codal_service.fetch_all_letters(symbol, max_pages=2)
    except codal_service.CodalUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if not letters:
        raise HTTPException(status_code=404, detail=f"هیچ گزارشی برای نماد «{symbol}» در کدال پیدا نشد.")

    if report_mode not in {"audited", "latest_codal"}:
        raise HTTPException(status_code=400, detail="report_mode نامعتبر است.")

    # ۳. انتخاب گزارش بر اساس حالت درخواستی
    candidate = None
    if report_mode == "latest_codal":
        candidate = next((rec for rec in letters if rec.get("HasExcel")), None)
    else:
        for rec in letters:
            title = rec.get("Title") or ""
            is_audited = ("حسابرسی شده" in title) and ("حسابرسی نشده" not in title)
            has_excel = bool(rec.get("HasExcel"))
            is_annual = "۱۲ ماهه" in title or "سال مالی" in title
            if is_audited and has_excel and is_annual:
                candidate = rec
                break

    if not candidate:
        report_label = "حسابرسی‌شده سالانه" if report_mode == "audited" else "دارای فایل اکسل"
        raise HTTPException(
            status_code=404,
            detail=f"هیچ گزارش {report_label} برای «{symbol}» در {len(letters)} اطلاعیه‌ی اخیر پیدا نشد.",
        )

    excel_url = candidate.get("ExcelUrl") or ""
    if excel_url.startswith("/"):
        excel_url = f"https://excel.codal.ir{excel_url}"

    # ۴. دانلود و پارس واقعی صورت مالی
    try:
        parsed = codal_excel_parser.fetch_and_parse(excel_url)
    except codal_excel_parser.CodalExcelDownloadError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except codal_excel_parser.CodalExcelParseError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # ۵. محاسبه‌ی نسبت‌ها
    live_pe = live_data.get("pe_ratio") if live_data else None
    industry_category = live_data.get("market_category") if live_data else None
    ratios = ratio_engine.compute_ratios(parsed["metrics"], live_pe_ratio=live_pe)
    health = ratio_engine.evaluate_health_status(ratios, industry_category=industry_category)

    # ۶. ذخیره در دیتابیس
    company = db.query(models.Company).filter(models.Company.symbol == symbol).first()
    if not company:
        company = models.Company(symbol=symbol, company_name=candidate.get("CompanyName", ""))
        db.add(company)
        db.commit()
        db.refresh(company)
    elif candidate.get("CompanyName") and not company.company_name:
        company.company_name = candidate["CompanyName"]
        db.commit()

    ratio_row = models.FinancialRatio(
        company_id=company.id,
        pe_ratio=ratios.get("pe_ratio"),
        eps=parsed["metrics"].get("eps_basic"),
        roe=ratios.get("roe_percent"),
        roa=ratios.get("roa_percent"),
        debt_to_equity=ratios.get("debt_to_equity"),
    )
    db.add(ratio_row)
    db.commit()

    return {
        "success": True,
        "symbol": symbol,
        "company_name": candidate.get("CompanyName"),
        "report_used": {
            "title": candidate.get("Title"),
            "tracing_no": candidate.get("TracingNo"),
            "publish_datetime": candidate.get("PublishDateTime"),
            "excel_url": excel_url,
        },
        "live_price": live_data,
        "live_price_error": live_error,
        "financial_metrics": parsed["metrics"],
        "financial_metrics_found": parsed["found_items"],
        "financial_metrics_missing": parsed["missing_items"],
        "ratios": ratios,
        "health": health,
    }
