"""
تنظیمات مرکزی پروژه. همه‌چیز از فایل .env خونده می‌شه تا رمزها
داخل کد هاردکد نشن.
"""
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "boursnegar")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "boursnegar_db")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# فاصله‌ی بین درخواست‌های پیاپی به کدال/تستمسی (ثانیه) - احترام به سرورهای مقصد
CODAL_RATE_LIMIT_SECONDS = float(os.getenv("CODAL_RATE_LIMIT_SECONDS", "1.5"))
TSETMC_TIMEOUT_SECONDS = float(os.getenv("TSETMC_TIMEOUT_SECONDS", "8"))
CODAL_TIMEOUT_SECONDS = float(os.getenv("CODAL_TIMEOUT_SECONDS", "10"))

HTTP_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# کلید API سرویس BrsApi.ir - جایگزین اتصال مستقیم به cdn.tsetmc.com
# (که از این هاست بلاک بود). محدودیت پیش‌فرض: ۳۰۰ درخواست هر ۵ دقیقه.
BRSAPI_KEY = os.getenv("BRSAPI_KEY", "")
