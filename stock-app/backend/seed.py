"""一鍵匯入示範資料：抓幾檔熱門台股的近 2 年日線進資料庫。

用法（記得先 activate venv）：
    python seed.py

跑完後啟動 API：
    uvicorn app.main:app --reload
然後開 http://127.0.0.1:8000/docs 測試。
"""
from datetime import date, timedelta

from app.database import Base, engine, SessionLocal
from app.data_fetcher import fetch_daily, fetch_stock_info, upsert_prices, upsert_stock

# 示範用熱門股（代號: 名稱），抓不到官方基本資料時用這份當後備
POPULAR = {
    "2330": "台積電",
    "2317": "鴻海",
    "2454": "聯發科",
    "2412": "中華電",
    "2882": "國泰金",
    "2881": "富邦金",
    "2603": "長榮",
    "2308": "台達電",
    "3008": "大立光",
    "0050": "元大台灣50",
}


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    start = (date.today() - timedelta(days=365 * 2)).isoformat()

    # 1) 嘗試抓官方基本資料（產業、市場別），失敗就用後備名稱
    info_map = {}
    try:
        info = fetch_stock_info()
        for _, r in info.iterrows():
            info_map[str(r["stock_id"])] = {
                "name": r.get("stock_name", ""),
                "industry": r.get("industry_category", ""),
                "market": "上市" if r.get("type") == "twse" else "上櫃",
            }
        print(f"已取得 {len(info_map)} 檔股票基本資料")
    except Exception as e:
        print(f"(略過基本資料抓取：{e})")

    # 2) 逐檔寫入基本資料 + 日線
    for sid, fallback_name in POPULAR.items():
        meta = info_map.get(sid, {})
        upsert_stock(
            db, sid,
            name=meta.get("name") or fallback_name,
            industry=meta.get("industry", ""),
            market=meta.get("market", "上市"),
        )
        try:
            df = fetch_daily(sid, start_date=start)
            n = upsert_prices(db, sid, df)
            print(f"  {sid} {fallback_name}: 新增 {n} 筆日線（共 {len(df)} 筆）")
        except Exception as e:
            print(f"  {sid} {fallback_name}: 抓取失敗 - {e}")

    db.close()
    print("\n完成！執行 `uvicorn app.main:app --reload` 啟動 API。")


if __name__ == "__main__":
    main()
