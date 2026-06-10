"""FastAPI 進入點。

啟動：  uvicorn app.main:app --reload
文件：  http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import stocks, watchlist

# 第一次啟動時自動建立資料表（正式專案會改用 Alembic 遷移）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="台股分析 API", version="0.1.0")

# 開發階段允許前端跨來源呼叫（前端另有 Vite proxy，雙保險）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, prefix="/api")
app.include_router(watchlist.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "台股分析 API 運行中", "docs": "/docs"}
