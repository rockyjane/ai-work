"""自選股 CRUD。展示後端的新增/查詢/刪除。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Watchlist, Stock
from ..schemas import WatchlistCreate

router = APIRouter(tags=["watchlist"])


@router.get("/watchlist")
def list_watchlist(db: Session = Depends(get_db)):
    items = db.query(Watchlist).order_by(Watchlist.created_at.desc()).all()
    out = []
    for w in items:
        s = db.query(Stock).filter(Stock.stock_id == w.stock_id).first()
        out.append({
            "id": w.id, "stock_id": w.stock_id,
            "name": s.name if s else None, "note": w.note,
        })
    return out


@router.post("/watchlist")
def add_watchlist(body: WatchlistCreate, db: Session = Depends(get_db)):
    exists = db.query(Watchlist).filter(Watchlist.stock_id == body.stock_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="已在自選股中")
    w = Watchlist(stock_id=body.stock_id, note=body.note or "")
    db.add(w)
    db.commit()
    db.refresh(w)
    return {"id": w.id, "stock_id": w.stock_id, "note": w.note}


@router.delete("/watchlist/{item_id}")
def remove_watchlist(item_id: int, db: Session = Depends(get_db)):
    w = db.query(Watchlist).filter(Watchlist.id == item_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="找不到此自選股")
    db.delete(w)
    db.commit()
    return {"ok": True}
