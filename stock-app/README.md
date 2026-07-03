# 台股分析 MVP

Vue 3 + FastAPI + SQLite/MySQL 的台股分析網站。功能：股票搜尋、K 線圖、技術指標（MA/RSI/MACD/KD）、漲跌幅排行、自選股。

> 環境已針對 MacBook Pro 2015 / Intel / Monterey 12.7.6 調校。詳見上層 `stock-analysis-project-plan.md`。
> 本專案**詳細開發紀錄**見 [`DEV_LOG.md`](DEV_LOG.md)（現象/原因/解法、實測、現況與下一步）；跨專案**簡要摘要**在 [`../DEV_LOG.md`](../DEV_LOG.md)；環境/工具搭建的雷在 [`../CLAUDE_CODE_SETUP_GUIDE.md`](../CLAUDE_CODE_SETUP_GUIDE.md)。

---

## 一、啟動後端（FastAPI）

> ⚠️ **重要**：你的 `python3` 是 Homebrew 的 **3.13**，但本專案要用 **3.11**
> （numpy<2 在 3.13 沒有預編譯 wheel，會嘗試編譯而失敗）。你的機器上有
> Anaconda 提供的 `python3.11`，所以下面**刻意用 `python3.11` 建 venv**。
> venv 一旦建好就獨立於 Anaconda，之後都用 venv 內的 `python`。

```bash
cd ~/ai_work/stock-app/backend

# 1. 用 Python 3.11 建獨立 venv（venv 建好後即與 Anaconda 脫鉤）
python3.11 -m venv .venv         # ← 一定要用 3.11，不要用 python3（那是 3.13）
source .venv/bin/activate
python -V                        # 應顯示 Python 3.11.x

# 2. 安裝套件（版本已在 requirements.txt 鎖好，避開 FinMind 相依衝突）
pip install --upgrade pip
pip install -r requirements.txt

# 3. 設定環境變數（預設用 SQLite，零設定）
cp .env.example .env

# 4. 匯入示範資料（抓 10 檔熱門台股近 2 年日線，需連網，約 10 秒）
python seed.py

# 5. 啟動 API
uvicorn app.main:app --reload
```

> 已在這台機器實測通過：seed 成功抓到 2330 等 10 檔近 485 個交易日的真實資料，
> 所有 API（搜尋 / K線+指標 / 排行 / 自選股）皆正常。

啟動後打開 **http://127.0.0.1:8000/docs** 就能看到並測試所有 API。

### 想改用你 Docker 裡的 MySQL？
1. 先到 phpMyAdmin 建一個 database：`stock_db`
2. 編輯 `.env`，把 `DATABASE_URL` 改成（密碼/埠號依你的設定）：
   ```
   DATABASE_URL=mysql+pymysql://root:你的密碼@127.0.0.1:3306/stock_db
   ```
3. 重新 `python seed.py` → `uvicorn app.main:app --reload`

> 程式碼完全不用改，切換 DB 只動這一行。這正好是面試可講的「資料層抽象」亮點。

---

## 二、啟動前端（Vue 3）

**另開一個終端機**（後端維持運行）：

```bash
cd ~/ai_work/stock-app/frontend
nvm use 20                      # Node 20 LTS
npm install
npm run dev
```

打開 **http://localhost:5173**。前端會透過 Vite proxy 自動把 `/api` 轉發到後端，不會有 CORS 問題。

---

## 三、操作流程

1. **股票總覽**：搜尋台積電/2330，右側有漲跌幅排行
2. 點任一檔 → **個股頁**：K 線 + 成交量 + 可切換 KD / MACD / RSI 副圖
3. 點「加入自選股」→ 到 **我的自選股** 頁管理

---

## 專案結構

```
stock-app/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 進入點
│   │   ├── database.py      # DB 連線（SQLite/MySQL 切換）
│   │   ├── models.py        # 資料表
│   │   ├── schemas.py       # API 資料格式
│   │   ├── indicators.py    # 技術指標計算（MA/RSI/MACD/KD）
│   │   ├── data_fetcher.py  # FinMind 抓資料
│   │   └── routers/         # API 路由
│   ├── seed.py              # 一鍵匯入示範資料
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/             # axios 封裝
        ├── views/           # 三個頁面
        └── components/      # KLineChart 圖表元件
```

## 疑難排解

- **`python seed.py` 抓不到資料**：FinMind 匿名額度可能被限流，到 https://finmindtrade.com 註冊拿免費 token，填到 `.env` 的 `FINMIND_TOKEN`，再重跑。
- **`pip install` 卡在 numpy/pandas**：確認 venv 用的是 Python 3.11，且已 `conda deactivate`。
- **前端打 API 失敗**：確認後端在 8000 埠運行中（`/docs` 打得開）。
