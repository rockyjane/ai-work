"""資料庫連線設定。

預設用 SQLite（零設定即可跑），把 .env 的 DATABASE_URL 改成 mysql+pymysql://...
就會自動切換到你 Docker 裡的 MySQL，程式碼完全不用動。
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock.db")

# SQLite 在多執行緒下需要這個參數；MySQL 不需要
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI 依賴注入用：每個請求拿一個 session，結束自動關閉。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
