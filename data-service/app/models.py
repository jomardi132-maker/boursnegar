from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(255))
    ins_code = Column(String(50))  # کد شناسایی داخلی تستمسی
    isic_code = Column(String(20))
    industry = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    reports = relationship("FinancialReport", back_populates="company")
    price_snapshots = relationship("PriceSnapshot", back_populates="company")
    ratios = relationship("FinancialRatio", back_populates="company")


class FinancialReport(Base):
    __tablename__ = "financial_reports"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    tracing_no = Column(String(50), unique=True, index=True)
    title = Column(Text)
    letter_code = Column(String(50))
    period_end_date = Column(String(20))  # تاریخ شمسی، مثلا 1404/12/29
    publish_datetime = Column(String(50))
    is_audited = Column(Boolean, default=False)
    excel_url = Column(Text)
    detail_url = Column(Text)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    raw_json = Column(JSON)

    company = relationship("Company", back_populates="reports")
    line_items = relationship("FinancialLineItem", back_populates="report")


class FinancialLineItem(Base):
    """
    آیتم‌های خام استخراج‌شده از صورت مالی (بعد از پارس فایل اکسل کدال).
    مرحله‌ی بعدی که هنوز پیاده‌سازی نکردیم پر می‌شه.
    """
    __tablename__ = "financial_line_items"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("financial_reports.id"), nullable=False)
    statement_type = Column(String(30))  # balance_sheet | income_statement | cash_flow
    item_name = Column(Text)
    item_value = Column(Float)
    unit = Column(String(30), default="IRR_million")

    report = relationship("FinancialReport", back_populates="line_items")


class PriceSnapshot(Base):
    """
    عکس لحظه‌ای قیمت از تستمسی - هر بار که کاربر سرچ می‌کنه یا کرون اجرا می‌شه، یک رکورد اضافه می‌شه.
    این تاریخچه بعدا برای نمودار قیمت هم به‌کار میاد.
    """
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    price = Column(Float)
    close_price = Column(Float)
    eps = Column(Float)
    pe_ratio = Column(Float)
    sector_pe = Column(Float)
    market_cap = Column(Float)
    min_week = Column(Float)
    max_week = Column(Float)
    min_year = Column(Float)
    max_year = Column(Float)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    raw_json = Column(JSON)

    company = relationship("Company", back_populates="price_snapshots")


class FinancialRatio(Base):
    """نسبت‌های مالی محاسبه‌شده (نه هاردکد!) - از روی line_items واقعی."""
    __tablename__ = "financial_ratios"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("financial_reports.id"))
    period_end_date = Column(String(20))
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    eps = Column(Float)
    roe = Column(Float)
    roa = Column(Float)
    current_ratio = Column(Float)
    debt_to_equity = Column(Float)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="ratios")
