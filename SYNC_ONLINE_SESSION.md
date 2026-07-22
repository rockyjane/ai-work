# 給「線上 Claude Code session」的同步訊息（範本）

> **這份在幹嘛**：雲端／網頁版 Claude Code 每開一個新 session，都是**當下 clone 一份 repo**。
> 它看到的治理檔（`ABOUT_ME.md`、`DEVELOPMENT_RULES.md`、`.gitignore`…）可能是**舊版**，
> 分支名也常是雲端自動產生的長名（如 `claude/ai-content-side-business-7ijz6u`）。
> 這份就是「**一貼過去，它就會同步更新 + 轉成正確分支命名**」的訊息範本。
>
> **怎麼用**：複製下面 `─── 複製從這裡開始 ───` 到 `─── 複製到這裡結束 ───` **之間的全部文字**，
> 貼進線上 session 的對話框即可。日後換專案／換分支，只要替換裡面的**專案名**與**長名分支名**就能重用。

---

─── 複製從這裡開始 ───

【任務：先同步 main 的治理更新，再依新分支策略重整，才繼續本專案開發】

背景：主庫 `main` 已完成多專案重整與規範定案。你這條分支是雲端自動開的，落後 `main` 很多 commit
（缺：更新後的 `ABOUT_ME.md`、四層分支策略、收窄後的 `.gitignore`）。
你自己那份 `ai-content-studio/` 資料夾的工作**必須保留，不可遺失**。

⚠️ 動手前請先讀完整段，並注意最後的「務必遵守事項」。

── 第 1 步：同步 main 的治理更新 ──
git status                 # 先確認有沒有未提交改動，有的話先 commit 或 stash，不可放著就切分支
git fetch origin
git checkout claude/ai-content-side-business-7ijz6u
git merge origin/main
# ⚠️ 若 ABOUT_ME.md / DEVELOPMENT_RULES.md / .gitignore 出現衝突，一律採用「main 的版本」
#    （這些是治理檔，main 才是唯一真相來源，不要保留你分支上的舊版）

── 第 2 步：務必重讀並遵守（都在 repo 根目錄、新 session 會自動載入）──
- `DEVELOPMENT_RULES.md` ← **分支策略已改成「四層」，務必照新版**（摘要見第 3 步）
- `CLAUDE.md`（記錄分流規則）、`ABOUT_ME.md`（已更新為正確的職涯資歷，別再用舊版內容）

── 第 3 步：改用四層分支命名（本專案名統一用 `ai-content-studio`，與資料夾一致）──
規則：**持久主線一律以 `/main` 收尾，功能一律走 `/feature/<功能>`**，合併由下往上。

  main
  └ ai-content-studio/main                      專案整合主線（自 main 開）
     └ ai-content-studio/<角色>/main            角色主線（自專案主線開）
        └ ai-content-studio/<角色>/feature/xxx  功能分支（自角色主線開）

※ 為什麼主線都要 `/main` 收尾：git 規定**一個分支名不能同時是另一個分支名的「上層資料夾」**。
  若主線叫 `ai-content-studio/designer`，就無法再開 `ai-content-studio/designer/feature/x`（會報
  `cannot lock ref ... exists`）。加上 `/main` 當葉名就能避開，功能分支才掛得上去。
※ 本專案是 **sub-agent 專案、未來會有多個角色**：每新增一個角色（sub-agent），就照
  `ai-content-studio/<角色>/main` 開一條角色主線即可。角色名依實際 sub-agent 自行命名，
  維持**精簡英文小寫**（例：`designer` 繪師、`writer` 編劇）。**不要用雲端自動產生的長亂碼名。**

實作（以某個角色為例，`<角色>`／`<功能>` 請換成實際名稱）：
git checkout origin/main -b ai-content-studio/main
git push -u origin ai-content-studio/main
git checkout ai-content-studio/main -b ai-content-studio/<角色>/main
git push -u origin ai-content-studio/<角色>/main
git checkout ai-content-studio/<角色>/main -b ai-content-studio/<角色>/feature/<功能>

# 把長名分支上的既有工作搬過來（擇一）：
git cherry-pick <長名分支的commit>
#   或
git merge claude/ai-content-side-business-7ijz6u

# ⚠️ 搬完後務必先 push 並「親眼確認新分支上的檔案完整」，確定沒東西遺失，才可以刪長名分支：
git push
git ls-files ai-content-studio | head        # 確認工作真的在新分支上
git push origin --delete claude/ai-content-side-business-7ijz6u   # 確認無誤後才執行

── 第 4 步：開發紀錄分流（每到里程碑就寫，別等最後補）──
- **專案細節** → 寫 `ai-content-studio/DEV_LOG.md`（該專案自己的詳細紀錄：現象→原因→解法、決策、學到的觀念）
- **跨專案摘要** → 到根目錄 `DEV_LOG.md` 補該專案「一行狀態摘要」（根目錄只放簡要，不放細節）
- **環境／工具搭建的雷** → 寫進 `CLAUDE_CODE_SETUP_GUIDE.md` 對應章節

── ⚠️ 務必遵守事項（違反會造成不可逆損失或破壞協作）──
※ 本訊息中的分支規範與各項紅線皆為**摘要**，**正式定義一律以 `DEVELOPMENT_RULES.md` 為準**；
  若兩者有出入，以該檔為準（第 1 步同步完 `main` 後，該檔就是最新版）。
1. **所有合併一律先 `gh pr create` 開 PR 供審、經使用者明確同意才合**，且方向由下往上：
   功能 → 角色主線 → 專案主線 → 儲庫 `main`。**不可自行 merge，也不可跳級直接合進 `main`**。
2. **切／開分支前先把未提交改動收好**（`git add` + `commit`，或 `git stash`），不可放著未提交就切分支。
3. **絕對禁止**：`git reset --hard`、`git push --force`／`-f`、`git clean -f`、`git checkout .`／`git restore .`
   等任何會清除或覆蓋「尚未提交」工作的指令。需要類似操作一律先停下來問使用者。
4. **刪任何分支前**，先確認其內容已合併／已搬到別處且已 push（見第 3 步的確認指令）。
5. **金鑰安全**：`.env` 與任何含密碼／token 的檔案**絕不 commit、不讀取外傳**；
   `docker-compose*.yml` 已被 `.gitignore` 擋掉，不要硬加進版控。程式碼／範例一律用佔位字串。
6. **不擅自安裝套件**：需要新依賴先說明用途、經同意再裝。
7. **回覆一律使用繁體中文**；介紹新技術術語時先用白話解釋一次再講細節。

─── 複製到這裡結束 ───

---

## 維護筆記（這段不用複製）

- **專案名**目前定為 `ai-content-studio`（與現有資料夾名一致，避免資料夾／分支不同名的混亂）。
- **分支四層規範**的正式定義在 [`DEVELOPMENT_RULES.md`](DEVELOPMENT_RULES.md) 的「分支策略」一節；
  這份訊息只是把它「翻譯成給線上 session 的行動指令」，**規範若有更新，請以該檔為準並同步修這裡**。
- 日後若又有新的雲端 session／新專案要接軌，複製同一份訊息、替換下列三處即可重用：
  **① 專案名**（`ai-content-studio`）、**② 長名分支**（`claude/...`）、**③ 專案資料夾名**。
