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

from .models import Stock, DailyPrice, Valuation, Financial


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


def fetch_per_pbr(stock_id: str, start_date: str, end_date: str | None = None) -> pd.DataFrame:
    """抓單一股票的每日評價指標（本益比/淨值比/殖利率），回傳整理好的 DataFrame。

    FinMind taiwan_stock_per_pbr 回傳欄位：date, stock_id, dividend_yield, PER, PBR。
    這裡把大寫 PER/PBR 統一轉成小寫欄位，對齊 models.Valuation。
    """
    api = _loader()
    df = api.taiwan_stock_per_pbr(
        stock_id=stock_id, start_date=start_date, end_date=end_date,
    )
    if df is None or df.empty:
        return pd.DataFrame(columns=["date", "per", "pbr", "dividend_yield"])
    df = df.rename(columns={"PER": "per", "PBR": "pbr"})
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df[["date", "per", "pbr", "dividend_yield"]]


def fetch_financials(stock_id: str, start_date: str, end_date: str | None = None) -> pd.DataFrame:
    """抓單一股票的季度財報，目前只取 EPS，回傳整理好的 DataFrame（date, eps）。

    FinMind taiwan_stock_financial_statement 是「長格式」：每個財報項目一列，
    用 type 欄標示（EPS, Revenue, GrossProfit...），value 欄是數值。
    這裡只篩出 type=='EPS' 的列，轉成一行一季的 (date, eps)。
    """
    api = _loader()
    df = api.taiwan_stock_financial_statement(
        stock_id=stock_id, start_date=start_date, end_date=end_date,
    )
    if df is None or df.empty:
        return pd.DataFrame(columns=["date", "eps"])
    eps = df[df["type"] == "EPS"][["date", "value"]].copy()
    if eps.empty:
        return pd.DataFrame(columns=["date", "eps"])
    eps = eps.rename(columns={"value": "eps"})
    eps["date"] = pd.to_datetime(eps["date"]).dt.date
    return eps[["date", "eps"]]


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


def upsert_valuation(db: Session, stock_id: str, df: pd.DataFrame) -> int:
    """把評價指標寫進 DB，已存在的日期跳過。回傳新增筆數。"""
    if df.empty:
        return 0
    existing = {
        d[0] for d in db.query(Valuation.date).filter(Valuation.stock_id == stock_id).all()
    }
    rows = []
    for _, r in df.iterrows():
        if r["date"] in existing:
            continue
        rows.append(Valuation(
            stock_id=stock_id,
            date=r["date"],
            per=r["per"], pbr=r["pbr"], dividend_yield=r["dividend_yield"],
        ))
    if rows:
        db.bulk_save_objects(rows)
        db.commit()
    return len(rows)


def upsert_financials(db: Session, stock_id: str, df: pd.DataFrame) -> int:
    """把季度財報（EPS）寫進 DB，已存在的季度跳過。回傳新增筆數。"""
    if df.empty:
        return 0
    existing = {
        d[0] for d in db.query(Financial.date).filter(Financial.stock_id == stock_id).all()
    }
    rows = []
    for _, r in df.iterrows():
        if r["date"] in existing:
            continue
        rows.append(Financial(stock_id=stock_id, date=r["date"], eps=r["eps"]))
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
