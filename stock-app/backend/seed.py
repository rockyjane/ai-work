"""匯入示範資料。

兩部分：
1) 全台股「基本資料」→ 寫進 stocks 表（讓搜尋涵蓋全台股，成本低）。
2) 台灣50 級別的大型權值股 → 抓近 2 年日線（K線/指標/排行用）。

用法（記得先 activate venv）：
    python seed.py

跑完後啟動 API：
    uvicorn app.main:app --reload

備註：FinMind 匿名額度有限，抓幾十檔可能被限流。若看到大量「抓取失敗」，
到 https://finmindtrade.com 註冊免費 token 填進 .env 的 FINMIND_TOKEN 再重跑。
"""
import time
from datetime import date, timedelta

from app.database import Base, engine, SessionLocal
from app.data_fetcher import fetch_daily, fetch_stock_info, upsert_prices
from app.models import Stock

# 台灣50 級別的大型權值股（精選約 50 檔；名稱僅為後備，實際以 FinMind 官方資料為準）
TW50 = {
    "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "2308": "台達電", "2382": "廣達",
    "2891": "中信金", "2882": "國泰金", "2881": "富邦金", "2412": "中華電", "2303": "聯電",
    "3711": "日月光投控", "2886": "兆豐金", "2884": "玉山金", "1216": "統一", "2885": "元大金",
    "2892": "第一金", "2357": "華碩", "3034": "聯詠", "2890": "永豐金", "2345": "智邦",
    "2379": "瑞昱", "3231": "緯創", "2883": "凱基金", "5880": "合庫金", "2887": "台新金",
    "2327": "國巨", "3008": "大立光", "2603": "長榮", "2002": "中鋼", "1303": "南亞",
    "1301": "台塑", "2207": "和泰車", "2880": "華南金", "4938": "和碩", "2301": "光寶科",
    "3037": "欣興", "2395": "研華", "6505": "台塑化", "1326": "台化", "2912": "統一超",
    "2801": "彰銀", "5871": "中租-KY", "3045": "台灣大", "2618": "長榮航", "9910": "豐泰",
    "2474": "可成", "2356": "英業達", "2344": "華邦電", "2409": "友達", "6669": "緯穎",
}

FETCH_SLEEP = 0.6  # 每檔之間間隔（秒），降低被 FinMind 限流的機率


def seed_all_stock_info(db):
    """把全台股基本資料寫進 stocks 表，讓搜尋涵蓋全台股。"""
    try:
        info = fetch_stock_info()
    except Exception as e:
        print(f"(略過全台股基本資料抓取：{e})")
        return
    existing = {s[0] for s in db.query(Stock.stock_id).all()}
    seen, rows = set(), []
    for _, r in info.iterrows():
        sid = str(r["stock_id"])
        if sid in existing or sid in seen:
            continue
        seen.add(sid)
        rows.append(Stock(
            stock_id=sid,
            name=r.get("stock_name", ""),
            industry=r.get("industry_category", ""),
            market="上市" if r.get("type") == "twse" else "上櫃",
        ))
    if rows:
        db.bulk_save_objects(rows)
        db.commit()
    print(f"基本資料：新增 {len(rows)} 檔（stocks 表共 {len(existing) + len(rows)} 檔）")


def ensure_tw50_rows(db):
    """保險：萬一全量基本資料抓失敗，至少確保 TW50 有基本資料列。"""
    existing = {s[0] for s in db.query(Stock.stock_id).all()}
    missing = [Stock(stock_id=c, name=n, market="上市") for c, n in TW50.items() if c not in existing]
    if missing:
        db.bulk_save_objects(missing)
        db.commit()
        print(f"（後備補上 {len(missing)} 檔 TW50 基本資料）")


def seed_daily_prices(db, start):
    """抓 TW50 的日線，含節流與限流容錯。"""
    ok = 0
    for i, sid in enumerate(TW50, 1):
        try:
            df = fetch_daily(sid, start_date=start)
            n = upsert_prices(db, sid, df)
            print(f"  [{i:>2}/{len(TW50)}] {sid} {TW50[sid]}: 新增 {n} 筆（共 {len(df)}）")
            ok += 1
        except Exception as e:
            print(f"  [{i:>2}/{len(TW50)}] {sid} {TW50[sid]}: 抓取失敗（可能限流）- {e}")
        time.sleep(FETCH_SLEEP)
    print(f"日線完成：{ok}/{len(TW50)} 檔成功")
    if ok < len(TW50):
        print("※ 有失敗檔，多半是 FinMind 匿名限流。設定 FINMIND_TOKEN 後重跑即可補齊。")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    seed_all_stock_info(db)
    ensure_tw50_rows(db)

    start = (date.today() - timedelta(days=365 * 2)).isoformat()
    seed_daily_prices(db, start)

    db.close()
    print("\n完成！執行 `uvicorn app.main:app --reload` 啟動 API。")


if __name__ == "__main__":
    main()
