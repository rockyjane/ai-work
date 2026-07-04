# DEV_LOG — ai-work 跨專案開發摘要

> 這份放在 repo 根目錄，是 ai-work 底下**所有專案的開發摘要（簡要）**：一個專案一小段，只記狀態、技術組成與關鍵決策。
>
> - **各專案的詳細紀錄**（現象→原因→解法、實測、現況與下一步）放在**該專案資料夾自己的 `DEV_LOG.md`**。
> - **環境／工具搭建**的雷（Claude Code、gh、Python/Node/venv/Docker）→ [`CLAUDE_CODE_SETUP_GUIDE.md`](CLAUDE_CODE_SETUP_GUIDE.md)。
>
> 用途：日後整理成 Medium 教學或面試談資時，先看這份總覽，再鑽進各專案細節。

---

## stock-app — 台股分析網站（重返金融業面試 DEMO + 學後端）

- **狀態**：後端 MVP 完成並驗證；**搜尋涵蓋全台股（3115 檔）、台灣50 有 K 線**；前端程式碼齊全，待啟動。
- **技術**：FastAPI + SQLAlchemy + 純 pandas 手算指標 + FinMind｜Vue 3 + Vite + ECharts｜DB SQLite⇄MySQL 可切。
- **關鍵決策**：技術指標純 pandas 手算（避開 FinMind 相依衝突）、資料層抽象（一份 ORM 兩種 DB）、行情先進 DB 再供前端。
- **詳細紀錄** → [`stock-app/DEV_LOG.md`](stock-app/DEV_LOG.md)

<!-- 之後每開一個新專案，就在下面新增一小段摘要，細節寫進該專案自己的 DEV_LOG.md -->
