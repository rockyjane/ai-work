# stock-app 開發紀錄（詳細）

> 「股票分析網站」這個專案**專屬**的詳細開發紀錄：完成了什麼、踩了什麼坑（現象→原因→解法）、實測結果。
> 面試時「我遇到問題→怎麼 debug→怎麼解」的故事，比功能本身更能展現實力。
>
> - 跨專案的**簡要摘要**在上層 [`../DEV_LOG.md`](../DEV_LOG.md)。
> - 環境／工具搭建的雷在 [`../CLAUDE_CODE_SETUP_GUIDE.md`](../CLAUDE_CODE_SETUP_GUIDE.md)。
> - 格式：每筆以 `## 日期 時間 [寫入者] 分類` 開頭；分類：`完成`／`雷`／`實測`／`決策`／`觀念`／`待辦`。

---

## 建置記錄（依時間順序）

## 2026-06-10 21:30 [claude] 完成
後端 FastAPI 完整骨架搭好：搜尋、K線+技術指標、漲跌幅排行、自選股共 4 組 API。用 `python3.11` 建好 venv、裝好套件；`seed.py` 從 FinMind 抓到 **10 檔台股、各約 485 個交易日的真實資料**（到 2026-06-10）；啟動伺服器**實測每個 API 都正常回傳**。前端 Vue 3 程式碼全部寫好（尚未 `npm install`）。

## 2026-06-10 21:40 [claude] 雷
**Python 版本不對，numpy 裝不起來。**
- 現象：`python3 -m venv` 建出來是 **Python 3.13**，裝 `numpy<2` 失敗（3.13 沒有預編譯 wheel，會硬編譯而出錯）。
- 原因：這台的 `python3` 指向 Homebrew 3.13；3.11 藏在 Anaconda 裡（`python3.11` 可直接叫到）。
- 解法：改用 `python3.11 -m venv .venv`；venv 一旦建好就獨立於 Anaconda。

## 2026-06-10 21:50 [claude] 雷
**FinMind 相依套件打架（最花時間的一關）。**
- 現象：一開始沒鎖版本，`ta` 被裝成 2019 舊版（API 不同、跑不動）；想修 `ta` 又把 pandas／pydantic 拉到互相衝突。
- 原因：FinMind 相依很「霸道」，會指定 pandas／pydantic／ta 版本，和 FastAPI（要新版 pydantic）打架。關鍵死結：`ta` 0.11 要 pandas<2.3、FinMind 1.9.11 要 pandas≥2.3 → 無解。
- 解法（關鍵決策）：**乾脆不用 `ta`，技術指標改用純 pandas 手算**。①衝突立刻消失 ②更看得懂指標原理。鎖定組合 `pandas 2.3.x + FinMind 1.9.11 + pydantic 2.x + numpy 1.26 + tqdm`（見 `backend/requirements.txt`）。

## 2026-06-10 22:00 [claude] 雷
**SQLite 主鍵不會自動編號。**
- 現象：寫入股價時報 `NOT NULL constraint failed: daily_prices.id`。
- 原因：`id` 用了 `BigInteger`，但 SQLite 只有宣告成 `INTEGER` 的主鍵才會自增。
- 解法：改用 `BigInteger().with_variant(Integer, "sqlite")` — MySQL 是 BIGINT、SQLite 變成可自增的 INTEGER，一份程式碼兩種 DB 都通。

## 2026-06-10 22:05 [claude] 決策
**資料層設計。** DB 預設 **SQLite**（零設定即可跑），`.env` 的 `DATABASE_URL` 改一行就切到 Docker **MySQL**，程式碼不動（面試談資：同一份 ORM 兩種 DB）。台股行情**先由後端抓進 DB 再供前端讀**，不讓前端直打第三方 API——控 FinMind rate limit、建立自有資料層、金融資料一致性。

## 2026-06-10 22:10 [claude] 實測
證明真的會動：
```
搜尋 2330 → 台積電 / 半導體業 / 上市
2330 近一年 K 線 250 天，最後一根：開2285 收2255 低2255 高2300（2026-06-10）
指標末值：MA5=2321  MA20=2297  MA60=2114  RSI=48  KD=37/53
漲幅榜：大立光 +6.31%、中華電 +1.41%
```

## 2026-06-10 22:15 [claude] 觀念
技術指標白話：MA=趨勢均價、RSI=超買超賣溫度計（>70 熱、<30 冷）、MACD=漲跌動能、KD=收盤價在近 9 日高低區間的位置。面試談資：「從不懂股票，到親手實作這些指標來真正理解其意義」。

---

## 現況與下一步（隨進度更新，配合 README.md）

- **後端**：完成且已驗證，照 `README.md` 即可啟動。
- **前端**：程式碼齊全，待 `cd frontend && nvm use 20 && npm install && npm run dev`。
- **待辦**：擴充更多股票 → 加財報基本面 → 最後用 Spring Boot 重寫後端做對照。
