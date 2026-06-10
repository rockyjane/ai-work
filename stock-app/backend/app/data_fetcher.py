"""從 FinMind 抓台股資料，寫進資料庫。

FinMind 文件：https://finmindtrade.com
taiwan_stock_daily 回傳欄位：date, stock_id, Trading_Volume, Trading_money,
open, max, min, close, spread, Trading_turnover
（注意：high=max、low=min、volume=Trading_Volume）
"""
import os
import pandas as pd
from FinMind.data import DataLoader
from sqlalchemy.orm import Session

from .models import Stock, DailyPrice


def _loader() -> DataLoader:
    api = DataLoader()
    token = os.getenv("FINMIND_TOKEN")
    if token:
        api.login_by_token(api_token=token)
    return api


def fetch_daily(stock_id: str, start_date: str, end_date: str | None = None) -> pd.DataFrame:
    """抓單一股票日線，回傳整理好的 DataFrame。"""
    api = _loader()
    df = api.taiwan_stock_daily(
        stock_id=stock_id, start_date=start_date, end_date=end_date,
    )
    if df is None or df.empty:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
    df = df.rename(columns={"max": "high", "min": "low", "Trading_Volume": "volume"})
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df[["date", "open", "high", "low", "close", "volume"]]


def fetch_stock_info() -> pd.DataFrame:
    """抓全台股基本資料（代號、名稱、產業、市場別）。"""
    api = _loader()
    df = api.taiwan_stock_info()
    return df


def upsert_prices(db: Session, stock_id: str, df: pd.DataFrame) -> int:
    """把日線寫進 DB，已存在的日期跳過。回傳新增筆數。"""
    if df.empty:
        return 0
    existing = {
        d[0] for d in db.query(DailyPrice.date).filter(DailyPrice.stock_id == stock_id).all()
    }
    rows = []
    for _, r in df.iterrows():
        if r["date"] in existing:
            continue
        rows.append(DailyPrice(
            stock_id=stock_id,
            date=r["date"],
            open=r["open"], high=r["high"], low=r["low"], close=r["close"],
            volume=int(r["volume"]),
        ))
    if rows:
        db.bulk_save_objects(rows)
        db.commit()
    return len(rows)


def upsert_stock(db: Session, stock_id: str, name: str, industry: str = "", market: str = "") -> None:
    """新增或更新一檔股票的基本資料。"""
    s = db.query(Stock).filter(Stock.stock_id == stock_id).first()
    if s is None:
        s = Stock(stock_id=stock_id, name=name, industry=industry, market=market)
        db.add(s)
    else:
        s.name = name or s.name
        s.industry = industry or s.industry
        s.market = market or s.market
    db.commit()
