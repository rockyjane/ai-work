"""資料表定義（ORM）。對應文檔 §5 的資料庫設計。"""
from sqlalchemy import (
    Column, String, Integer, BigInteger, Numeric, Date, DateTime,
    UniqueConstraint, func,
)
from .database import Base

# 在 SQLite 用 INTEGER（才會自動遞增 rowid），在 MySQL 用 BIGINT
PK = BigInteger().with_variant(Integer, "sqlite")


class Stock(Base):
    """股票基本資料"""
    __tablename__ = "stocks"

    stock_id = Column(String(10), primary_key=True)   # 例如 2330
    name = Column(String(50))                          # 台積電
    industry = Column(String(50))                      # 半導體業
    market = Column(String(10))                        # 上市 / 上櫃


class DailyPrice(Base):
    """每日 K 線（日線）"""
    __tablename__ = "daily_prices"

    id = Column(PK, primary_key=True, autoincrement=True)
    stock_id = Column(String(10), index=True)
    date = Column(Date, index=True)
    open = Column(Numeric(10, 2))
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
    close = Column(Numeric(10, 2))
    volume = Column(BigInteger)

    # 同一檔股票同一天只會有一筆，避免重複匯入
    __table_args__ = (UniqueConstraint("stock_id", "date", name="uniq_stock_date"),)


class Watchlist(Base):
    """自選股"""
    __tablename__ = "watchlist"

    id = Column(PK, primary_key=True, autoincrement=True)
    stock_id = Column(String(10))
    note = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())
