from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency برای FastAPI - یک سشن دیتابیس می‌ده و بعد از درخواست می‌بنده."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
