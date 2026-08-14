import re
import json
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models
from app.services import tsetmc_service, codal_service, codal_excel_parser, ratio_engine
from app.analytics.snapshot_v2 import build_snapshot_payload

# ساخت جدول‌ها در صورت عدم وجود (برای MVP کافیه؛ بعداً می‌تونیم Alembic اضافه کنیم)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Boursnegar Data Service", version="0.1.0")
_DATE_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


class AnalysisV2Request(BaseModel):
    query: str = Field(min_length=1, max_length=32)
    report_mode: str = Field(default="audited", alias="reportMode")


def _persist_v2_snapshot(db: Session, raw: dict, payload: dict) -> str:
    live = raw.get("live_price") or {}
    symbol = str(raw.get("symbol") or "").strip()
    stable_code = str(live.get("isin") or f"symbol:{symbol}")
    industry_title = str(live.get("market_category") or "نامشخص")
    row = db.execute(
        text(
            """
            WITH industry AS (
              INSERT INTO industries(code,title_fa,model_family)
              VALUES(:industry_code,:industry_title,'unclassified')
              ON CONFLICT(code) DO UPDATE SET title_fa=excluded.title_fa
              RETURNING id
            ), issuer AS (
              INSERT INTO issuers(stable_code,legal_name,industry_id)
              VALUES(:stable_code,:legal_name,(SELECT id FROM industry))
              ON CONFLICT(stable_code) DO UPDATE
                SET legal_name=excluded.legal_name,industry_id=excluded.industry_id,updated_at=now()
              RETURNING id
            ), instrument AS (
              INSERT INTO instruments(issuer_id,isin,market_instrument_id)
              VALUES((SELECT id FROM issuer),:isin,:market_id)
              ON CONFLICT(isin) DO UPDATE SET market_instrument_id=excluded.market_instrument_id
              RETURNING id
            ), alias AS (
              INSERT INTO symbol_aliases(instrument_id,symbol,valid_from,source)
              VALUES((SELECT id FROM instrument),:symbol,current_date,'market')
              ON CONFLICT(instrument_id,symbol,valid_from) DO NOTHING
            ), snapshot AS (
              INSERT INTO analytical_snapshots(
                instrument_id,report_mode,status,data_as_of,stale_after,coverage,
                confidence,model_version,policy_version,payload_checksum,quality_summary
              ) VALUES(
                (SELECT id FROM instrument),:report_mode,'INSUFFICIENT_DATA',
                :data_as_of,:stale_after,:coverage,:confidence,:model_version,
                :policy_version,:checksum,CAST(:quality_summary AS jsonb)
              )
              ON CONFLICT(instrument_id,report_mode,data_as_of,model_version,policy_version)
              DO UPDATE SET calculated_at=now(),stale_after=excluded.stale_after,
                coverage=excluded.coverage,confidence=excluded.confidence,
                payload_checksum=excluded.payload_checksum,quality_summary=excluded.quality_summary
              RETURNING id
            )
            INSERT INTO recommendation_results(
              snapshot_id,decision,top_reasons,top_risks,critical_warning,policy_version
            ) VALUES(
              (SELECT id FROM snapshot),'INSUFFICIENT_DATA','[]'::jsonb,
              CAST(:risks AS jsonb),
              :warning,:policy_version
            )
            ON CONFLICT(snapshot_id) DO UPDATE SET top_risks=excluded.top_risks,
              critical_warning=excluded.critical_warning,policy_version=excluded.policy_version
            RETURNING snapshot_id
            """
        ),
        {
            "industry_code": f"market:{industry_title}",
            "industry_title": industry_title,
            "stable_code": stable_code,
            "legal_name": raw.get("company_name") or symbol,
            "isin": live.get("isin") or stable_code,
            "market_id": str(live.get("market_id")) if live.get("market_id") else None,
            "symbol": symbol,
            "report_mode": payload["reportMode"],
            "data_as_of": datetime.now(timezone.utc),
            "stale_after": datetime.fromisoformat(payload["staleAfter"]),
            "coverage": payload["dataCoverage"],
            "confidence": payload["confidence"],
            "model_version": payload["modelVersion"],
            "policy_version": payload["policyVersion"],
            "checksum": payload["payloadChecksum"],
            "quality_summary": json.dumps(payload, ensure_ascii=False),
            "risks": json.dumps(payload["risks"], ensure_ascii=False),
            "warning": payload["criticalWarning"],
        },
    ).scalar_one()
    db.commit()
    return str(row)


def _period_end_from_letter(letter: dict) -> str | None:
    text = " ".join(str(letter.get(k) or "") for k in ("Title", "PublishDateTime")).translate(_DATE_DIGITS)
    match = re.search(r"14(?:04|05)[/\-]\d{1,2}[/\-]\d{1,2}", text)
    return match.group(0).replace("-", "/") if match else None


def _persist_letters(db: Session, company: models.Company, letters: list[dict]) -> int:
    """ذخیره idempotent فراداده گزارش‌های ۱۴۰۴ و ۱۴۰۵ برای مقایسه‌های بعدی."""
    inserted = 0
    for rec in letters:
        tracing_no = str(rec.get("TracingNo") or "")
        if not tracing_no:
            continue
        period_end = _period_end_from_letter(rec)
        searchable = " ".join(str(rec.get(k) or "") for k in ("Title", "PublishDateTime")).translate(_DATE_DIGITS)
        if "1404" not in searchable and "1405" not in searchable and period_end is None:
            continue
        existing = db.query(models.FinancialReport).filter(models.FinancialReport.tracing_no == tracing_no).first()
        if existing:
            if period_end and not existing.period_end_date:
                existing.period_end_date = period_end
                existing.raw_json = rec
            continue
        title = rec.get("Title") or ""
        excel_url = rec.get("ExcelUrl") or None
        if excel_url and excel_url.startswith("/"):
            excel_url = f"https://excel.codal.ir{excel_url}"
        detail_url = rec.get("Url") or None
        if detail_url and detail_url.startswith("/"):
            detail_url = f"https://codal.ir{detail_url}"
        db.add(models.FinancialReport(
            company_id=company.id, tracing_no=tracing_no, title=title,
            letter_code=rec.get("LetterCode"), period_end_date=period_end,
            publish_datetime=rec.get("PublishDateTime"),
            is_audited=("حسابرسی شده" in title and "حسابرسی نشده" not in title),
            excel_url=excel_url, detail_url=detail_url, raw_json=rec,
        ))
        inserted += 1
    db.commit()
    return inserted


def _persist_parsed_metrics(db: Session, report: models.FinancialReport | None, parsed: dict) -> int:
    if report is None:
        return 0
    inserted = 0
    for item_name, item_value in parsed.get("metrics", {}).items():
        if item_value is None:
            continue
        exists = db.query(models.FinancialLineItem).filter(
            models.FinancialLineItem.report_id == report.id,
            models.FinancialLineItem.item_name == item_name,
        ).first()
        if exists:
            continue
        statement = "cash_flow" if item_name == "operating_cash_flow" else "balance_sheet" if item_name.startswith("total_") else "income_statement"
        db.add(models.FinancialLineItem(report_id=report.id, statement_type=statement, item_name=item_name, item_value=item_value))
        inserted += 1
    db.commit()
    return inserted


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
        letters = codal_service.fetch_all_letters(symbol, max_pages=4)
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

    # گزارش هم‌طول قبلی برای محاسبه رشد واقعی؛ شکست این بخش تحلیل اصلی را متوقف نمی‌کند.
    title = candidate.get("Title") or ""
    period_label = next((p for p in ("۱۲ ماهه", "۹ ماهه", "۶ ماهه", "۳ ماهه") if p in title), None)
    comparison = None
    comparison_unavailable_reason = "گزارش دوره هم‌طول قبلی دارای فایل اکسل پیدا نشد."
    if period_label:
        previous = next(
            (rec for rec in letters if rec is not candidate and rec.get("HasExcel") and period_label in (rec.get("Title") or "")),
            None,
        )
        if previous:
            previous_url = previous.get("ExcelUrl") or ""
            if previous_url.startswith("/"):
                previous_url = f"https://excel.codal.ir{previous_url}"
            try:
                previous_parsed = codal_excel_parser.fetch_and_parse(previous_url)
                current_revenue = parsed["metrics"].get("revenue")
                previous_revenue = previous_parsed["metrics"].get("revenue")
                current_profit = parsed["metrics"].get("net_profit")
                previous_profit = previous_parsed["metrics"].get("net_profit")
                comparison = {
                    "period_label": period_label,
                    "current_report": candidate.get("TracingNo"),
                    "previous_report": previous.get("TracingNo"),
                    "current_revenue": current_revenue,
                    "previous_revenue": previous_revenue,
                    "revenue_growth_percent": ((current_revenue / previous_revenue) - 1) * 100 if current_revenue is not None and previous_revenue not in (None, 0) else None,
                    "current_net_profit": current_profit,
                    "previous_net_profit": previous_profit,
                    "net_profit_growth_percent": ((current_profit / previous_profit) - 1) * 100 if current_profit is not None and previous_profit not in (None, 0) else None,
                    "source": "صورت‌های مالی رسمی کدال",
                }
                comparison_unavailable_reason = None
            except (codal_excel_parser.CodalExcelDownloadError, codal_excel_parser.CodalExcelParseError):
                comparison_unavailable_reason = "فایل گزارش دوره هم‌طول قبلی قابل دریافت یا استخراج نبود."

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

    history_reports_added = _persist_letters(db, company, letters)
    used_report = db.query(models.FinancialReport).filter(
        models.FinancialReport.tracing_no == str(candidate.get("TracingNo") or "")
    ).first()
    history_line_items_added = _persist_parsed_metrics(db, used_report, parsed)

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
        "period_comparison": comparison,
        "period_comparison_unavailable_reason": comparison_unavailable_reason,
        "ratios": ratios,
        "health": health,
        "history_sync": {
            "years": [1404, 1405],
            "reports_added": history_reports_added,
            "line_items_added": history_line_items_added,
            "policy": "on_symbol_search",
        },
    }


@app.post("/api/v2/analyze")
def analyze_v2(request: AnalysisV2Request, db: Session = Depends(get_db)):
    if request.report_mode not in {"audited", "latest_codal"}:
        raise HTTPException(status_code=400, detail="reportMode نامعتبر است.")
    symbol = request.query.strip().removeprefix("نماد ").strip()
    if not re.fullmatch(r"[\u0600-\u06FFa-zA-Z0-9‌_-]{1,32}", symbol):
        raise HTTPException(status_code=400, detail="نماد نامعتبر است.")
    raw = analyze_symbol(symbol, request.report_mode, db)
    payload = build_snapshot_payload(raw, request.report_mode)
    payload["analysisId"] = _persist_v2_snapshot(db, raw, payload)
    return {"success": True, "data": payload}


@app.get("/api/v2/analysis/{analysis_id}")
def get_analysis_v2(analysis_id: str, db: Session = Depends(get_db)):
    row = db.execute(
        text(
            """
            SELECT s.id,s.status,s.data_as_of,s.calculated_at,s.stale_after,
                   s.coverage,s.confidence,s.model_version,s.policy_version,
                   s.quality_summary,r.decision,r.top_reasons,r.top_risks,
                   r.critical_warning
            FROM analytical_snapshots s
            JOIN recommendation_results r ON r.snapshot_id=s.id
            WHERE s.id=:id
            """
        ),
        {"id": analysis_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="تحلیل پیدا نشد.")
    return {"success": True, "data": dict(row)}


@app.get("/api/v2/symbols/{symbol}")
def get_symbol_v2(symbol: str, db: Session = Depends(get_db)):
    rows = db.execute(
        text(
            """
            SELECT s.id,s.report_mode,s.status,s.data_as_of,s.calculated_at,
                   s.stale_after,s.coverage,s.confidence,r.decision
            FROM symbol_aliases a
            JOIN instruments i ON i.id=a.instrument_id
            JOIN analytical_snapshots s ON s.instrument_id=i.id
            JOIN recommendation_results r ON r.snapshot_id=s.id
            WHERE a.symbol=:symbol AND a.valid_to IS NULL
            ORDER BY s.calculated_at DESC LIMIT 20
            """
        ),
        {"symbol": symbol},
    ).mappings().all()
    return {"success": True, "symbol": symbol, "snapshots": [dict(row) for row in rows]}


@app.get("/api/v2/symbols/{symbol}/lineage")
def get_symbol_lineage_v2(symbol: str, db: Session = Depends(get_db)):
    rows = db.execute(
        text(
            """
            SELECT s.id AS snapshot_id,s.quality_summary->'sourceLineage' AS lineage,
                   s.data_as_of,s.model_version,s.policy_version
            FROM symbol_aliases a
            JOIN instruments i ON i.id=a.instrument_id
            JOIN analytical_snapshots s ON s.instrument_id=i.id
            WHERE a.symbol=:symbol AND a.valid_to IS NULL
            ORDER BY s.calculated_at DESC LIMIT 20
            """
        ),
        {"symbol": symbol},
    ).mappings().all()
    return {"success": True, "symbol": symbol, "lineage": [dict(row) for row in rows]}


@app.get("/api/v2/ingestion/status")
def ingestion_status_v2(db: Session = Depends(get_db)):
    rows = db.execute(
        text(
            """
            SELECT id,pipeline,source,partition_key,status,started_at,finished_at,
                   watermark,metrics,error_summary
            FROM ingestion_runs ORDER BY started_at DESC LIMIT 100
            """
        )
    ).mappings().all()
    return {"success": True, "runs": [dict(row) for row in rows]}
