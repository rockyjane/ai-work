"""股票相關 API：搜尋、個股資訊、K線+技術指標、漲跌幅排行。"""
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Stock, DailyPrice, Valuation, Financial, Revenue
from ..schemas import ValuationOut, FinancialOut, RevenueOut
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


@router.get("/stocks/{stock_id}/valuation", response_model=list[ValuationOut])
def get_valuation(
    stock_id: str,
    limit: int = Query(60, description="最近幾個交易日的評價指標"),
    db: Session = Depends(get_db),
):
    """回傳個股每日評價指標（本益比 PER / 淨值比 PBR / 殖利率），由新到舊。"""
    rows = (
        db.query(Valuation)
        .filter(Valuation.stock_id == stock_id)
        .order_by(Valuation.date.desc())
        .limit(limit)
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="這檔股票還沒有評價資料，請先執行 seed.py 匯入")
    return [
        ValuationOut(
            date=r.date.isoformat(),
            per=float(r.per) if r.per is not None else None,
            pbr=float(r.pbr) if r.pbr is not None else None,
            dividend_yield=float(r.dividend_yield) if r.dividend_yield is not None else None,
        )
        for r in rows
    ]


@router.get("/stocks/{stock_id}/financials", response_model=list[FinancialOut])
def get_financials(
    stock_id: str,
    limit: int = Query(12, description="最近幾季的財報（預設 12 季＝3 年）"),
    db: Session = Depends(get_db),
):
    """回傳個股季度財報（目前為 EPS 每股盈餘），由新到舊。"""
    rows = (
        db.query(Financial)
        .filter(Financial.stock_id == stock_id)
        .order_by(Financial.date.desc())
        .limit(limit)
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="這檔股票還沒有財報資料，請先執行 seed.py 匯入")
    return [
        FinancialOut(
            date=r.date.isoformat(),
            eps=float(r.eps) if r.eps is not None else None,
        )
        for r in rows
    ]


@router.get("/stocks/{stock_id}/revenue", response_model=list[RevenueOut])
def get_revenue(
    stock_id: str,
    limit: int = Query(12, description="最近幾個月的營收（預設 12 個月）"),
    db: Session = Depends(get_db),
):
    """回傳個股每月營收，並即時計算 YoY（年增率）、MoM（月增率），由新到舊。"""
    rows = (
        db.query(Revenue)
        .filter(Revenue.stock_id == stock_id)
        .order_by(Revenue.year.asc(), Revenue.month.asc())
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="這檔股票還沒有營收資料，請先執行 seed.py 匯入")

    # 建 (年,月) -> 營收 的查表，方便找「去年同月」「上個月」
    rev_map = {(r.year, r.month): r.revenue for r in rows}

    def pct(cur: int, base) -> float | None:
        if not base:            # base 為 None 或 0 都不算，避免除以 0
            return None
        return round((cur - base) / base * 100, 2)

    out = []
    for r in rows:
        yoy = pct(r.revenue, rev_map.get((r.year - 1, r.month)))          # 去年同月
        prev_ym = (r.year, r.month - 1) if r.month > 1 else (r.year - 1, 12)  # 上個月（跨年處理）
        mom = pct(r.revenue, rev_map.get(prev_ym))
        out.append(RevenueOut(
            year=r.year, month=r.month, revenue=int(r.revenue), yoy=yoy, mom=mom,
        ))

    # 由新到舊，取最近 limit 筆
    out.reverse()
    return out[:limit]


@router.get("/rankings")
def rankings(top: int = 10, db: Session = Depends(get_db)):
    """以最近兩個交易日計算漲跌幅，回傳上漲/下跌排行。"""
    # 只遍歷「有日線資料」的股票（約 50 檔），不要掃全台 3088 檔做無謂查詢
    # （原本 for 全部 Stock 再逐檔查 DB 是 N+1，實測 ~4.5s；改這樣後只剩數十次查詢）
    stock_ids = [r[0] for r in db.query(DailyPrice.stock_id).distinct().all()]
    name_map = dict(
        db.query(Stock.stock_id, Stock.name).filter(Stock.stock_id.in_(stock_ids)).all()
    )
    results = []
    for sid in stock_ids:
        last2 = (
            db.query(DailyPrice)
            .filter(DailyPrice.stock_id == sid)
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
            "stock_id": sid, "name": name_map.get(sid, ""),
            "close": float(cur.close), "change": round(change, 2), "pct": pct,
        })
    results.sort(key=lambda x: x["pct"], reverse=True)
    return {"gainers": results[:top], "losers": results[-top:][::-1]}
