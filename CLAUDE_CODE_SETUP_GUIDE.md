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
開發者的完整背景請見 @ABOUT_ME.md，協助開發時請一併納入考量。

## 開發記錄（DEV_LOG）
專案的共同開發記錄請見 @DEV_LOG.md，遇到重要的雷／觀念／決策請主動依格式追加。
```

- 搭配檔案建議：
  - `ABOUT_ME.md`：你的背景與溝通偏好（如「用繁體中文、術語先白話」）。
  - `DEV_LOG.md`：跨環境／跨 session 共用的開發筆記（雷／觀念／決策）。因為跟著 Git 走，**不管在本機、雲端、或 subagent 寫的都是同一份**，解決「對話歷史會分散又可能被裁切」的問題。
- ⚠️ 這些規則要**合併進 `main`** 後、之後從 `main` 開的新 session 才會自動生效（新 session 預設從 `main` clone）。

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
3. 放入長期參考檔：`CLAUDE.md`（+ `@ABOUT_ME.md`、`@DEV_LOG.md`）。
4. 確認 GitHub App 已 **Installed** 到這個 repo 並有寫入權（第 4 點）。
5. （雲端）建立／選擇環境：設定 **Network access 等級**、環境變數、setup script。
6. 開始交辦任務；完成後 review diff → 視需要建 PR。
7. 遇到雷／觀念／決策 → 請 Claude 依格式追加到 `DEV_LOG.md`。

---

## 10. 換電腦 / 重裝 Checklist

- [ ] 裝 Node.js
- [ ] 裝 Claude Code CLI，`claude` → `/login`（claude.ai 帳號）
- [ ] 裝 `gh`，`gh auth login`
- [ ] （要用網頁版）`/web-setup` 或在 `claude.ai/code` 連接 GitHub
- [ ] 確認官方 **Claude** GitHub App 已 **Installed** 到要用的 repo（含 read/write）
- [ ] `git clone` 你的專案，確認根目錄有 `CLAUDE.md`
- [ ] 需要接力雲端 session 時，用 `worktree` + `claude --teleport`

---

## 附錄：常見錯誤訊息對照

| 訊息 | 多半代表 | 解法 |
| :--- | :--- | :--- |
| `403 Resource not accessible by integration` | GitHub App 沒 Installed 或無寫入權 | 第 4 點：安裝官方 Claude App 到 repo |
| `Permission to ....git denied` (push 403) | 同上，連線唯讀 | 同上 |
| `Host not in allowlist`（cloudflared 等） | 雲端網路白名單封鎖 | 第 5 點：改本機跑或部署 |
| `Unknown command`（`/web-setup`） | 在一般 shell 打、或 CLI 太舊 | 在 `claude` 內打；`claude update` |
| `--teleport unavailable` | 非 claude.ai 訂閱登入 | `/login` 改用 claude.ai 帳號 |
| `Could not resume session ... environment has expired` | 雲端容器已被回收 | 正常現象；改開新 session |
