# stock-app 開發紀錄（詳細）

> 「股票分析網站」專案**專屬**的詳細開發紀錄。面試時「遇到問題→怎麼 debug→怎麼解」的故事，比功能本身更能展現實力；而這個專案的核心目的之一是**邊做邊學**，所以「決策」與「學到的觀念/知識」各自獨立成一大點。
>
> - 跨專案**簡要摘要**在上層 [`../DEV_LOG.md`](../DEV_LOG.md)；環境／工具搭建的雷在 [`../CLAUDE_CODE_SETUP_GUIDE.md`](../CLAUDE_CODE_SETUP_GUIDE.md)。
> - **結構固定為六大要點**：一、完成 ／ 二、坑&解法 ／ 三、決策 ／ 四、學到的觀念/知識 ／ 五、實測 ／ 六、現況。
> - 每到一個進度點，就在對應大點加上時間戳條目 `### 日期 時間 [寫入者] [屬於誰] 分類`，並更新「六、現況與下一步」。
>   - **[寫入者]** = 這份工作是誰做的：`[me]`（開發者本人）、`[claude]`（我）；日後分工可用 `[frontend-dev]`、`[backend-dev]` 等。（你自行開發的部分不必自己寫，交付前我依 diff 補寫、標 `[me]`。）
>   - **[屬於誰]** = 這則屬於哪一塊：`[前端]` ／ `[後端]` ／ `[全端]` ／ `[金融]`（可組合，如 `[前、後端]`）。方便日後一眼看出每個雷/決策/觀念當時屬於誰。
>   - **分類**：完成／雷／決策／觀念／實測。
> - 「坑&解法」每筆**至少**要有 **現象→原因→解法**，鼓勵再補好處、可用組合等。「觀念/知識」涵蓋**程式與金融**兩類，金融的先用白話解釋。

---

## 一、這次完成了什麼

### 2026-06-10 21:30 [claude] [全端] 完成
✅ 後端 FastAPI 完整骨架（搜尋、K線+指標、排行、自選股 4 組 API）
✅ 用 `python3.11` 建好 venv、裝好所有套件
✅ `seed.py` 從 FinMind 抓到 10 檔台股、各約 485 個交易日的真實資料（到 2026-06-10）
✅ 啟動伺服器並實測每個 API 都正常回傳
✅ 前端 Vue 3 程式碼全部寫好（尚未 `npm install`，留給你跑）

### 2026-07-04 17:06 [claude] [後端] 完成
擴充股票池：`seed.py` 改為 ① 把**全台股基本資料（3115 檔）**寫進 `stocks` 表，讓搜尋涵蓋全台股；② 抓**台灣50 級別約 50 檔大型權值股**近 2 年日線（K線/指標/排行用），加每檔節流（0.6s）與限流容錯（失敗跳過不中斷）。

### 2026-07-19 17:30 [claude] [後端] 完成
把資料庫從 SQLite **實際切換到 Docker MySQL 8.4 並跑通**：`.env` 改一行 `DATABASE_URL` → 重跑 seed → 全台股 **3088 檔**可搜尋、台灣50 共 **51 檔**日線 **24570 筆**進 MySQL；四組 API 端到端實測皆讀 MySQL 正常。（過程逼出一個跨 DB 真雷，見 §二；前端仍待啟動。）

---

## 二、踩到的坑 & 解法（重點）

### 2026-06-10 21:40 [claude] [後端] 雷
**Python 版本不對，numpy 裝不起來。**
- **現象**：`python3 -m venv` 建出來是 Python 3.13，安裝 `numpy<2` 時失敗（3.13 沒有預編譯好的 numpy 1.x，會去硬編譯而出錯）。
- **原因**：你的 `python3` 指向 Homebrew 的 3.13；而 3.11 其實藏在 Anaconda 裡（指令 `python3.11` 可直接叫到）。
- **解法**：改用 `python3.11 -m venv .venv`。venv 一旦建好就獨立運作，跟 Anaconda 無關。

### 2026-06-10 21:50 [claude] [後端] 雷
**FinMind 的相依套件「打架」（最花時間的一關）。**
- **現象**：一開始沒鎖版本，pip 自由安裝後，技術指標套件 `ta` 被裝成 2019 的舊版（API 不一樣，程式跑不動）；想修 `ta` 又連帶把 pandas、pydantic 拉到互相衝突的版本。
- **根本原因**：`FinMind` 這個套件的相依關係很「霸道」，會去指定 pandas / pydantic / ta 的版本，和 FastAPI（要新版 pydantic）打架。
  - `ta` 0.11 要求 pandas **< 2.3**
  - FinMind 1.9.11 要求 pandas **≥ 2.3**
  - → 兩者無解，無法同時安裝
- **解法（關鍵決策）**：乾脆不用 `ta` 套件，技術指標改成用 pandas 自己手算。
  - 好處 1：拔掉打架的那個套件，衝突立刻消失
  - 好處 2：你會看懂每個指標怎麼算出來的，學股票更扎實（不是 call 黑盒子）
- **最終鎖定的可用組合**（寫在 `backend/requirements.txt`）：`pandas 2.3.x` + `FinMind 1.9.11` + `pydantic 2.x` + `numpy 1.26`，外加補一個 FinMind 忘了宣告的 `tqdm`。

### 2026-06-10 22:00 [claude] [後端] 雷
**SQLite 主鍵不會自動編號。**
- **現象**：寫入股價時報錯 `NOT NULL constraint failed: daily_prices.id`。
- **原因**：資料表的 `id` 用了 `BigInteger`，但 SQLite 只有宣告成 `INTEGER` 的主鍵才會自動遞增編號。
- **解法**：改用 `BigInteger().with_variant(Integer, "sqlite")` — 在 MySQL 是 BIGINT、在 SQLite 自動變成會遞增的 INTEGER，一份程式碼兩種資料庫都通。

### 2026-07-19 17:30 [claude] [後端] 雷
**換 MySQL 才爆的「Data too long」——SQLite 不檢查 VARCHAR 長度、MySQL 會。**
- **現象**：`.env` 從 SQLite 改指 MySQL、重跑 seed 寫 `stocks` 基本資料時報 `DataError (1406) Data too long for column 'stock_id' at row 3077`；同一份程式碼在 SQLite 一路正常。
- **原因**：FinMind 全台股基本資料混入「指數」列（`industry=Index`，代碼如 `TradingConsumersGoods` 長 21 字元），超過 `stock_id = String(10)`。**SQLite 不強制 VARCHAR 長度**（超過照存），**MySQL 嚴格檢查**超長就擋 → 這雷只在 MySQL 現形。
- **解法**：seed 過濾掉 `industry=='Index'` 的指數列（本就非個股、不該進股票搜尋），並加 `len(sid)>10` 長度保險。真實證券代碼最長 6 碼（連債券 ETF `00835B` 都在 `String(10)` 內），故**維持 `String(10)`、不需改 schema**。
- **同類延伸**：和上一則「SQLite 主鍵不自增」同源，都是「SQLite 寬鬆、MySQL 嚴格」的跨 DB 差異——用嚴格的 MySQL 實測才逼得出來，這正是把 DB 換成 MySQL 的價值。

---

## 三、決策（為何這樣設計）

### 2026-06-10 22:05 [claude] [後端] 決策
**資料層設計。**
- DB 預設 **SQLite**（零設定即可跑），`.env` 的 `DATABASE_URL` 改一行就切到 Docker **MySQL**，程式碼完全不動（面試談資：同一份 ORM、兩種資料庫）。
- 台股行情**先由後端抓進 DB 再供前端讀**，不讓前端直接打第三方 API——控 FinMind rate limit、建立自有資料層、金融資料一致性。

---

## 四、學到的觀念/知識（程式 & 金融）

### 2026-06-10 22:15 [claude] [金融] 觀念
**技術指標白話（金融）。** MA=趨勢均價、RSI=超買超賣溫度計（>70 熱、<30 冷）、MACD=漲跌動能、KD=收盤價在近 9 日高低區間的位置。面試談資：「從不懂股票，到親手實作這些指標來真正理解其意義」。

### 2026-07-19 17:30 [claude] [全端] 觀念
**串 MySQL 過程學到的核心觀念（濃縮）。**
- **資料層抽象（面試亮點）**：程式碼一行未改，只改 `.env` 的 `DATABASE_URL` 一行，資料就從 SQLite 改灌 MySQL、API 照常——SQLAlchemy(ORM) 把「用哪種 DB」抽象掉。
- **Vite proxy**：dev 時前端 5173、後端 8000 是「不同來源」會被瀏覽器 CORS 擋；Vite 把 `/api` 開頭的請求「代轉」到 8000，瀏覽器以為只跟 5173 講話 → 不觸發 CORS。前端 `load()→getStocks()(axios GET /api/stocks)→stocks.value→渲染`，proxy 就藏在那一次 axios 發送。
- **Vue3 `ref<Stock[]>([])`**：`ref`=會通知畫面重繪的「智慧盒子」；`[]`=初始空陣列；`<Stock[]>`=TS 型別註記。`<script>` 內用 `.value` 存取、`<template>` 自動拆箱；≈ Vue2 的 `this.stocks`。
- **TS interface vs Java interface**：TS interface 只描述「資料長相」、編譯後消失（結構型別，鴨子測試）；Java interface 是「行為合約」、執行期存在（名目型別，需 `implements`）。
- **`.env` vs `.env.example`**：程式只讀 `.env`（被 gitignore、放真值）；`.env.example` 是給人照抄的範本、會進 git、只放佔位字串（本次曾誤改到 example 而不生效）。
- **最小權限**：連線用 `stock_user`（僅 stock_db 有權）而非 `root`，字串外洩傷害面較小。

---

## 五、實測結果（證明真的會動）

### 2026-06-10 22:10 [claude] [後端] 實測
```
搜尋 2330 → 台積電 / 半導體業 / 上市
2330 近一年 K 線 250 天，最後一根：開2285 收2255 低2255 高2300（2026-06-10）
指標末值：MA5=2321  MA20=2297  MA60=2114  RSI=48  KD=37/53
漲幅榜：大立光 +6.31%、中華電 +1.41%
```
（此次為 API／後端層實測；前端尚未 `npm install` 跑起來。）

### 2026-07-04 17:06 [claude] [後端] 實測
擴充後 DB 驗證：`stocks` 表 **3115 檔**（可搜尋全台股）、**51 檔有日線**（台灣50 + 原 0050）、日線共 **24842 筆**；抽查搜尋「台積」1 檔、「鋼」15 檔皆正常。台灣50 在 FinMind 匿名額度下 **50/50 檔抓取成功**。

### 2026-07-19 17:30 [claude] [後端] 實測
**MySQL 8.4.8 串接端到端驗證（資料源＝MySQL，非 SQLite）：**
```
DB：mysql+pymysql → 127.0.0.1:3306/stock_db（VERSION 8.4.8）
stocks 3088 檔可搜尋（較 SQLite 版 3115 少 27＝過濾掉的指數列）
daily_prices 24570 筆、涵蓋 51 檔；2330 最新一根 2026-07-17 收 2290
API：/api/stocks?q=2330→台積電、中文「台積」→台積電、/api/rankings→兆豐金+2.15%…、/api/stocks/2330/prices→K線+指標　皆正常
seed 冪等：已存在的 10 檔日線「新增 0 筆」（upsert 跳過），台灣50 50/50 成功
```

---

## 六、現況與下一步（隨進度更新，配合 README.md）

- **後端**：完成且已驗證；**搜尋涵蓋全台股、台灣50 有 K 線資料**；**已可切換並實跑於 Docker MySQL 8.4**（SQLite/MySQL 皆通）。照 `README.md` 即可啟動。
- **前端**：程式碼齊全，待 `cd frontend && nvm use 20 && npm install && npm run dev`。
- **待辦**：~~擴充更多股票~~（✅ 2026-07-04）→ ~~串接 Docker MySQL~~（✅ 2026-07-19）→ **下一步：加財報基本面** → 最後用 Spring Boot 重寫後端做對照。
