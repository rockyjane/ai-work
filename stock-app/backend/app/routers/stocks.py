"""股票相關 API：搜尋、個股資訊、K線+技術指標、漲跌幅排行。"""
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Stock, DailyPrice
from ..indicators import compute_indicators

router = APIRouter(tags=["stocks"])


@router.get("/stocks")
def list_stocks(q: str = "", db: Session = Depends(get_db)):
    """搜尋股票（依代號或名稱）。q 留空回傳前 50 檔。"""
    query = db.query(Stock)
    if q:
        query = query.filter(or_(Stock.stock_id.contains(q), Stock.name.contains(q)))
    rows = query.limit(50).all()
    return [
        {"stock_id": s.stock_id, "name": s.name, "industry": s.industry, "market": s.market}
        for s in rows
    ]


@router.get("/stocks/{stock_id}")
def get_stock(stock_id: str, db: Session = Depends(get_db)):
    s = db.query(Stock).filter(Stock.stock_id == stock_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="找不到這檔股票")
    return {"stock_id": s.stock_id, "name": s.name, "industry": s.industry, "market": s.market}


@router.get("/stocks/{stock_id}/prices")
def get_prices(
    stock_id: str,
    indicators: str = Query("ma,rsi,macd,kd", description="逗號分隔：ma,rsi,macd,kd"),
    limit: int = Query(250, description="最近幾個交易日"),
    db: Session = Depends(get_db),
):
    """回傳 K 線、成交量與技術指標，格式直接給 ECharts 用。"""
    rows = (
        db.query(DailyPrice)
        .filter(DailyPrice.stock_id == stock_id)
        .order_by(DailyPrice.date.asc())
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="這檔股票還沒有行情資料，請先執行 seed.py 匯入")

    data = [{
        "date": r.date.isoformat(),
        "open": float(r.open), "high": float(r.high),
        "low": float(r.low), "close": float(r.close),
        "volume": int(r.volume),
    } for r in rows]
    df = pd.DataFrame(data)

    which = [x.strip() for x in indicators.split(",") if x.strip()]
    ind = compute_indicators(df, which)

    # 只取最近 limit 筆（指標已用完整資料算好，避免邊界失真後才裁切）
    if limit and len(df) > limit:
        df = df.tail(limit).reset_index(drop=True)
        ind = {k: v[-limit:] for k, v in ind.items()}

    return {
        "stock_id": stock_id,
        "dates": df["date"].tolist(),
        # ECharts candlestick 的順序是 [open, close, low, high]
        "kline": [[row.open, row.close, row.low, row.high] for row in df.itertuples()],
        "volumes": df["volume"].tolist(),
        "indicators": ind,
    }


@router.get("/rankings")
def rankings(top: int = 10, db: Session = Depends(get_db)):
    """以最近兩個交易日計算漲跌幅，回傳上漲/下跌排行。"""
    results = []
    for s in db.query(Stock).all():
        last2 = (
            db.query(DailyPrice)
            .filter(DailyPrice.stock_id == s.stock_id)
            .order_by(DailyPrice.date.desc())
            .limit(2)
            .all()
        )
        if len(last2) < 2:
            continue
        cur, prev = last2[0], last2[1]
        prev_close = float(prev.close)
        if prev_close == 0:
            continue
        change = float(cur.close) - prev_close
        pct = round(change / prev_close * 100, 2)
        results.append({
            "stock_id": s.stock_id, "name": s.name,
            "close": float(cur.close), "change": round(change, 2), "pct": pct,
        })
    results.sort(key=lambda x: x["pct"], reverse=True)
    return {"gainers": results[:top], "losers": results[-top:][::-1]}
