# Claude Code 安裝與使用說明書

> 用途：把搭建／使用 Claude Code（含網頁版 Claude Code on the web）過程中踩過的雷、流程、工具搭配記錄下來。
> 之後換電腦、重裝環境、或開新專案時，照這份走即可，不必再從頭摸索。
> 本檔**不含任何專案程式碼**，只記「環境與工具」層級的東西。
>
> 名詞先白話：
> - **Claude Code CLI**：裝在你電腦終端機裡的指令工具，在本機跑。
> - **Claude Code on the web（網頁版）**：在 `claude.ai/code` 上，程式跑在 Anthropic 的雲端機器（用完即丟的沙盒），手機 App 也能看同一個 session。
> - **session**：一段對話／工作階段。
> - **repo**：GitHub 上的程式碼倉庫。

---

## 0. 先備齊的東西

| 項目 | 說明 |
| :--- | :--- |
| Anthropic 訂閱 | Claude Code on the web 屬 research preview，需 **Pro / Max / Team**（或 Enterprise premium）方案。 |
| GitHub 帳號 | 雲端 session 要靠它 clone 程式碼、推送分支。 |
| 本機終端機 | macOS 內建 Terminal 即可。 |
| Node.js | 裝 Claude Code CLI 與多數前端專案會用到。 |

---

## 1. 安裝 Claude Code CLI（本機）

```bash
# 官方安裝（擇一，依官方文件為準）
npm install -g @anthropic-ai/claude-code
# 或使用官方安裝腳本（見官方文件）

# 啟動
claude

# 在 CLI 內登入 claude.ai 帳號（這步很重要，teleport / web-setup 都需要）
/login
```

- 若 `--teleport` 等功能說「unavailable」，多半是你用 API key／Bedrock／Vertex 登入，而非 claude.ai 訂閱。請 `/login` 改用 claude.ai 帳號。
- CLI 太舊也會缺功能：`claude update`。

---

## 2. 安裝 GitHub CLI（gh）並登入

`gh` 是 GitHub 官方命令列工具，之後 `/web-setup`、`--autofix-pr` 等會用到。

```bash
# macOS（Homebrew）
brew install gh

# 登入（會開瀏覽器授權）
gh auth login
#   選 GitHub.com → HTTPS → 用瀏覽器登入即可
```

驗證：

```bash
gh auth status     # 看到 Logged in to github.com 就 OK
```

---

## 3. 把 GitHub 連到 Claude Code on the web（兩種方式，擇一）

雲端 session 需要存取你的 repo。官方有兩條路：

### 方式 A：GitHub App（適合用瀏覽器、想要 Auto-fix 的人）
1. 到 `claude.ai/code` 登入。
2. 依提示**安裝官方 Claude GitHub App** 並授權你的 repo。

### 方式 B：`/web-setup`（適合已在用 gh 的個人開發者）
1. 先完成第 2 步（`gh auth login`）。
2. 在 Claude Code CLI 內：`/login` → 然後 `/web-setup`。
3. 它會把你本機的 `gh` token 同步到 Claude 帳號，並建立一個預設雲端環境。

> 注意：`/web-setup` 是在 **Claude Code CLI 裡**打，不是在一般 shell 打。打錯會顯示 Unknown command。

---

## 4. ⚠️ 最大的雷：GitHub App「Authorized ≠ Installed」（推送 403 的元兇）

這是我們卡最久的地方，務必看懂。

### 症狀
- 雲端 session 可以讀 repo、列出 repo 清單，但**一 push 就失敗**：
  - `git push` → `remote: Permission ... denied` / `403`
  - 透過 GitHub 整合 → `403 Resource not accessible by integration`

### 原因（白話）
GitHub 對一顆 App 有**兩件不同的事**：

| 狀態 | 在哪看 | 意思 |
| :--- | :--- | :--- |
| **Authorized（已授權）** | Settings → Applications → **Authorized GitHub Apps** | App「認得你是誰」、看得到你看得到的 repo（所以清單跑得出來） |
| **Installed（已安裝到 repo）** | Settings → Applications → **Installed GitHub Apps** | App 被「裝進某個 repo 並拿到**寫入權**」，才能 push |

> 只有「Authorized」而沒有「Installed」→ 只能讀不能寫 → push 一律 403。
> （另外 **Authorized OAuth Apps** 又是第三種東西，例如 VS Code 會在那；跟這個無關，別動它。）

### 解法
1. 開官方安裝頁：**https://github.com/apps/claude**（發行者是 **Anthropic**）。
2. 按 **Install / Configure** → 選你的帳號 → **Only select repositories** → 勾選目標 repo（或 All repositories）→ 確認。
3. 回 `github.com/settings/installations` 確認 **Installed GitHub Apps** 裡出現 **Claude**，且 Repository access 含你的 repo。

> 🚫 **不要去 GitHub Marketplace 搜尋 "Claude Code" 自己亂裝**——那裡有一堆同名第三方仿冒，裝錯等於把 repo 授權給陌生人。官方那顆就叫 **Claude**，從上面網址或 `claude.ai/code` 的連接流程進去最安全。
>
> ✅ 實測：把官方 Claude App「Installed」到 repo 後，**連正在跑的雲端 session 都立刻能 push 了**，不必重開。

---

## 5. 雲端 web session 的特性與雷

| 雷 / 特性 | 說明與對策 |
| :--- | :--- |
| **容器用完即丟** | 雲端機器是臨時的，閒置一陣子會被回收。**沒 push 上 GitHub 的 commit 會永久消失。** 重要變更要儘早 push（或在本機做）。 |
| **網路是白名單** | 預設 `Trusted` 等級只放行 npm／PyPI 等套件源，**封鎖一般外網**。所以 Cloudflare／ngrok 之類的「通道服務」連不出去。 |
| **不能 QR 到手機看畫面** | 承上：雲端 session 無法開對外網址，**無法在外面用手機掃 QR 直接看雲端跑的網站**。要手機預覽 → 見第 7 點。 |
| **權限可能是唯讀** | 若 GitHub App 沒 Installed（見第 4 點），session 就是唯讀，推不動。 |
| **互動式指令受限** | 雲端 session 不支援會開互動選單的指令（如 `/model`、`/config`）。 |

---

## 6. CLAUDE.md：讓每個新 session 自動「記得」你的偏好與背景

雲端 session 每次都是**重新 clone 一份乾淨 repo**，所以你裝在自己電腦上的個人設定它看不到。要讓「每個新 session 開場就先參照某些內容」，正規做法是：

- 在 **repo 根目錄放一個 `CLAUDE.md`**，它會在每個 session 啟動時**自動載入**。
- 用 `@檔名` 語法引入其他檔，維持單一來源，例如：

```markdown
# CLAUDE.md
## 開發者背景
@ABOUT_ME.md
## 開發行為規範
@DEVELOPMENT_RULES.md
## 記錄分流
專案細節 → 各專案 DEV_LOG.md；跨專案摘要 → 根目錄 @DEV_LOG.md；環境/工具雷 → 本搭建指南。
```

- 搭配檔案（本 repo 實際採用，皆以 `@` 從 `CLAUDE.md` 引入，維持單一來源）：
  - `ABOUT_ME.md`：開發者背景與溝通偏好。
  - `DEVELOPMENT_RULES.md`：開發行為規範（Git／分支策略、開發流程、記錄分流）。
  - `DEV_LOG.md`：**兩層**——根目錄放各專案「簡要摘要」；各專案資料夾放自己的詳細 `DEV_LOG.md`（完成/雷/決策/觀念/實測，帶時間戳與歸屬）。跟著 Git 走，**本機／雲端／subagent 寫的都是同一份**。
  - `CLAUDE_CODE_SETUP_GUIDE.md`：環境／工具搭建的雷（就是本檔）。
  - ⚠️ 確切格式與分流規則**以各檔本身為準**，其他檔只引用、不重抄，避免多處走鐘。
- ⚠️ **自動載入發生在「新 session 開場」讀檔**（現有 session 不會中途重載）；且要讓「預設從 `main` 開」的新 session（尤其雲端／網頁版）吃到，這些檔**必須先合併進 `main`**。
- ⚠️ **已經在跑的雲端 session 不會自動吃到後來的更新**（它手上是當初 clone 的舊版：舊 `ABOUT_ME`、舊分支策略…）。
  要讓它同步，用 [`SYNC_ONLINE_SESSION.md`](SYNC_ONLINE_SESSION.md) 裡那段現成訊息**貼給它跑**即可（含同步指令、分支改名、注意事項）。

---

## 7. 想在手機／實機看畫面怎麼辦

因為雲端 session 開不了對外網址（第 5 點），要在手機看畫面有兩條路：

- **本機跑（最單純、最私密）**：在自己電腦上跑 dev server，讓它綁區網位址，手機連**同一個 Wi-Fi** 就能看。
  - 以 Vite 為例：`server.host = true`，再裝 `vite-plugin-qrcode`，啟動時終端機會印出可掃的 QR，手機掃 QR 或輸入它顯示的 `http://192.168.x.x:5173` 即可。
- **部署到正式主機**：打包後發佈到 GitHub Pages／Vercel／Cloudflare Pages，得到永久網址，任何手機隨時可開（注意：純前端部署時，後端 API 要另外處理）。

---

## 8. 網頁版 ⇄ 本機終端機 互通（teleport / remote）

| 方向 | 指令 | 說明 |
| :--- | :--- | :--- |
| **雲端 → 本機**（延續網頁到本機） | `claude --teleport`（新終端機）<br>或 CLI 內 `/teleport`（`/tp`） | 把某個雲端 session 的「對話歷史 + 分支」拉到本機繼續。 |
| **本機 → 雲端** | `claude --remote "任務描述"` | ⚠️ 這是**另開一個全新**雲端 session，**不是**延續既有本機 session。它從 GitHub clone 你目前分支，所以**先 push**。 |

**方向性結論**：CLI 的接力是**單向**的——可以把雲端拉下本機（teleport），但**不能**把既有本機 session 推上雲端。（要從本機把現場帶上雲，只能用 Desktop App 的「Continue in」選單。）

### teleport 前置條件
- 在**同一個 repo 的 checkout**下執行（不能是 fork）。
- **git 狀態要乾淨**（有未提交變更會要你先 stash）。
- 雲端 session 的**分支必須已 push 到遠端**（teleport 會自動 fetch + checkout）。

### ⚠️ 不覆蓋掉「本機正在跑的 session」的做法
- **不要**在那個還在跑的 session 裡打 `/tp`（會把它切換成雲端內容，蓋掉現場）。
- 改用**獨立工作目錄**承接，原 session 完全不受影響：

```bash
git fetch origin <雲端分支>
git worktree add ../專案-web <雲端分支>   # 開一個獨立資料夾，掛在該分支
cd ../專案-web
claude --teleport                          # 或在網頁點「Open in CLI」複製現成指令
```

> 原理：teleport 會 `git checkout` 分支，而 git 分支狀態是「跟著資料夾」的。給雲端 session 一個獨立資料夾（worktree 或另 clone），兩邊就不會互相切分支打架。

---

## 9. 開新專案的搭配流程（推薦順序）

1. **GitHub 上先建一個空 repo**（雲端 session 只能用既有的 GitHub repo）。
2. 本機 `git clone` 下來，或在 `claude.ai/code` 選這個 repo。
3. 放入長期參考檔：`CLAUDE.md`（+ `@ABOUT_ME.md`、`@DEVELOPMENT_RULES.md`、`@DEV_LOG.md`）。
4. 確認 GitHub App 已 **Installed** 到這個 repo 並有寫入權（第 4 點）。
5. （雲端）建立／選擇環境：設定 **Network access 等級**、環境變數、setup script。
6. 開始交辦任務；完成後 review diff → 視需要建 PR。
7. 遇到值得記的事 → 依 `CLAUDE.md` 的分流規則，寫進對應的 DEV_LOG（專案細節／根摘要）或本搭建指南。

---

## 10. 換電腦 / 重裝 Checklist

**Claude Code / GitHub 工具：**
- [ ] 裝 Node.js（NVM，`nvm install 20`，第 11.4 點）
- [ ] 裝 Claude Code CLI，`claude` → `/login`（claude.ai 帳號）
- [ ] 裝 `gh`，`gh auth login`
- [ ] （要用網頁版）`/web-setup` 或在 `claude.ai/code` 連接 GitHub
- [ ] 確認官方 **Claude** GitHub App 已 **Installed** 到要用的 repo（含 read/write）
- [ ] `git clone` 你的專案，確認根目錄有 `CLAUDE.md`
- [ ] 需要接力雲端 session 時，用 `worktree` + `claude --teleport`

**本機開發環境（做 Python 專案時，第 11 點）：**
- [ ] 先搞清楚 `python3` 是哪版（`python3 -V`），需要時改用 `python3.11 -m venv .venv`
- [ ] venv 獨立於 Anaconda（提示字元無 `(base)`），`which python` 指向 `.venv`
- [ ] `requirements.txt` 鎖好版本；裝完用 `python -c "import 套件"` 實測
- [ ] 舊 macOS 的 Docker Desktop 能跑就別升級（第 11.5 點）
- [ ] 推送 GitHub 用 classic `repo` token；用完去 Developer settings **revoke**（第 12 點）

---

## 11. 本機環境搭建踩雷（macOS Intel + 多套 Python/Node 並存）

> 情境：MacBook Pro 2015 / Intel / macOS Monterey 12.7.6，機器上同時有
> Anaconda、Homebrew Python、NVM、rbenv、Docker。**多套工具並存正是雷的來源。**

### 11.1 ⚠️ Python 有好幾個版本，`python3` 不一定是你要的那個
- 實測：這台機器上 `python3` 指向 **Homebrew 的 Python 3.13**，而 **3.11 藏在 Anaconda 裡**（指令 `python3.11` 可直接叫到，路徑類似 `~/opt/anaconda3/bin`）。
- 為什麼要在意：很多資料科學套件（如 `numpy<2`）在**太新的 Python（3.13）沒有預編譯好的 wheel**，pip 會去硬編譯而失敗。
- **對策**：建虛擬環境時**明確指定版本**，不要無腦用 `python3`：
  ```bash
  python3.11 -m venv .venv      # ← 指定 3.11，不要用 python3（那可能是 3.13）
  source .venv/bin/activate
  python -V                     # 確認真的是 3.11.x
  which python                  # 確認指向 .venv 而不是 Anaconda/Homebrew
  ```
- **判斷指令**：`command -v python3.11`、`python3 -V` 先各跑一次，搞清楚哪個是哪個再動手。

### 11.2 venv 要獨立於 Anaconda（避免 PATH 打架）
- 提示字元前若有 `(base)`，代表 conda 環境是 active 的，容易污染 PATH。
- 用 `python3.11 -m venv` 建出來的 venv **一旦建好就獨立運作**，跟 Anaconda 脫鉤；之後一律用 venv 內的 `python`／`pip`。

### 11.3 ⚠️ Python 套件版本一定要「鎖」——相依地獄是真的
- **不鎖版本的下場**：`pip install` 會抓到一堆**最新但互不相容**的版本。我們實際遇到：
  - 沒鎖 → pandas 被拉到 3.0、指標套件 `ta` 卻被降到 2019 的舊版（API 全變，程式跑不動）。
  - 某些套件相依很「霸道」，會反過來指定 pandas / pydantic / numpy 的版本，跟 FastAPI 等打架。例如資料源套件硬要舊版 `pydantic 1.x`，直接讓需要 `pydantic 2.x` 的 FastAPI 崩掉。
- **三條心法**：
  1. `requirements.txt` 用**鎖好的版本範圍**（自己實測能跑的組合），別讓 pip 隨意挑。
  2. 兩個套件**版本要求互斥**時（A 要 pandas<2.3、B 要 pandas≥2.3），找**交集的「甜蜜點」版本**（例如 pandas 2.3.x 兩邊都收）。
  3. **真的喬不攏，就拿掉那個「製造衝突」的套件**。我們最後把技術指標庫整個拔掉、改用 pandas 手算——衝突消失，還更看得懂原理。
- **小工具**：`pip install` 後務必 `python -c "import 套件"` 實際 import 一次，光看「Successfully installed」不代表跑得動（有套件還會漏宣告相依，例如少裝 `tqdm`）。

### 11.4 Node 用 NVM，選 LTS 就好
- 舊機器（Intel / Monterey）追最新 Node 容易出狀況，**Node 20 LTS** 最穩：
  ```bash
  nvm install 20 && nvm use 20
  ```
- 不必追 Node 22+；Vite 5 只要 Node 18+ 即可。

### 11.5 Docker Desktop 別亂升級
- 舊 macOS（如 Monterey）上，**新版 Docker Desktop 可能已不支援**。
- 若你現在的版本能正常跑（容器、phpMyAdmin 都正常），就**維持現狀別升級**，免得升完整個開不起來。

### 11.6 跨資料庫小雷：SQLite 的自增主鍵
- 同一份 ORM 程式想同時支援 SQLite（本機開發）與 MySQL（正式）時：
  **SQLite 只有宣告成 `INTEGER` 的主鍵才會自動遞增**，用 `BigInteger` 會報 `NOT NULL constraint failed: xxx.id`。
- 解法（一份程式兩種 DB 都通）：
  ```python
  from sqlalchemy import Integer, BigInteger
  PK = BigInteger().with_variant(Integer, "sqlite")   # MySQL→BIGINT，SQLite→可自增的 INTEGER
  ```

---

## 12. 本機用 Token 推送 GitHub 的雷（和第 4 點雲端 403 是「不同的 403」）

> ⚠️ 重要區分：
> - **第 4 點的 403**＝**雲端** session 經由 **GitHub App** 推送，App 沒 Installed → `Resource not accessible by integration`。
> - **本節的 403**＝**本機** `git push` 用 **Personal Access Token（PAT）**，token 權限不足或 keychain 憑證搞混 → `Permission ... denied`。
> 兩者解法完全不同，別套錯。

### 症狀
- 本機 `git push` → `remote: Permission to <user>/<repo>.git denied to <user>` / `403`。
- 弔詭點：明明 `gh auth status` 顯示已登入、帳號也是 repo 擁有者。

### 根因（我們實際踩到兩層）
1. **fine-grained PAT 沒給「Contents: Read and write」**——這是最隱蔽的雷。
   - 用 GitHub API 查 repo 會看到 `"permissions": {"push": true, "admin": true}`，**但那是「你這個帳號」對 repo 的權限，不是「token」的權限**。看到 push:true 會以為沒問題，其實 token 本身根本沒勾寫入。
   - **怎麼確認 token 到底能不能寫**（非破壞性探針，失敗不會留檔）：
     ```bash
     curl -s -X PUT -H "Authorization: Bearer <TOKEN>" \
       https://api.github.com/repos/<user>/<repo>/contents/.probe \
       -d '{"message":"probe","content":"cHJvYmU="}'
     # 回 "Resource not accessible by personal access token" → token 沒有 Contents 寫入權
     # 回 含 commit sha → token 可寫
     ```
2. **macOS Keychain 存了舊的 github 憑證**，`git push` 會優先抓那組舊的，把你想用的新 token 蓋掉。

### 解法
- **最省事：改用 classic token**
  - GitHub → Settings → Developer settings → **Personal access tokens → Tokens (classic)** → Generate → **勾最上面那個大項 `repo`** → 複製（`ghp_` 開頭）。`repo` 全範圍一定能 push。
- **想用 fine-grained token**：編輯 token → **Repository permissions → `Contents` 改成 `Read and write`**（不是只選 repo 就好，那一格預設是 No access），並確認 Repository access 含目標 repo。
- **推送時不讓 token 落地、也繞過 keychain**：
  ```bash
  # 用 -c credential.helper= 關掉憑證助手，token 只放在這一次的 URL，不寫進 .git/config
  git -c credential.helper= push "https://<user>:<TOKEN>@github.com/<user>/<repo>.git" main:main
  git remote get-url origin   # 確認 origin 仍是乾淨的無 token 網址
  ```
- **清掉 keychain 裡的舊憑證**（之後想讓它正常記住新 token 時）：
  ```bash
  git credential-osxkeychain erase
  # 接著輸入兩行後按兩下 Enter：
  #   host=github.com
  #   protocol=https
  ```

### 12.1 ⚠️ `gh` 用的是「另一套」憑證，受限 token 會擋住改 PR
- `gh`（pr create/edit/merge 等）用的是它**自己存在 keyring 的 token**，跟 `git push` 用的憑證**是兩套**。
- 若當初是用**受限的 fine-grained token** 登入 `gh`，改 PR 會被擋：
  `GraphQL: Resource not accessible by personal access token (updatePullRequest)`。
- 臨時繞過：`GH_TOKEN=<有 repo 權限的 token> gh pr edit ...`（一次性、不落地）。但**正解是下面的重新授權**。

### 12.2 ✅ 讓 `gh` 與 `git push` 從此順暢（推薦，免再手貼 token）
用**瀏覽器 OAuth 重新登入 `gh`**，拿到完整權限的 token，而且全程不用手貼任何字串：

```bash
gh auth login
#   依序選：GitHub.com → HTTPS → "Authenticate Git with your GitHub credentials?" 選 Yes
#          → "Login with a web browser" → 複製畫面上的一次性代碼 → 到瀏覽器貼上並授權
gh auth setup-git     # 讓 git push 也改用 gh 的憑證（之後 push 不必再帶 token）
gh auth status        # 確認：Token 應是 'gho_' 開頭的 OAuth、scopes 含 repo
```

完成後：`gh pr create/edit/merge` 都能用；`git push` 走 gh 憑證助手；**從此不必再把任何 token 貼到對話或指令列**（最安全的狀態）。

> ⚠️ **`gh auth login` 要在「真正的終端機分頁」跑，不要用 Claude Code 的 `!` 背景模式。**
> 它是互動式（device code + 開瀏覽器），在背景/非互動環境會卡住並失敗：
> `failed to authenticate via web browser: context deadline exceeded`。
> 對策：另開一個終端機分頁手動跑 `gh auth login` + `gh auth setup-git`。因為 gh 把 token 存進**系統 keyring**，授權完後**正在跑的 Claude Code session 直接就能用**（`git push` 會自動走 gh 憑證），不必重開。
> （萬一已經不小心在背景跑了、Claude Code 畫面卡住，脫身步驟見 **§13**。）

### 12.3 🔐 貼過的 token 要不要 revoke？（看暴露風險，不是反射動作）
- 原則：**任何在對話／指令列／log 出現過的 token，視同可能被看到**。但要不要撤銷取決於風險：
  - 可能被別人看到（共用螢幕、會被他人存取的 log、公開 CI）→ **務必 revoke 重建**。
  - 自己的私有 repo、自己掌握的本機 session／transcript → **風險低，是否撤銷由你判斷，不是非撤不可**。
- **更好的是「根本不要貼」**：改用 12.2 的瀏覽器 OAuth + `setup-git`，之後 push／PR 都走 keyring，永遠不必把 token 給任何人 → 也就沒有「貼了要不要撤」的兩難。
- 改用 OAuth 後，那顆手貼過的 token 已用不到，可以順手 revoke 收乾淨。
- 永遠不要把 token commit 進 repo；`.env`、含 token 的 URL 都要在 `.gitignore`。

---

## 13. Claude Code CLI 操作雷：互動式指令卡住、輸入法、如何安全脫身

> 承 §12.2——萬一你（或 Claude）真的在 Claude Code 裡用 `!` 背景模式跑了**互動式指令**（`gh auth login`、`ssh-keygen`、`vim`…），畫面會卡在「等一個永遠等不到的輸入」。以下是脫身 SOP。

### 13.1 ⚠️ 中文輸入法會讓你「英數鍵、連 Esc 都打不進去」
- **症狀**：Claude Code 全螢幕介面下，輸入框**只吃得了中文，英文字母、數字、甚至 `Esc` 都送不進去**，怎麼按都沒反應。
- **原因（白話）**：終端機在這種全螢幕 TUI 下，**中文輸入法（注音／拼音）會先攔截英數鍵**拿去組字，按鍵根本沒送到程式，所以看起來「整個卡死」。
- **對策**：先把**輸入法切回英文（ABC / U.S.）**——按 `Caps Lock`（中文輸入法多半用它切中／英）、或 `Ctrl + Space`、或點螢幕右上角選單列的輸入法圖示。切完英數鍵就正常了，後面的步驟才按得動。

### 13.2 切到英文後，安全脫身步驟
1. 按幾下 `Esc`，關掉畫面上的覆蓋提示（若出現「How is Claude doing this session?」評分列，按 `0` Dismiss）。
2. 打 `/bashes`（或畫面下方提示的 `↓ to manage`）→ 找到那個卡住的背景 shell → 把它 **kill**。
3. 還是完全沒反應 → **連按兩次 `Ctrl + C`** 離開 Claude Code，或乾脆**直接關掉那個終端機分頁／視窗**。
   - 這 **100% 安全**：互動式指令只是在空等輸入，沒有任何破壞性操作在跑，你的**檔案與 git 都在硬碟上、原封不動**，卡住的指令會跟著一起結束。

### 13.3 ✅ 關掉後別怕弄丟對話——用 `--resume` 救回
Claude Code 的對話歷史存在本機，關掉 / `Ctrl+C` 後可以叫回來，**舊 session 不會消失**：
```bash
claude --resume     # 列出過去的 session，挑回剛剛那個接續
# 或
claude -c           # 直接接續「這個資料夾」最近一次對話
```

> **通則（同 §12.2）**：需要你親自互動的指令（device code、按 Enter、選單）一律**自己在終端機分頁跑**，不要丟給 Claude 背景執行；設定好再回 Claude Code 繼續即可。

---

## 14. Auto-fix（自動修 CI／回應 PR 留言）：開關位置與 token 取捨

> 一句話：**Auto-fix 是「網頁版（雲端）」專屬功能**，雲端會在背景盯著 PR 自動動作。**本機 CLI 不會背景跑這個**。

### 14.1 它是什麼、誰在跑
- **Auto-fix** 開啟後，雲端 session 會持續盯一個 PR，遇到 **① CI 檢查失敗 ② 新的 review 留言** 就自動調查並推修正。（坊間說的「address comments」就是它回應 review 留言的那部分，跟修 CI 是同一個功能。）
- **本機 CLI 不會背景監看**；它只能用 `/autofix-pr` 去**啟動一個雲端 session** 來盯——啟動後仍是雲端在跑。
- 所以本機 session 不會自動看到你的 PR 留言；要看得叫它去抓（見 14.4）。

### 14.2 開關在哪（你要的那顆按鈕）
在**網頁版開著某個 PR 時，畫面最上方的「CI 狀態列（CI status bar）」**裡：

| 動作 | 操作 |
| :--- | :--- |
| **開** | 點開 CI 狀態列 → 選 **Auto-fix** |
| **關** | 點開 CI 狀態列 → **取消 Auto-fix 勾選**，或直接跟 Claude 說「停止盯這個 PR」 |

其他開啟方式：終端機 `/autofix-pr`、手機 App 說「watch this PR」、或把 PR 連結貼進 session 叫它 auto-fix。

### 14.3 ⚠️ token 取捨
- 雲端 session 跟你帳號**共用同一份用量／rate limit**；**雲端 VM 不另外收費，但 token 照算**。
- Auto-fix 每被觸發一次（新留言／CI 失敗）就跑一輪、吃 token。
- **建議**：沒在等 CI、沒在收 review 時就**關掉**，需要時再從 CI 狀態列打開。（本機 CLI 則只有你對話的回合才耗 token，不會背景常駐。）

### 14.4 本機 CLI 的等效手動做法（隨叫隨做、可控）
```bash
gh pr view <PR#> --json reviews          # 看 review 留言
gh pr view <PR#> --json statusCheckRollup # 看 CI 狀態
gh pr diff <PR#>                          # 看 diff
```
再自己 `git pull` → 改 → 測 → `git push`。等於手動做 Auto-fix 的事，但**在你掌控下、不會背景偷耗 token**。

📚 來源：官方 [Claude Code on the web — Auto-fix pull requests](https://code.claude.com/docs/en/claude-code-on-the-web.md#auto-fix-pull-requests)、[Limitations / Rate limits](https://code.claude.com/docs/en/claude-code-on-the-web.md#limitations)。

---

## 附錄：常見錯誤訊息對照

| 訊息 | 多半代表 | 解法 |
| :--- | :--- | :--- |
| `403 Resource not accessible by integration` | **雲端** GitHub App 沒 Installed 或無寫入權 | 第 4 點：安裝官方 Claude App 到 repo |
| `Resource not accessible by personal access token` | **本機** PAT 沒有 `Contents` 寫入權 | 第 12 點：用 classic `repo` token，或補 fine-grained 的 Contents R/W |
| `... personal access token (updatePullRequest)` | **`gh`** 用受限 token 登入，不能改 PR | 第 12.2 點：`gh auth login` 瀏覽器 OAuth 重新授權 |
| `Permission to ....git denied`（本機 push 403） | 本機 PAT 權限不足／keychain 抓到舊憑證 | 第 12 點 |
| `Could not read Username ... Device not configured` | 沒有可用憑證又無互動終端可輸入 | 第 12 點：用內含 token 的 URL 推送 |
| `Host not in allowlist`（cloudflared 等） | 雲端網路白名單封鎖 | 第 5 點：改本機跑或部署 |
| `Unknown command`（`/web-setup`） | 在一般 shell 打、或 CLI 太舊 | 在 `claude` 內打；`claude update` |
| `--teleport unavailable` | 非 claude.ai 訂閱登入 | `/login` 改用 claude.ai 帳號 |
| Claude Code 畫面卡住、英數／`Esc` 都打不進去 | 中文輸入法攔截全螢幕 TUI 的英數鍵 | 第 13.1 點：切回英文輸入法（ABC） |
| 互動式指令（`gh auth login` 等）在 `!` 背景模式卡死 | 互動式指令收不到輸入 | 第 13 點：切英文→`/bashes` kill→必要時關終端機→`claude --resume` |
| `Could not resume session ... environment has expired` | 雲端容器已被回收 | 正常現象；改開新 session |
| `NOT NULL constraint failed: xxx.id`（SQLite） | BigInteger 主鍵在 SQLite 不自增 | 第 11.6 點：用 `with_variant(Integer, "sqlite")` |
| pip 裝完仍 `ModuleNotFoundError` / 版本被亂降 | 套件相依衝突、或套件漏宣告相依 | 第 11.3 點：鎖版本、找甜蜜點、必要時拔掉衝突套件 |
| 編譯 numpy/pandas 失敗 | Python 版本太新（如 3.13）沒有 wheel | 第 11.1 點：改用 `python3.11 -m venv` |
