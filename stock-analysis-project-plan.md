# 台股分析網站 — 可行性與開發文檔

> 目標：做一個可在面試 DEMO 的「台股分析」全端網站，同時藉此補強後端與股票知識。
> 路線：前端用熟悉的 Vue/Angular 展示實力 → 後端先 Python(FastAPI) 快速做出成果 → 再用 Java(Spring Boot) 重寫同一套 API 做對照學習。

---

## 0. 為什麼這個專案適合你

| 你的條件 | 在這個專案的對應 |
|---|---|
| Vue 2 / Angular 16+ 熟悉、TypeScript 有底 | 前端用 **Vue 3 + TS**，3 天內就能做出漂亮 DEMO，面試直接展示強項 |
| Python / Java / MySQL 有基礎但不熟 | 後端從 FastAPI 入門（最好上手），再用 Spring Boot 進階，剛好補強 |
| 對股票一竅不通 | 每個技術指標（MA/RSI/MACD/KD）都是一堂股市基礎課，邊做邊學 |
| 想進台灣金融業 | 台股題材 + 金融常見的「資料處理 + 圖表儀表板」是金融前後端的核心場景 |

**面試敘事**：「我從前端轉全端，自己用 Vue 3 + FastAPI + MySQL 做了一個台股分析平台，能抓即時行情、畫 K 線、算技術指標，後端我還用 Spring Boot 重寫了一遍來比較兩種生態。」— 這故事對金融業很有說服力。

---

## 1. 技術選型（已鎖定可在你電腦穩定運行的版本）

### 前端
| 項目 | 選擇 | 理由 |
|---|---|---|
| 框架 | **Vue 3.4+ + Vite 5** | 你已熟 Vue 2，Composition API 是現代寫法，面試加分 |
| 語言 | **TypeScript** | 你 Angular 已用過 TS，直接沿用 |
| 狀態管理 | **Pinia** | Vue 3 官方推薦，比 Vuex 簡單 |
| 路由 | **Vue Router 4** | 標配 |
| UI 元件庫 | **Element Plus** | 金融儀表板常用，表格/表單/日期選擇器齊全 |
| 圖表 | **Apache ECharts 5** | 內建 K 線(candlestick)、可疊加技術指標、中文文件完整。<br>（備選：TradingView Lightweight Charts，更「券商感」但功能較專一） |

### 後端 — 第一階段（主力）
| 項目 | 選擇 | 理由 |
|---|---|---|
| 框架 | **FastAPI** | 最易上手、自動產生 Swagger API 文件、效能好 |
| 伺服器 | **Uvicorn** | FastAPI 標配 |
| ORM | **SQLAlchemy 2.0 + Alembic** | 連 MySQL、做資料表遷移 |
| 資料處理 | **pandas + numpy** | 算指標、整理行情的核心 |
| 技術指標 | **`ta` 套件（純 Python）** | ⚠️ **不要用 TA-Lib**：它要編譯 C 函式庫，在你這台 Intel/Monterey 容易卡安裝。`ta` 純 Python 免編譯 |
| 排程 | **APScheduler** | 每日定時抓收盤資料進 DB |

### 後端 — 第二階段（進階對照）
| 項目 | 選擇 |
|---|---|
| 框架 | **Spring Boot 3.x**（需 Java 17+） |
| 模組 | Spring Web、Spring Data JPA、MySQL Connector/J |
| 建置工具 | **Maven**（或 Gradle，二選一） |
| 目標 | 把 FastAPI 的同一套 REST API 重寫一遍，比較兩種後端生態 |

### 資料庫
- **MySQL**（用你現有的 Docker 容器，不用另裝）。

---

## 2. ⚠️ 你的電腦相容性把關（最重要）

你的環境：**MacBook Pro Mid 2015 / Intel / macOS Monterey 12.7.6**，並存 Anaconda、Homebrew Python、NVM、rbenv、Docker(MySQL+phpMyAdmin)。針對這台做的風險控管：

### 2.1 Python 環境（多版本並存 → 最大風險）
你同時有 **Anaconda** 和 **Homebrew Python**，PATH 容易打架。**鐵則：本專案用一個獨立 venv，不要用 conda base 環境。**

> 📌 **實測補充**：在你這台機器上，`python3` 指向 **Homebrew 的 Python 3.13.7**，
> 而 **3.11.13 來自 Anaconda**（`python3.11` 指令可直接叫到）。本專案要用 3.11，
> 所以建 venv 時**明確用 `python3.11`**，不要用 `python3`。

```bash
# 進專案後端資料夾，用 Python 3.11 建獨立 venv（venv 建好後就獨立於 Anaconda）
python3.11 -m venv .venv         # ← 不要用 python3（那是 3.13）
source .venv/bin/activate
python -V   # 確認是 3.11.x，且 which python 指向 .venv
```
- ❌ 避免用 **Python 3.13**：`numpy<2` 在 3.13 沒有預編譯 wheel，會嘗試編譯而失敗。**用 3.11**。
- 每次開發前先 `source .venv/bin/activate`，避免裝到全域。

> 💡 **踩雷紀錄（已解決）**：FinMind 套件的相依關係很「霸道」，會牽動 pandas / pydantic / ta
> 的版本。實測鎖定的可用組合是 **pandas 2.3.x + FinMind 1.9.11 + pydantic 2.x**，且技術指標
> 改成**純 pandas 手算**（不裝 ta 套件）以徹底避開衝突。這些都已寫進 `stock-app/backend/requirements.txt`。

### 2.2 Node.js（用你的 NVM）
```bash
nvm install 20      # Node 20 LTS，對 Intel/Monterey 最穩
nvm use 20
node -v             # v20.x
```
- Vite 5 需要 Node 18+，**Node 20 LTS** 是安全選擇；不必追 Node 22+。

### 2.3 Docker / MySQL（你已有，不要亂升級）
- ⚠️ **不要升級 Docker Desktop**。新版 Docker Desktop 可能已不支援 Monterey，而你現在的版本 phpMyAdmin 已正常運作 → **維持現狀**。
- 沿用現有 MySQL 容器，新增一個 database 給本專案即可（例如 `stock_db`），用 phpMyAdmin 介面建立。
- **記憶體提醒**：2015 機種 RAM 有限，Docker(MySQL) + 前端 dev server + 後端 同時跑會吃資源。開發時關掉其他大型 App；做 Java 階段時，不要 Python/Java 後端同時開。

### 2.4 Java（第二階段才裝）
```bash
# 用 Homebrew 裝 Temurin 17 LTS（Spring Boot 3 需要 Java 17+，且對 Intel Mac 支援完整）
brew install --cask temurin@17
java -version       # 確認 17.x
brew install maven
```
- **用 Java 17 LTS**，不要追太新版本，確保 Spring Boot 3 與 Intel/Monterey 都穩。

### 2.5 相容性總結（一眼版）
| 工具 | 鎖定版本 | 備註 |
|---|---|---|
| Python | **3.11**（獨立 venv） | 別用 conda base、別用 3.13 |
| Node | **20 LTS**（NVM） | 別追 22+ |
| Java | **17 LTS**（Temurin，第二階段） | Spring Boot 3 需要 |
| Docker Desktop | **維持現有版本** | ⚠️ 不要升級 |
| MySQL | 現有容器新增 DB | 用 phpMyAdmin 管理 |

---

## 3. 系統架構

```
┌────────────────────┐     HTTP/JSON      ┌──────────────────────┐
│   前端 (Vue 3)      │ ─────────────────► │  後端 API            │
│   Vite + TS         │ ◄───────────────── │  Phase1: FastAPI     │
│   Element Plus      │                    │  Phase2: Spring Boot │
│   ECharts (K線)     │                    └──────────┬───────────┘
└────────────────────┘                               │ SQLAlchemy / JPA
                                                      ▼
                                          ┌──────────────────────┐
            台股資料源 (FinMind / TWSE)    │  MySQL (Docker)       │
            ───── 定時抓取 (APScheduler) ─►│  stocks / prices ...  │
                                          └──────────────────────┘
```
**資料流**：排程程式每天抓台股收盤資料 → 存進 MySQL → API 從 DB 讀取並計算指標 → 前端畫圖。
（不直接讓前端打第三方 API，是為了：① 控制 rate limit ② 展示後端資料處理能力 ③ 金融業重視自有資料層）

---

## 4. 台股資料來源（免費）

| 來源 | 用途 | 說明 |
|---|---|---|
| **FinMind** ⭐主力 | 股價、財報、月營收、除權息 | 免費 API + Python 套件，文件完整，台股最齊。有流量限制，故搭配 DB 快取 |
| **TWSE 證交所開放資料** | 上市每日行情、基本資料 | 官方來源，補充用 |
| **yfinance** | 備援股價 | 台股代號加 `.TW`（如 `2330.TW`） |
| **twstock** | 即時/歷史報價 | 純 Python，抓 TWSE，當備援 |

> 起手式建議：**FinMind 當主資料源**（一個套件搞定股價+財報），TWSE 開放資料當補充。

---

## 5. 資料庫設計（MVP）

```sql
-- 股票基本資料
CREATE TABLE stocks (
  stock_id   VARCHAR(10) PRIMARY KEY,   -- 2330
  name       VARCHAR(50),               -- 台積電
  industry   VARCHAR(50),               -- 半導體
  market     VARCHAR(10)                -- 上市/上櫃
);

-- 每日 K 線
CREATE TABLE daily_prices (
  id        BIGINT AUTO_INCREMENT PRIMARY KEY,
  stock_id  VARCHAR(10),
  date      DATE,
  open      DECIMAL(10,2),
  high      DECIMAL(10,2),
  low       DECIMAL(10,2),
  close     DECIMAL(10,2),
  volume    BIGINT,
  UNIQUE KEY uniq_stock_date (stock_id, date),
  INDEX idx_stock (stock_id)
);

-- 自選股（展示 CRUD / 之後可加會員）
CREATE TABLE watchlist (
  id        BIGINT AUTO_INCREMENT PRIMARY KEY,
  stock_id  VARCHAR(10),
  note      VARCHAR(200),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
（進階再加 `financial_statements` 財報表、`users` 會員表。）

---

## 6. 功能清單 ＋ 對應學到的股票知識

### MVP（先做到這裡就能 DEMO）
| 功能 | 後端 | 學到的股票知識 |
|---|---|---|
| 股票搜尋（代號/名稱） | `GET /api/stocks?q=台積` | 認識上市櫃、股票代號 |
| 個股 K 線圖 + 成交量 | `GET /api/stocks/{id}/prices` | 看懂開高低收、K 棒紅黑、量價關係 |
| **均線 MA**（5/20/60 日） | 後端用 pandas 算 | 短中長期趨勢、黃金/死亡交叉 |
| 自選股 CRUD | `POST/DELETE /api/watchlist` | 投組概念 |
| 漲跌幅排行榜 | `GET /api/rankings` | 強弱勢股 |

### 進階（讓 DEMO 更亮眼）
| 功能 | 學到的股票知識 |
|---|---|
| **RSI**（相對強弱） | 超買超賣 |
| **MACD** | 趨勢動能、背離 |
| **KD 隨機指標** | 台股最常用的指標之一 |
| **布林通道 Bollinger** | 波動率、壓力支撐 |
| 基本面：本益比 PE、EPS、殖利率 | 價值投資基礎 |
| 簡單策略警示（如 RSI<30 提示） | 量化交易入門 |

> 這些指標 `ta` 套件都有現成函式，你只要呼叫 + 理解意義，正好是「學股票」的入口。

---

## 7. 開發階段與時程（建議）

| 階段 | 內容 | 預估 | 產出 |
|---|---|---|---|
| **P0 環境建置** | venv / Node / Docker DB 確認、建 repo | 0.5 天 | 能跑的空殼 |
| **P1 資料管線** | FinMind 抓台積電等資料 → 寫進 MySQL | 1.5 天 | DB 有真實台股資料 |
| **P2 FastAPI** | 股票、K線、自選股 REST API + Swagger | 2 天 | 可呼叫的 API |
| **P3 前端骨架** | Vue3 專案、路由、清單頁、串接 API | 2 天 | 看得到資料的網頁 |
| **P4 圖表＋指標** | ECharts 畫 K 線、疊 MA/RSI/MACD/KD | 2.5 天 | 像樣的分析頁 ⭐DEMO 點 |
| **P5 收尾** | 自選股、排行榜、RWD、錯誤處理 | 1.5 天 | 完整 MVP |
| **P6 Java 重寫** | Spring Boot 實作同一套 API（對照學習） | 3 天 | 後端雙版本 |
| **P7 部署(選配)** | 前端 Vercel／後端 Render，免費方案 | 1 天 | 線上可訪問連結 |

> 全職投入約 **2～3 週**到 MVP（P0–P5），Java 與部署可面試前再補。
> 部署用雲端免費方案，**和你 2015 Intel Mac 無關**（雲端跑），不必擔心機器負擔。

---

## 8. 環境建置快速指令

```bash
# === 後端 (Phase 1) ===
mkdir -p ~/ai_work/stock-app/backend && cd ~/ai_work/stock-app/backend
conda deactivate 2>/dev/null            # 避免 conda 干擾
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn[standard] sqlalchemy alembic pymysql \
            pandas numpy ta FinMind apscheduler python-dotenv
uvicorn main:app --reload               # 寫好 main.py 後啟動，開 http://127.0.0.1:8000/docs

# === 前端 ===
cd ~/ai_work/stock-app
nvm use 20
npm create vite@latest frontend -- --template vue-ts
cd frontend && npm install
npm install element-plus echarts pinia vue-router axios
npm run dev                             # http://localhost:5173

# === MySQL（用現有 Docker，透過 phpMyAdmin 建 stock_db）===
# 在 phpMyAdmin 介面新增 database: stock_db
```

`.env`（後端，連你的 Docker MySQL；連線埠依你 phpMyAdmin 設定調整）：
```
DATABASE_URL=mysql+pymysql://root:你的密碼@127.0.0.1:3306/stock_db
FINMIND_TOKEN=（到 finmindtrade.com 免費註冊取得，可選）
```

---

## 9. 面試 DEMO 重點（怎麼講最加分）

1. **打開 K 線分析頁** → 切換不同股票、疊加 MA/MACD，展示前端圖表互動力。
2. **打開 `/docs`（Swagger）** → 顯示你設計的 REST API，講資料如何從 DB 來。
3. **講架構決策**：「為什麼後端先存進 MySQL 而不是前端直接打第三方？」→ rate limit、自有資料層、金融資料一致性。
4. **講雙後端**：「我用 FastAPI 跟 Spring Boot 各實作一次，FastAPI 開發快、Spring Boot 在金融業更主流也更嚴謹。」→ 展示學習力與技術判斷。
5. **誠實談股票知識**：「做這專案前我不懂股票，透過實作技術指標理解了均線、KD、MACD 的意義。」→ 學習態度。

---

## 10. 風險與注意事項

- ⚠️ **Python 多環境衝突**：務必用獨立 venv，別污染 conda base（見 §2.1）。
- ⚠️ **Docker Desktop 勿升級**：保住現有可用版本（見 §2.3）。
- ⚠️ **不用 TA-Lib**：改用純 Python 的 `ta`，避開編譯問題（見 §1）。
- ⚠️ **資料源流量限制**：FinMind 免費版有 API 上限 → 一定要做 DB 快取，別每次都打外部 API。
- ⚠️ **2015 機器資源**：避免 Docker + 雙後端 + 前端同時全開；做 Java 階段先關掉 Python 後端。
- ⚠️ **台股交易日**：抓資料要處理假日/休市（沒資料的日期），ECharts 的 K 線 x 軸用「交易日陣列」而非連續日期，避免出現空白。
- 📌 **版權/用途**：免費資料源僅供個人學習 DEMO，勿商用。

---

## 11. 後續可延伸（面試後加分）

- 使用者登入（JWT）＋ 個人化自選股
- WebSocket 即時報價推播
- Docker Compose 一鍵啟動整套（前端+後端+DB）→ 展示 DevOps 概念
- 簡單回測引擎（給定策略，算歷史報酬）
- CI/CD（GitHub Actions）

---

### 下一步建議
先做 **P0 + P1**：把環境建好、用 FinMind 把台積電(2330)的歷史股價抓進 MySQL。這一步打通，整個專案就活了。需要我幫你寫 P1 的抓資料腳本、或先把後端 `main.py` 骨架生出來，跟我說一聲。
