import re
import json
import hashlib
import jdatetime
from datetime import date as gregorian_date, datetime, timezone

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models
from app.services import tsetmc_service, codal_service, codal_excel_parser, ratio_engine
from app.analytics.snapshot_v2 import build_snapshot_payload
from app.analytics.period_comparison import build_period_comparison, period_label_from_title
from app.analytics.ttm import FLOW_FACT_KEYS, build_ttm_metrics
from app.ingestion.market_history import model_family

# ساخت جدول‌ها در صورت عدم وجود (برای MVP کافیه؛ بعداً می‌تونیم Alembic اضافه کنیم)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Boursnegar Data Service", version="0.1.0")
_DATE_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


class AnalysisV2Request(BaseModel):
    query: str = Field(min_length=1, max_length=32)
    report_mode: str = Field(default="audited", alias="reportMode")


def _safe_tracing_no(letter: dict) -> str:
    """Keep legacy report keys within the varchar(50) database limit.

    BrsApi can return a full Codal URL in TracingNo. Preserve that URL in
    raw_json/detail_url, while using a deterministic compact key for lookup.
    """
    raw = str(letter.get("TracingNo") or "").strip()
    if len(raw) <= 50:
        return raw
    return "url:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:44]


def _persist_v2_snapshot(db: Session, raw: dict, payload: dict) -> str:
    live = raw.get("live_price") or {}
    symbol = str(raw.get("symbol") or "").strip()
    existing_instrument = db.execute(
        text(
            """
            SELECT i.isin,i.market_instrument_id
            FROM symbol_aliases sa
            JOIN instruments i ON i.id=sa.instrument_id
            WHERE sa.symbol=:symbol AND sa.valid_to IS NULL
            ORDER BY sa.valid_from DESC NULLS LAST
            LIMIT 1
            """
        ),
        {"symbol": symbol},
    ).mappings().first()
    if existing_instrument and not live.get("isin"):
        live = {
            **live,
            "isin": existing_instrument["isin"],
            "market_id": existing_instrument["market_instrument_id"],
        }
    stable_code = str(live.get("isin") or f"symbol:{symbol}")
    industry_title = str(live.get("market_category") or "نامشخص")
    row = db.execute(
        text(
            """
            WITH industry AS (
              INSERT INTO industries(code,title_fa,model_family)
              VALUES(:industry_code,:industry_title,:model_family)
              ON CONFLICT(code) DO UPDATE SET title_fa=excluded.title_fa,
                model_family=CASE WHEN excluded.model_family='unclassified'
                  THEN industries.model_family ELSE excluded.model_family END
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
              ON CONFLICT DO NOTHING
            ), snapshot AS (
              INSERT INTO analytical_snapshots(
                instrument_id,report_mode,status,data_as_of,stale_after,coverage,
                confidence,model_version,policy_version,payload_checksum,quality_summary
              ) VALUES(
                (SELECT id FROM instrument),:report_mode,:decision,
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
              (SELECT id FROM snapshot),:decision,CAST(:reasons AS jsonb),
              CAST(:risks AS jsonb),
              :warning,:policy_version
            )
            ON CONFLICT(snapshot_id) DO UPDATE SET decision=excluded.decision,
              top_reasons=excluded.top_reasons,top_risks=excluded.top_risks,
              critical_warning=excluded.critical_warning,policy_version=excluded.policy_version
            RETURNING snapshot_id
            """
        ),
        {
            "industry_code": f"market:{industry_title}",
            "industry_title": industry_title,
            "model_family": (payload.get("valuation") or {}).get("family", "unclassified"),
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
            "decision": payload["decision"],
            "reasons": json.dumps(payload["reasons"], ensure_ascii=False),
            "risks": json.dumps(payload["risks"], ensure_ascii=False),
            "warning": payload["criticalWarning"],
        },
    ).scalar_one()
    if payload.get("healthScore") is not None:
        db.execute(text("""
          INSERT INTO health_score_results(snapshot_id,score,dimensions,reasons,risks)
          VALUES(:snapshot,:score,CAST(:dimensions AS jsonb),CAST(:reasons AS jsonb),CAST(:risks AS jsonb))
          ON CONFLICT(snapshot_id) DO UPDATE SET score=excluded.score,
            dimensions=excluded.dimensions,reasons=excluded.reasons,risks=excluded.risks
        """), {"snapshot": row, "score": payload["healthScore"],
                 "dimensions": json.dumps(payload.get("healthDimensions") or {}, ensure_ascii=False),
                 "reasons": json.dumps(payload["reasons"], ensure_ascii=False),
                 "risks": json.dumps(payload["risks"], ensure_ascii=False)})
    valuation = payload.get("valuation")
    if valuation:
        base = valuation["fairValueBase"]
        db.execute(text("""
          INSERT INTO valuation_results(
            snapshot_id,model_type,model_version,fair_value_low,fair_value_base,
            fair_value_high,buy_zone,hold_zone,sell_zone,scenarios,assumptions
          ) VALUES(
            :snapshot,:model_type,:model_version,:low,:base,:high,
            jsonb_build_object('max',:buy_max),
            jsonb_build_object('min',:buy_max,'max',:sell_min),
            jsonb_build_object('min',:sell_min),
            CAST(:scenarios AS jsonb),CAST(:assumptions AS jsonb)
          ) ON CONFLICT(snapshot_id,model_type,model_version) DO UPDATE SET
            fair_value_low=excluded.fair_value_low,fair_value_base=excluded.fair_value_base,
            fair_value_high=excluded.fair_value_high,buy_zone=excluded.buy_zone,
            hold_zone=excluded.hold_zone,sell_zone=excluded.sell_zone,
            scenarios=excluded.scenarios,assumptions=excluded.assumptions
        """), {"snapshot": row, "model_type": valuation["method"],
                 "model_version": valuation["modelVersion"],
                 "low": valuation["fairValueLow"], "base": base,
                 "high": valuation["fairValueHigh"], "buy_max": base * 0.8,
                 "sell_min": valuation["fairValueHigh"] * 1.15,
                 "scenarios": json.dumps(valuation["scenarios"], ensure_ascii=False),
                 "assumptions": json.dumps(valuation["assumptions"], ensure_ascii=False)})
    db.commit()
    return str(row)


def _period_end_from_letter(letter: dict) -> str | None:
    text = " ".join(str(letter.get(k) or "") for k in ("Title", "PublishDateTime")).translate(_DATE_DIGITS)
    current_year = jdatetime.date.fromgregorian(date=gregorian_date.today()).year
    match = re.search(rf"(?:{current_year - 1}|{current_year})[/\-]\d{{1,2}}[/\-]\d{{1,2}}", text)
    return match.group(0).replace("-", "/") if match else None


def _persist_letters(db: Session, company: models.Company, letters: list[dict]) -> int:
    """ذخیره idempotent فراداده گزارش‌های ۱۴۰۴ و ۱۴۰۵ برای مقایسه‌های بعدی."""
    inserted = 0
    for rec in letters:
        tracing_no = _safe_tracing_no(rec)
        if not tracing_no:
            continue
        period_end = _period_end_from_letter(rec)
        searchable = " ".join(str(rec.get(k) or "") for k in ("Title", "PublishDateTime")).translate(_DATE_DIGITS)
        current_year = jdatetime.date.fromgregorian(date=gregorian_date.today()).year
        if not any(str(year) in searchable for year in (current_year - 1, current_year)) and period_end is None:
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
    # Production is local-artifact only. Discovery is performed on the
    # operator workstation and imported before this endpoint is called.
    letters = _stored_codal_letters(db, symbol)

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
        tracing_no = _safe_tracing_no(rec)
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


def _stored_codal_letters(db: Session, symbol: str) -> list[dict]:
    """Rebuild Codal search records from our provenance-preserving local cache."""
    company = db.query(models.Company).filter(models.Company.symbol == symbol).first()
    if not company:
        return []
    reports = (
        db.query(models.FinancialReport)
        .filter(models.FinancialReport.company_id == company.id)
        .order_by(models.FinancialReport.publish_datetime.desc(), models.FinancialReport.id.desc())
        .limit(200)
        .all()
    )
    letters = []
    for report in reports:
        raw = dict(report.raw_json or {})
        raw.update({
            "TracingNo": raw.get("TracingNo") or report.tracing_no,
            "Title": raw.get("Title") or report.title,
            "CompanyName": raw.get("CompanyName") or company.company_name,
            "LetterCode": raw.get("LetterCode") or report.letter_code,
            "PublishDateTime": raw.get("PublishDateTime") or report.publish_datetime,
            "ExcelUrl": raw.get("ExcelUrl") or report.excel_url,
            "HasExcel": bool(raw.get("HasExcel") or report.excel_url),
            "Url": raw.get("Url") or report.detail_url,
        })
        letters.append(raw)
    return letters


def _stored_financial_report(db: Session, symbol: str, report_mode: str) -> tuple[dict, str, dict] | None:
    """Use a validated local v1 financial snapshot before making a Codal request."""
    audited_clause = "AND fp.audited" if report_mode == "audited" else ""
    annual_clause = "AND fp.length_months = 12" if report_mode == "audited" else ""
    rows = db.execute(text(f"""
      SELECT fp.id AS period_id,d.title,d.source_disclosure_id,d.published_date_jalali,d.scope,
             fp.end_date,fp.end_date_jalali,fp.length_months,fp.audited,
             dv.metadata->>'excel_url' AS excel_url,ff.fact_key,ff.normalized_value,
             ff.quality_status,ff.normalized_unit
      FROM symbol_aliases sa
      JOIN instruments i ON i.id=sa.instrument_id
      JOIN financial_periods fp ON fp.issuer_id=i.issuer_id
      JOIN financial_facts ff ON ff.period_id=fp.id
      JOIN disclosure_versions dv ON dv.id=fp.disclosure_version_id
      JOIN disclosures d ON d.id=dv.disclosure_id
      WHERE sa.symbol=:symbol AND sa.valid_to IS NULL {audited_clause} {annual_clause}
        AND ff.quality_status='VALID'
        -- A newer interim or subsidiary statement may contain only balance-sheet
        -- facts. Select a period that can actually support the core analysis.
        AND EXISTS (
          SELECT 1 FROM financial_facts revenue_fact
          WHERE revenue_fact.period_id=fp.id
            AND revenue_fact.fact_key='revenue'
            AND revenue_fact.quality_status='VALID'
            AND revenue_fact.normalized_value IS NOT NULL
        )
        AND EXISTS (
          SELECT 1 FROM financial_facts profit_fact
          WHERE profit_fact.period_id=fp.id
            AND profit_fact.fact_key='net_profit'
            AND profit_fact.quality_status='VALID'
            AND profit_fact.normalized_value IS NOT NULL
        )
      ORDER BY CASE WHEN fp.scope='consolidated' THEN 0 ELSE 1 END,
               fp.end_date DESC,fp.audited DESC,ff.fact_key
    """), {"symbol": symbol}).mappings().all()
    if not rows:
        return None
    metrics = {key: None for key in (
        "revenue", "cogs", "gross_profit", "operating_profit", "net_profit",
        "eps_basic", "total_assets", "total_liabilities", "total_equity",
        "operating_cash_flow",
    )}
    first = rows[0]
    for row in rows:
        # Codal often publishes the income statement and balance sheet as
        # separate disclosures. They may share a period end but have different
        # period ids; combine only an exact same-date, same-length, same-scope,
        # same-audit-status set so parent/subsidiary facts never mix.
        same_financial_period = (
            row["end_date"] == first["end_date"]
            and row["length_months"] == first["length_months"]
            and row["scope"] == first["scope"]
            and row["audited"] == first["audited"]
        )
        if not same_financial_period:
            continue
        if row["fact_key"] in metrics and row["normalized_value"] is not None:
            metrics[row["fact_key"]] = float(row["normalized_value"])
    if metrics["revenue"] is None or metrics["net_profit"] is None:
        return None
    candidate = {
        "Title": first["title"], "TracingNo": first["source_disclosure_id"],
        "PublishDateTime": first["published_date_jalali"], "ExcelUrl": first["excel_url"],
        "HasExcel": bool(first["excel_url"]), "scope": first["scope"],
        "_period_id": str(first["period_id"]), "_end_date": first["end_date"],
        "_end_date_jalali": first["end_date_jalali"],
        "_length_months": first["length_months"],
    }
    return candidate, str(first["excel_url"] or ""), {
        "metrics": metrics,
        "found_items": sorted(key for key, value in metrics.items() if value is not None),
        "missing_items": sorted(key for key, value in metrics.items() if value is None),
        "source": "local_codal_financial_facts",
    }


def _stored_period_comparison(db: Session, symbol: str, candidate: dict, parsed: dict):
    """Compare the selected persisted period with the closest earlier same-length period."""
    if not candidate.get("_end_date") or not candidate.get("_length_months"):
        return None, "گزارش دوره هم‌طول قبلی در داده‌های واردشده پیدا نشد."
    previous = db.execute(text("""
      SELECT fp.id AS period_id,d.source_disclosure_id
      FROM symbol_aliases sa
      JOIN instruments i ON i.id=sa.instrument_id
      JOIN financial_periods fp ON fp.issuer_id=i.issuer_id
      JOIN disclosure_versions dv ON dv.id=fp.disclosure_version_id
      JOIN disclosures d ON d.id=dv.disclosure_id
      WHERE sa.symbol=:symbol AND sa.valid_to IS NULL
        AND fp.end_date < :end_date AND fp.length_months=:length
        AND fp.scope=:scope
        AND EXISTS (SELECT 1 FROM financial_facts ff WHERE ff.period_id=fp.id AND ff.quality_status='VALID' AND ff.fact_key='revenue')
      ORDER BY fp.end_date DESC,fp.audited DESC
      LIMIT 1
    """), {"symbol": symbol, "end_date": candidate["_end_date"],
             "length": candidate["_length_months"], "scope": candidate.get("scope") or "unknown"}).mappings().first()
    if not previous:
        return None, "گزارش دوره هم‌طول قبلی در داده‌های واردشده پیدا نشد."
    values = dict(db.execute(text("""
      SELECT fact_key,normalized_value FROM financial_facts
      WHERE period_id=:period AND quality_status='VALID' AND fact_key IN ('revenue','net_profit')
    """), {"period": previous["period_id"]}).all())
    current_revenue=parsed["metrics"].get("revenue"); previous_revenue=values.get("revenue")
    current_profit=parsed["metrics"].get("net_profit"); previous_profit=values.get("net_profit")
    label=period_label_from_title(str(candidate.get("Title") or ""))
    return {
      "period_label": label, "current_report": candidate.get("TracingNo"),
      "previous_report": previous["source_disclosure_id"],
      "current_revenue": current_revenue, "previous_revenue": float(previous_revenue) if previous_revenue is not None else None,
      "revenue_growth_percent": ((current_revenue / float(previous_revenue)) - 1) * 100 if current_revenue is not None and previous_revenue not in (None,0) else None,
      "current_net_profit": current_profit, "previous_net_profit": float(previous_profit) if previous_profit is not None else None,
      "net_profit_growth_percent": ((current_profit / float(previous_profit)) - 1) * 100 if current_profit is not None and previous_profit not in (None,0) else None,
      "source": "صورت‌های مالی رسمی کدال (داده واردشده)"
    }, None


def _stored_analysis_context(db: Session, symbol: str) -> dict:
    """Return sourced context that can qualify a categorical decision."""
    row = db.execute(text("""
      WITH target AS (
        SELECT i.id AS instrument_id,i.issuer_id
        FROM symbol_aliases sa JOIN instruments i ON i.id=sa.instrument_id
        WHERE sa.symbol=:symbol AND sa.valid_to IS NULL LIMIT 1
      ), prices AS (
        SELECT DISTINCT ON (dp.trading_date)
          dp.trading_date,COALESCE(dp.adjusted_close,dp.close) AS price,
          dp.close AS raw_close,dp.shares_outstanding
        FROM daily_prices dp,target t
        WHERE dp.instrument_id=t.instrument_id AND dp.quality_status='VALID'
        ORDER BY dp.trading_date,dp.retrieved_at DESC
      ), latest AS (SELECT * FROM prices ORDER BY trading_date DESC LIMIT 1),
      share_series AS (
        SELECT trading_date,shares_outstanding,
          lag(shares_outstanding) OVER(ORDER BY trading_date) previous_shares
        FROM prices WHERE shares_outstanding>0
      ), latest_share_change AS (
        SELECT trading_date FROM share_series
        WHERE previous_shares>0 AND abs(shares_outstanding/previous_shares-1)>=0.01
        ORDER BY trading_date DESC LIMIT 1
      )
      SELECT
        (SELECT count(DISTINCT (fp.end_date,fp.length_months,fp.scope))
         FROM financial_periods fp,target t WHERE fp.issuer_id=t.issuer_id
           AND EXISTS(SELECT 1 FROM financial_facts ff WHERE ff.period_id=fp.id AND ff.quality_status='VALID')) AS financial_periods,
        (SELECT count(*) FROM disclosures d,target t WHERE d.issuer_id=t.issuer_id
           AND (d.letter_code IN ('ن-۳۰','ن-30') OR d.title LIKE '%گزارش فعالیت ماهانه%')) AS monthly_disclosures,
        (SELECT count(*) FROM corporate_actions ca,target t WHERE ca.instrument_id=t.instrument_id) AS corporate_actions,
        (SELECT count(*) FROM corporate_actions ca,target t,latest_share_change sc
          WHERE ca.instrument_id=t.instrument_id
            AND ca.effective_date BETWEEN sc.trading_date-INTERVAL '120 days' AND sc.trading_date+INTERVAL '120 days') AS matched_corporate_actions,
        (SELECT count(*) FROM prices) AS price_observations,
        (SELECT trading_date FROM latest) AS latest_price_date,
        (SELECT price FROM latest) AS latest_price,
        (SELECT raw_close FROM latest) AS latest_raw_close,
        (SELECT shares_outstanding FROM prices WHERE shares_outstanding>0 ORDER BY trading_date LIMIT 1) AS earliest_shares,
        (SELECT shares_outstanding FROM prices WHERE shares_outstanding>0 ORDER BY trading_date DESC LIMIT 1) AS latest_shares,
        (SELECT trading_date FROM latest_share_change) AS shares_change_date,
        (SELECT p.price FROM prices p,latest WHERE p.trading_date<=latest.trading_date-INTERVAL '90 days' ORDER BY p.trading_date DESC LIMIT 1) AS price_90d,
        (SELECT p.price FROM prices p,latest WHERE p.trading_date<=latest.trading_date-INTERVAL '365 days' ORDER BY p.trading_date DESC LIMIT 1) AS price_365d
    """), {"symbol": symbol}).mappings().first()
    if not row:
        return {}
    result = dict(row)
    latest = float(result["latest_price"]) if result.get("latest_price") is not None else None
    for days in (90, 365):
        previous = result.pop(f"price_{days}d", None)
        result[f"price_return_{days}d_percent"] = (
            round((latest / float(previous) - 1) * 100, 2)
            if latest is not None and previous not in (None, 0) else None
        )
    if result.get("latest_price") is not None:
        result["latest_price"] = latest
    raw_close = result.pop("latest_raw_close", None)
    result["price_adjustment_gap_percent"] = (
        round((float(raw_close) / latest - 1) * 100, 2)
        if latest not in (None, 0) and raw_close is not None else None
    )
    earliest_shares = result.pop("earliest_shares", None)
    latest_shares = result.pop("latest_shares", None)
    result["shares_change_percent"] = (
        round((float(latest_shares) / float(earliest_shares) - 1) * 100, 2)
        if earliest_shares not in (None, 0) and latest_shares is not None else None
    )
    result["capital_action_data_gap"] = bool(
        result["shares_change_percent"] not in (None, 0)
        and abs(result["shares_change_percent"]) >= 1
        and not result.get("matched_corporate_actions")
    )
    if result.get("shares_change_date") is not None:
        result["shares_change_date"] = result["shares_change_date"].isoformat()
    if result.get("latest_price_date") is not None:
        result["latest_price_date"] = result["latest_price_date"].isoformat()
    return result


def _stored_monthly_signals(db: Session, symbol: str) -> dict:
    """Compare only explicitly labelled Codal monthly sales cells."""
    rows = db.execute(text("""
      SELECT period_end_jalali,fact_key,max(value) AS value
      FROM codalpy_records
      WHERE symbol=:symbol AND output_type='monthly_activity'
        AND fact_key IN ('monthly_sales_current','monthly_sales_ytd')
        AND period_end_jalali IS NOT NULL
      GROUP BY period_end_jalali,fact_key
      ORDER BY period_end_jalali DESC
    """), {"symbol": symbol}).mappings().all()
    by_key = {}
    for row in rows:
        try:
            date_text = str(row["period_end_jalali"]).translate(_DATE_DIGITS).replace("-", "/")
            year, month, _ = [int(part) for part in date_text.split("/")[:3]]
            by_key.setdefault(row["fact_key"], []).append((year, month, float(row["value"]), date_text))
        except (TypeError, ValueError):
            continue

    def comparison(key: str) -> dict:
        values = by_key.get(key) or []
        if not values:
            return {}
        current = values[0]
        previous = next((value for value in values[1:] if value[0] == current[0] - 1 and value[1] == current[1]), None)
        return {
            "current": current[2], "currentPeriod": current[3],
            "previous": previous[2] if previous else None,
            "previousPeriod": previous[3] if previous else None,
            "growthPercent": round((current[2] / previous[2] - 1) * 100, 2)
            if previous and previous[2] != 0 else None,
        }

    monthly = comparison("monthly_sales_current")
    ytd = comparison("monthly_sales_ytd")
    return {
        "available": bool(monthly.get("growthPercent") is not None or ytd.get("growthPercent") is not None),
        "monthlySales": monthly, "ytdSales": ytd,
        "source": "سلول‌های صریح جمع مبلغ فروش در گزارش فعالیت ماهانه کدال",
    }


def _stored_ttm(db: Session, symbol: str, candidate: dict, parsed: dict):
    """Build TTM flows without mixing scope, units, or incompatible periods."""
    length = candidate.get("_length_months")
    if length == 12:
        return {
            "metrics": {key: parsed["metrics"].get(key) for key in FLOW_FACT_KEYS},
            "method": "latest_annual",
            "current_report": candidate.get("TracingNo"),
            "source": "صورت‌های مالی رسمی کدال (داده واردشده)",
        }, None
    if not length or not candidate.get("_end_date"):
        return None, "اجزای سازگار برای محاسبه دوازده‌ماهه اخیر موجود نیست."

    periods = db.execute(text("""
      SELECT fp.id,fp.length_months,fp.end_date,d.source_disclosure_id
      FROM symbol_aliases sa
      JOIN instruments i ON i.id=sa.instrument_id
      JOIN financial_periods fp ON fp.issuer_id=i.issuer_id
      JOIN disclosure_versions dv ON dv.id=fp.disclosure_version_id
      JOIN disclosures d ON d.id=dv.disclosure_id
      WHERE sa.symbol=:symbol AND sa.valid_to IS NULL AND fp.scope=:scope
        AND fp.end_date < :end_date AND fp.length_months IN (12,:length)
      ORDER BY fp.end_date DESC,fp.audited DESC
    """), {"symbol": symbol, "scope": candidate.get("scope") or "unknown",
             "end_date": candidate["_end_date"], "length": length}).mappings().all()
    annual = next((row for row in periods if row["length_months"] == 12), None)
    if not annual:
        return None, "گزارش سالانه سازگار برای محاسبه دوازده‌ماهه اخیر موجود نیست."
    prior = next((row for row in periods if row["length_months"] == length and row["end_date"] < annual["end_date"]), None)
    if not prior:
        return None, "دوره هم‌طول سال قبل برای محاسبه دوازده‌ماهه اخیر موجود نیست."

    def period_flows(period_id):
        return dict(db.execute(text("""
          SELECT fact_key,normalized_value FROM financial_facts
          WHERE period_id=:period AND quality_status='VALID'
            AND fact_key IN ('revenue','cogs','gross_profit','operating_profit','net_profit','operating_cash_flow')
        """), {"period": period_id}).all())

    metrics = build_ttm_metrics(parsed["metrics"], period_flows(annual["id"]), period_flows(prior["id"]))
    return {
        "metrics": metrics, "method": "annual_plus_current_ytd_minus_prior_ytd",
        "current_report": candidate.get("TracingNo"),
        "annual_report": annual["source_disclosure_id"],
        "prior_comparable_report": prior["source_disclosure_id"],
        "missing_items": sorted(key for key, value in metrics.items() if value is None),
        "source": "صورت‌های مالی رسمی کدال (داده واردشده)",
    }, None


def _stored_live_snapshot(db: Session, symbol: str) -> dict | None:
    """Use the latest real, persisted BrsApi observation when the provider is down."""
    company = db.query(models.Company).filter(models.Company.symbol == symbol).first()
    if not company:
        return None
    snapshot = (
        db.query(models.PriceSnapshot)
        .filter(models.PriceSnapshot.company_id == company.id)
        .order_by(models.PriceSnapshot.fetched_at.desc(), models.PriceSnapshot.id.desc())
        .first()
    )
    if not snapshot:
        return None
    raw = dict(snapshot.raw_json or {})
    mapped = tsetmc_service._map_symbol_record(raw) if raw else {}
    mapped.update({
        "symbol": symbol,
        "full_name": mapped.get("full_name") or company.company_name,
        "isin": mapped.get("isin") or company.ins_code,
        "market_category": mapped.get("market_category") or company.industry,
        "last_price": snapshot.price if snapshot.price is not None else mapped.get("last_price"),
        "closing_price": snapshot.close_price if snapshot.close_price is not None else mapped.get("closing_price"),
        "eps": snapshot.eps if snapshot.eps is not None else mapped.get("eps"),
        "pe_ratio": snapshot.pe_ratio if snapshot.pe_ratio is not None else mapped.get("pe_ratio"),
        "market_cap": snapshot.market_cap if snapshot.market_cap is not None else mapped.get("market_cap"),
        "_fallback": True,
    })
    return mapped


def _is_financial_statement(letter: dict) -> bool:
    title = str(letter.get("Title") or "").replace("\u200c", " ")
    code = str(letter.get("LetterCode") or "").replace("۰", "0").replace("۱", "1")
    return code in {"ن-10", "ن-۱۰"} or "صورت های مالی" in title.replace("‌", " ")


def _financial_candidates(letters: list[dict], report_mode: str) -> list[dict]:
    candidates = [letter for letter in letters if letter.get("HasExcel") and _is_financial_statement(letter)]
    if report_mode == "latest_codal":
        return candidates
    return [
        letter for letter in candidates
        if "حسابرسی شده" in str(letter.get("Title") or "")
        and "حسابرسی نشده" not in str(letter.get("Title") or "")
        and ("۱۲ ماهه" in str(letter.get("Title") or "") or "سال مالی" in str(letter.get("Title") or ""))
    ]


def _related_codal_disclosures(letters: list[dict], candidate: dict) -> list[dict]:
    """Return nearby explanation/amendment notices as context, never as metrics."""
    published = str(candidate.get("PublishDateTime") or "")
    related = []
    for letter in letters:
        title = str(letter.get("Title") or "")
        if letter is candidate or not ("توضیحات" in title or "اصلاحیه" in title):
            continue
        related.append({
            "title": title,
            "publishedAt": letter.get("PublishDateTime"),
            "tracingNo": letter.get("TracingNo"),
            "detailUrl": letter.get("Url") or letter.get("URL") or letter.get("DetailUrl"),
            "nearby": bool(published and str(letter.get("PublishDateTime") or "") <= published),
        })
    return related[:8]


def _excel_url(letter: dict) -> str:
    value = str(letter.get("ExcelUrl") or "")
    return f"https://excel.codal.ir{value}" if value.startswith("/") else value


def _parse_first_usable_report(candidates: list[dict]) -> tuple[dict, str, dict]:
    errors = []
    for candidate in candidates:
        excel_url = _excel_url(candidate)
        try:
            parsed = codal_excel_parser.fetch_and_parse(excel_url)
        except (codal_excel_parser.CodalExcelDownloadError, codal_excel_parser.CodalExcelParseError) as exc:
            errors.append(str(exc))
            continue
        metrics = parsed.get("metrics") or {}
        if metrics.get("revenue") is not None and metrics.get("net_profit") is not None:
            return candidate, excel_url, parsed
        errors.append(f"گزارش {candidate.get('TracingNo')} فاقد اقلام اصلی صورت مالی بود.")
    detail = errors[-1] if errors else "هیچ فایل صورت مالی قابل استفاده‌ای پیدا نشد."
    raise HTTPException(status_code=422, detail=detail)


def _build_period_comparison(
    candidate: dict, parsed: dict, letters: list[dict]
) -> tuple[dict | None, str | None]:
    """گزارش هم‌طول قبلی برای رشد واقعی؛ شکست این بخش تحلیل اصلی را متوقف نمی‌کند."""
    period_label = period_label_from_title(str(candidate.get("Title") or ""))
    previous_candidates = [
        rec for rec in _financial_candidates(letters, "latest_codal")
        if rec is not candidate and period_label is not None and period_label in str(rec.get("Title") or "")
    ]
    return build_period_comparison(
        candidate, parsed, previous_candidates, _parse_first_usable_report
    )


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
    if live_data is None:
        live_data = _stored_live_snapshot(db, symbol)

    if report_mode not in {"audited", "latest_codal"}:
        raise HTTPException(status_code=400, detail="report_mode نامعتبر است.")

    # Production is artifact-only: Codal discovery/download is local-only.
    # Both modes use persisted, previously imported data and never call Codal.
    local_report = _stored_financial_report(db, symbol, report_mode)
    letters = _stored_codal_letters(db, symbol)
    if not local_report:
        raise HTTPException(status_code=404, detail=f"برای نماد «{symbol}» گزارش واردشده‌ای موجود نیست.")
    candidate, excel_url, parsed = local_report

    comparison, comparison_unavailable_reason = _stored_period_comparison(db, symbol, candidate, parsed)
    ttm, ttm_unavailable_reason = _stored_ttm(db, symbol, candidate, parsed)
    related_disclosures = _related_codal_disclosures(letters, candidate)

    # ۵. محاسبه‌ی نسبت‌ها
    live_pe = live_data.get("pe_ratio") if live_data else None
    company = db.query(models.Company).filter(models.Company.symbol == symbol).first()
    industry_category = live_data.get("market_category") if live_data else None
    # TSETMC/BrsApi can return a visually different spelling of the industry
    # (for example a zero-width joiner). Prefer the official company industry
    # when the provider value cannot be mapped to a supported model family.
    if model_family(industry_category) == "unclassified" and company and company.industry:
        industry_category = company.industry
        if live_data is not None:
            live_data["market_category"] = industry_category
    ratio_metrics = dict(parsed["metrics"])
    if ttm:
        ratio_metrics.update({key: value for key, value in ttm["metrics"].items() if value is not None})
    ratios = ratio_engine.compute_ratios(ratio_metrics, live_pe_ratio=live_pe)
    health = ratio_engine.evaluate_health_status(ratios, industry_category=industry_category)

    # ۶. ذخیره در دیتابیس
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
        models.FinancialReport.tracing_no == _safe_tracing_no(candidate)
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

    analysis_context = _stored_analysis_context(db, symbol)
    monthly_signals = _stored_monthly_signals(db, symbol)
    analysis_context["monthly_signals_available"] = monthly_signals["available"]
    analysis_context["monthlySignals"] = monthly_signals

    return {
        "success": True,
        "symbol": symbol,
        "company_name": candidate.get("CompanyName"),
        "report_used": {
            "title": candidate.get("Title"),
            "tracing_no": candidate.get("TracingNo"),
            "publish_datetime": candidate.get("PublishDateTime"),
            "period_end": candidate.get("_end_date_jalali") or candidate.get("_end_date"),
            "period_length_months": candidate.get("_length_months"),
            "excel_url": excel_url,
        },
        "live_price": live_data,
        "live_price_error": live_error,
        "financial_metrics": parsed["metrics"],
        "financial_metrics_found": parsed["found_items"],
        "financial_metrics_missing": parsed["missing_items"],
        "period_comparison": comparison,
        "period_comparison_unavailable_reason": comparison_unavailable_reason,
        "analysis_context": analysis_context,
        "monthly_activity": monthly_signals,
        "ttm": ttm,
        "ttm_unavailable_reason": ttm_unavailable_reason,
        "related_codal_disclosures": related_disclosures,
        "ratios": ratios,
        "health": health,
        "history_sync": {
            "years": [jdatetime.date.fromgregorian(date=gregorian_date.today()).year - 1, jdatetime.date.fromgregorian(date=gregorian_date.today()).year],
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
    settings = dict(db.execute(text("""
      SELECT key,value FROM system_settings
      WHERE key IN ('bank_deposit_rate_percent','inflation_rate_percent')
    """)).all())
    raw["references"] = {
        "bankDepositRate": float(settings["bank_deposit_rate_percent"])
        if settings.get("bank_deposit_rate_percent") is not None else None,
        "inflationRate": float(settings["inflation_rate_percent"])
        if settings.get("inflation_rate_percent") is not None else None,
    }
    payload = build_snapshot_payload(raw, request.report_mode)
    payload["analysisId"] = _persist_v2_snapshot(db, raw, payload)
    # Persist the snapshot before returning so the public symbol endpoint can
    # immediately observe successful analysis requests.
    db.commit()
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
