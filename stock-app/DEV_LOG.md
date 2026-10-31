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
> - **⚠️ 減少合併衝突的寫法約定**（前後端兩條線都會改這份，實測常在 DEV_LOG 撞衝突）：
>   1. **各寫各的「新增」條目**：一到六大點都用「追加新 `###` 區塊」的方式記，**不要去改別人既有的行**——新增不會衝突、改同一行才會。
>   2. **「六、現況」前後端分行寫**：後端狀態、前端狀態**各自獨立一行**（`- **後端**：…` / `- **前端**：…`），各自只改自己那行，避免兩邊搶同一行。
>   3. **降低整合頻率**：功能分支完成合回「角色主線」即可；**角色主線 → `stock-app/main` 只在里程碑做一次**（累積數個功能再上），不要每個小功能都往上合（往上合越頻繁、DEV_LOG 越常撞）。

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

### 2026-10-17 [claude] [後端] 完成
新增**財報評價基本面**第一塊：PER（本益比）/ PBR（股價淨值比）/ 殖利率。後端按既有四層對稱擴充——`models.Valuation` 表、`data_fetcher.fetch_per_pbr`+`upsert_valuation`、`schemas.ValuationOut`、API `GET /api/stocks/{id}/valuation`，`seed.py` 讓台灣50 順抓近一年評價資料。資料源 FinMind `taiwan_stock_per_pbr`（一個接口同時給三個指標）。

### 2026-10-19 [claude] [前端] 完成
評價指標**上前端**：個股頁（`StockDetailView.vue`）K 線上方新增「基本面」卡片，顯示最新 PER/PBR/殖利率，各欄位附 tooltip 白話說明（延續零基礎友善風格）。`api/index.ts` 加 `Valuation` 型別與 `getValuation()`。評價獨立抓取並容錯：抓不到只是不顯示卡片、不影響 K 線。台積電/鴻海個股頁實際瀏覽器驗證卡片正常顯示。

### 2026-10-20 [claude] [後端] 完成
新增**季度財報 EPS（每股盈餘）**。因財報是「每季」頻率（非每日），獨立開 `models.Financial` 表（不塞進每日的 valuations）；`data_fetcher.fetch_financials`（篩 FinMind 長格式 `type==EPS`）+ `upsert_financials`、`schemas.FinancialOut`、API `GET /api/stocks/{id}/financials`（預設近 12 季），`seed.py` 台灣50 順抓近 3 年 EPS。資料源 FinMind `taiwan_stock_financial_statement`。

### 2026-10-21 [claude] [前端] 完成
**EPS 上前端**：個股頁「基本面」卡片在 PER/PBR/殖利率下方新增一排 **EPS 季度趨勢長條圖**（近 8 季），每根 hover 顯示年月+EPS，一眼看出獲利成長/衰退。`api/index.ts` 加 `Financial` 型別與 `getFinancials()`。小圖用純 CSS flex 繪製（不為小圖另開 ECharts）；長條高度用 `computed` 依最大 EPS 算相對比例。台積電個股頁瀏覽器驗證：8 季由舊到新遞增、hover 正常。

### 2026-10-22 [claude] [後端] 完成
新增**每月營收**（第三種頻率：每月，繼每日評價、每季 EPS 之後）。獨立開 `models.Revenue` 表（`(stock_id,year,month)` 唯一，只存原始營收金額）；`data_fetcher.fetch_revenue`+`upsert_revenue`、`schemas.RevenueOut`、API `GET /api/stocks/{id}/revenue`。**YoY（年增率）/ MoM（月增率）不存 DB、在 API 即時計算**。`seed.py` 台灣50 順抓近 3 年。資料源 FinMind `taiwan_stock_month_revenue`。

### 2026-10-31 [claude] [前端] 完成
月營收上前端（基本面卡片新增「月營收 YoY」長條圖，正紅負綠）；並做**全站手機 RWD** 與**總覽列表重構**：header/兩欄佈局/K線 tooltip 與量軸、長條圖橫滑都修好手機跑版；總覽改分頁（每頁 10 筆）、拿掉「看圖」（點列進詳情）、手機加自選改代號前星星 icon、星星顯示「已加入」實心狀態；自選股移除改紅叉 icon 並點列進詳情；排行榜可開合＋手機移到列表上方。

### 2026-10-31 [claude] [後端] 完成
rankings 效能優化：原本遍歷全台 3088 檔逐檔查 DB（N+1），改為只遍歷有日線的約 50 檔，4.5s→0.1s。

### 2026-10-31 [claude] [Java後端] 完成
**啟動 Spring Boot 版後端（新角色 `backend-java/`，對照 Python FastAPI 版）**：Spring Boot 3.4.1 + JDK 21 + Maven Wrapper；三層架構 Entity(`Stock`)/Repository(`StockRepository`)/Controller(`StockController`) 寫出第一支 `GET /api/stocks?q=`。連**同一個 MySQL `stock_db`**（讀 Python 版灌好的資料，不重 seed），跑在 **8081** 埠。實測與 Python 版（8000）回傳**完全相同的 JSON**（含中文搜尋）。環境搭建雷另記於 `CLAUDE_CODE_SETUP_GUIDE.md`。

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

### 2026-10-31 [claude] [後端] 雷
**漲跌排行每次都慢 4~5 秒（N+1 查詢）。**
- **現象**：進出任一股票回到總覽，排行榜都要重算、等 4~5 秒。
- **原因**：rankings 用 `for s in db.query(Stock).all()`（全台 3088 檔）再逐檔查最近 2 筆日線——這是 N+1；但其實只有約 50 檔有日線，掃其餘 3000+ 檔全是白工。
- **解法**：先 `db.query(DailyPrice.stock_id).distinct()` 取「有日線」的代號（約 50），只對這些算。實測 **4.5s → 0.1s（快 45 倍）**。

### 2026-10-31 [claude] [前端] 雷
**console 狂噴 error 以為程式壞了，其實是瀏覽器擴充。**
- **現象**：DevTools 累積上千 error、感覺「背景一直在跑」。
- **原因**：訊息是 `extensionAdapter.sendMessageToTab`、`inlineForm...doNotRemove`、`You do not have a background page`——都是瀏覽器**擴充套件**注入頁面報的，與 app 無關。
- **解法／判斷**：用**無痕視窗**（擴充停用）開 app，console 即乾淨。排錯時先認清 error 來源（我方程式 vs 擴充／第三方），別被誤導。

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

### 2026-10-17 [claude] [金融] 觀念
**財報評價指標白話（金融）。** K 線看「行情」，評價指標看「體質／貴不貴」：
- **EPS 每股盈餘**：公司每一股幫你賺多少錢，越高越會賺。
- **PER 本益比** = 股價 ÷ EPS：你付的價格是它一年獲利的幾倍，判斷「貴不貴」（相對低＝相對便宜）。
- **PBR 股價淨值比** = 股價 ÷ 每股淨值：股價相對公司「家底」幾倍。
- **殖利率(%)** = 年配息 ÷ 股價：把錢放這檔一年領幾 % 股息，存股族最看。
- 這些**逐日變動**（分母的 EPS/淨值短期固定，分子股價天天動）。虧損公司 PER 無意義（可能為負或空），所以欄位允許 null。

### 2026-10-17 [claude] [後端] 觀念
**後端分層設計（加 valuation 時的實作心法）。**
- **fetch 與 upsert 單一職責**：`fetch_per_pbr` 只負責「抓＋把外部欄位翻譯成自家格式」（大寫 `PER`→`per`），`upsert_valuation` 只負責「寫 DB、跳過已存在」。拆開後換資料源只改 fetch、換 DB 只改 upsert，好測好維護。
- **schema＝後端版的「資料長相合約」**：`ValuationOut`（Pydantic）規定 API 回傳 JSON 的欄位，自動驗證＋自動產 `/docs` 文件——概念同前端 TS interface，但執行期會真的驗證。
- **冪等 upsert**：靠 `(stock_id, date)` UniqueConstraint ＋ 先撈 existing 再跳過，重複跑不產生重複列。

### 2026-10-19 [claude] [全端] 觀念
**前後端有相依時，後端要先往上合到「共同主線」，前端分支才拿得到。**
- **現象**：前端分支（自 `stock-app/main` 開）要顯示評價，但在這個工作樹打 API 卻 404、路由消失。
- **原因**：valuation 後端當時只在 `stock-app/back-end/main`，還沒合進 `stock-app/main`；而「**一個資料夾同一時間只攤開一條分支**」——切到前端分支後，整個資料夾（含 backend）都是前端分支的版本，那裡的 `routers/stocks.py` 是沒有 valuation 的舊版，`--reload` 還因此熱載成舊版。
- **解法／心法**：先把後端那塊 `back-end/main → stock-app/main`（里程碑往上合），前端分支再 `git merge stock-app/main`，工作樹就同時具備前後端新程式。**跨角色相依的功能，整合點要上移到兩者共同的主線。**

### 2026-10-20 [claude] [程式] 觀念
**資料頻率決定「存去哪張表」＋ pandas 長格式篩選（加 EPS 時學到）。**
- **每日 vs 每季分表**：PER/PBR/殖利率是每日資料（放 `valuations`），EPS 是每季資料（放 `financials`）。硬塞同一張表會有大量空值；依「資料更新頻率」分表，每張表乾淨、查詢也單純。這也影響 API 預設筆數（valuation `limit=60` 天、financial `limit=12` 季）。
- **寬格式 vs 長格式**：`per_pbr` 是寬格式（一列含 PER/PBR/殖利率多欄）；`financial_statement` 是長格式（每個財報項目一列，用 `type` 欄標示）。長格式要先篩：`df[df["type"]=="EPS"]` 這招叫**布林遮罩**——`df["type"]=="EPS"` 產生一串 True/False，`df[布林]` 只留 True 的列，等同 SQL 的 `WHERE type='EPS'`。

### 2026-10-21 [claude] [前端] 觀念
**Vue3 `computed` 計算屬性 ＋ 不為小圖殺雞用牛刀。**
- **`computed`**：根據 `ref` 自動算出衍生資料（這裡把後端「由新到舊」的 EPS 反轉成「由舊到新」、並算每根長條相對高度%）。來源 `ref` 一變就自動重算、畫面自動更新，不必手動同步——等同 Vue2 的 computed，寫法改為 `computed(() => {...})`。
- **選圖的務實判斷**：K 線那種複雜互動圖才用 ECharts；EPS 這種「幾根長條看趨勢」的小圖，用純 CSS flex（高度綁 `heightPct`）更輕量、好懂、不必再開一個圖表實例。技術選型看需求、不是越重越好。

### 2026-10-22 [claude] [程式＋金融] 觀念
**衍生值即算不存＋YoY/MoM 的計算與跨年邊界（加月營收時學到）。**
- **原始值存 DB、衍生值即算**：月營收只存原始金額，YoY/MoM 在 API 回傳時算。因為成長率是「推導得出」的值，存了反而有「資料不一致」風險（改了 revenue 忘了改成長率）；即算永遠正確。
- **成長率白話（金融）**：`YoY 年增率`＝跟**去年同月**比（排除淡旺季，看真實成長，最常看）；`MoM 月增率`＝跟**上個月**比（短期動能）。公式 `(本期−基準)/基準×100`。
- **查表加速**：算 YoY/MoM 要反覆找「去年同月/上個月」，先把全部撈成 `{(年,月):營收}` dict，查詢 O(1)——用空間換時間。
- **跨年邊界雷**：1 月的「上個月」是**去年 12 月**不是「0 月」；`month==1` 要特判成 `(year-1, 12)`，否則 1 月的 MoM 永遠算錯。除法前也要擋 base 為 0/None（最早幾個月沒有 YoY 屬正常，回 null）。

### 2026-10-22 [claude] [全端] 觀念
**多分支共用文件的合併衝突，與減少衝突的習慣（協作經驗，面試可聊）。**
- **現象**：每做一個前端功能、把前後端往上合進 `stock-app/main` 時，`DEV_LOG.md` 幾乎每次都衝突（程式碼反而不衝突）。
- **原因**：前後端兩條線都在改**同一份 DEV_LOG 的同一區域**（尤其「六、現況」那幾行）。git 合併時「兩邊改同一行」就會衝突；「各自新增不同行」則能自動合。
- **解法／習慣**（已寫入本檔開頭「減少合併衝突的寫法約定」）：① 只「追加新 `###` 條目」不改別人既有行；② 「六、現況」前後端**分行**各寫各的；③ **降低往上整合的頻率**（功能合回角色主線即可，角色→專案主線只在里程碑做）。
- **延伸**：這就是真實團隊「為什麼要約定文件/程式的編輯慣例」——降低 merge conflict 是協作效率問題，不只是技術問題。

### 2026-10-31 [claude] [前端] 觀念
**手機 RWD 與互動細節（做月營收 UI 時順手修全站）。**
- **寬內容自己捲**：長條圖/表格用 `overflow-x` 在自身容器捲動，`body` 不橫向跑版。
- **斷點與順序**：兩欄佈局用 Element 斷點 `:xs/:sm/:md`（手機整行堆疊）；堆疊順序可用 flex `order` 調換，不動 DOM（桌面維持原佈局）。
- **大數字與浮框**：成交量用 formatter 縮成「億/萬」避免被 Y 軸寬度裁切；ECharts tooltip `confine:true` 把浮框限制在容器內不外溢。
- **`ref<Set>` 要重新賦值**：Vue3 `ref<Set>` 直接 `.add()` 不會觸發畫面更新，要 `new Set(舊).add(x)` 重新賦值（星星「已加入」狀態就是靠這更新）。
- **N+1 查詢**：後端 rankings 的教訓——「迴圈裡逐筆查 DB」在資料量大時會很慢，先縮小迴圈範圍（只查有資料的）或改一次查詢。

### 2026-10-31 [claude] [Java後端] 觀念
**Spring Boot 三層架構，對照 Python FastAPI（學 Java 的切入點）。**
- **Entity（`@Entity`）≈ SQLAlchemy model**：一個 class 對一張表，欄位用註解映射；`stockId`（Java 駝峰）靠 `spring.jackson.property-naming-strategy=SNAKE_CASE` 輸出成 `stock_id`，和 Python 版 JSON 一致 → **同契約、兩實作**，同一前端通用。
- **Repository（`extends JpaRepository`）≈ db.query**：只寫 interface、不寫實作，Spring Data **自動生出** findAll/save… 比 SQLAlchemy 還自動；自訂搜尋用 `@Query`（類 SQL 的 JPQL）。
- **Controller（`@RestController`/`@GetMapping`）≈ FastAPI router**：註解即路由；建構子注入 Repository ≈ FastAPI 的 `Depends`。
- **核心差異感受**：Java/Spring 大量用**註解驅動**＋**依賴注入**，比 Python 更「約定大於配置」；型別嚴格、要寫 getter。但三層職責和 Python 版一一對應，觀念可直接遷移。

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

### 2026-10-17 [claude] [後端] 實測
**財報評價 API 端到端驗證（資料源＝MySQL）：**
```
seed：台灣50 評價指標 50/50 檔成功，valuations 共 12100 筆、涵蓋 50 檔
2330 最新：2026-10-16  PER 28.05  PBR 9.76  殖利率 0.91%
API：GET /api/stocks/2330/valuation?limit=3 → 正確回近 3 日 PER/PBR/殖利率
     查無資料的 9999 → 正確回 404「請先執行 seed.py 匯入」
```

### 2026-10-20 [claude] [後端] 實測
**EPS 財報 API 端到端驗證（資料源＝MySQL）：**
```
seed：台灣50 財報 50/50 檔成功，financials 共 550 筆（50 檔 × 11 季）
2330 近 4 季 EPS：27.25 / 22.08 / 19.51 / 17.44（由新到舊，逐季成長）
API：GET /api/stocks/2330/financials?limit=4 → 正確回近 4 季 EPS
     查無資料的 9999 → 正確回 404
```

### 2026-10-22 [claude] [後端] 實測
**月營收 API 端到端驗證（含即時 YoY/MoM，資料源＝MySQL）：**
```
seed：台灣50 月營收 50/50 成功，revenues 共 1800 筆（50 檔 × 36 月）
2330 2026/9：營收 5119 億  YoY +54.65%  MoM -0.57%
     2026/8：營收 5148 億  YoY +53.32%  MoM +10.1%
手算驗證 MoM：(5119-5148)/5148 = -0.57% ✓
查無資料的 9999 → 正確 404
```

### 2026-10-31 [claude] [後端] 實測
rankings 優化前後（同機連測 3 次）：**4.99s / 4.60s / 4.44s → 0.12s / 0.10s / 0.09s**；回傳內容一致（緯創 +5%…）。

### 2026-10-31 [claude] [Java後端] 實測
**Spring Boot 版第一支 API 與 Python 版並排對照（讀同一個 MySQL）：**
```
Java   (8081) GET /api/stocks?q=2330 → [{"stock_id":"2330","name":"台積電","industry":"電子工業","market":"上市"}]
Python (8000) GET /api/stocks?q=2330 → [{"stock_id":"2330","name":"台積電","industry":"電子工業","market":"上市"}]
兩者回傳「完全相同」；中文搜尋「台積」、空搜尋前 50 筆也正常。
```

---

## 六、現況與下一步（隨進度更新，配合 README.md）

- **後端（Python）**：完成且已驗證；**搜尋涵蓋全台股、台灣50 有 K 線＋評價指標（PER/PBR/殖利率）＋季度財報（EPS）＋每月營收（含 YoY/MoM）**；rankings 已優化（4.5s→0.1s）；**已可切換並實跑於 Docker MySQL 8.4**（SQLite/MySQL 皆通）。照 `README.md` 即可啟動。
- **前端**：K 線/搜尋/自選股已點測正常；基本面卡片（PER/PBR/殖利率）＋ EPS 趨勢圖＋**月營收 YoY 圖**皆已呈現；**全站手機 RWD＋總覽分頁/星星已加入狀態/排行榜開合**均已完成並實測。
- **後端（Java，`backend-java/`）**：Spring Boot 3.4.1 骨架 + 第一支 `GET /api/stocks` 已跑通（8081，讀同一 MySQL、JSON 與 Python 版一致）。**下一步：逐支翻譯 prices/valuation/financials/revenue/rankings/watchlist**。
- **待辦**：~~擴充更多股票~~（✅ 2026-07-04）→ ~~串接 Docker MySQL~~（✅ 2026-07-19）→ ~~評價指標 PER/PBR/殖利率（後端+前端）~~（✅ 2026-10-17～19）→ ~~EPS（後端+前端）~~（✅ 2026-10-20～21）→ ~~月營收（後端+前端）~~（✅ 2026-10-22～31）→ ~~手機 RWD＋UX 優化＋rankings 效能~~（✅ 2026-10-31）→ ~~Spring Boot 骨架+第一支 API~~（✅ 2026-10-31）→ **下一步：Spring Boot 逐支翻譯其餘 API**。
