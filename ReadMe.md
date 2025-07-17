# BlogCommerce

## 專案簡介
BlogCommerce 是一個結合部落格與電商功能的現代化平台，支援內容管理、商品銷售、訂單處理、用戶管理、即時分析等多元功能。

---

## 主要技術架構
- **後端**：Python 3.10+、FastAPI、SQLAlchemy、Alembic、uvicorn
- **前端**：Vue 3、Vite、Ant Design
- **套件管理**：全面採用 [uv](https://github.com/astral-sh/uv) 進行 Python 依賴管理
- **容器化**：Docker 多階段建構

---

## 開發環境安裝與啟動

### 1. 安裝 uv
建議先安裝 uv（如未安裝）：
```bash
pip install --upgrade uv
```

### 2. 建立虛擬環境並安裝依賴
```bash
uv venv .venv
source .venv/bin/activate
uv pip install --requirements pyproject.toml
```

### 3. 啟動後端服務
```bash
uv run run.py
```

### 4. 前端開發（可選）
```bash
cd admin-src
npm install
npm run dev
```

---

## 測試方式

### 執行所有測試
```bash
pytest
```

---

## Docker 部署

### 建立映像檔
```bash
docker build -t blogcommerce-uv .
```

### 啟動容器
```bash
docker run --rm -p 8002:8080 blogcommerce-uv
```
- 預設後端服務會在 8080 port（容器內），可對外映射 8002:8080

---

## 資料庫初始化與遷移

### 新系統（全新安裝）
1. 初始化 Alembic（只需執行一次）
   ```bash
   uv run -m alembic init alembic
   ```
2. 產生初始 migration 檔案
   ```bash
   uv run -m alembic revision --autogenerate -m "Initial migration"
   ```
3. 執行資料庫升級
   ```bash
   uv run -m alembic upgrade head
   ```
4. 寫入初始管理員帳號（預設帳號/密碼）
   - 帳號：admin
   - 密碼：admin123456
   > 系統啟動後，預設會自動建立初始管理員帳號（如有自動建立程式，否則請參考 seed_database.py 或相關腳本）

### 舊有系統（已存在資料庫）
1. 先備份現有資料庫
2. 依照新 pyproject.toml 安裝所有依賴
   ```bash
   uv pip install --requirements pyproject.toml
   ```
3. 產生 migration（如有 schema 變更）
   ```bash
   uv run -m alembic revision --autogenerate -m "Schema update"
   uv run -m alembic upgrade head
   ```
4. 檢查管理員帳號是否存在，若無請手動建立

---

## 重要注意事項
- **所有 Python 依賴皆以 `pyproject.toml` 管理，不再使用 requirements.txt**
- 啟動、遷移、測試等流程皆建議用 uv 指令
- start.sh、Dockerfile 皆已全面支援 uv

---

## 參考指令
- 安裝依賴：`uv pip install --requirements pyproject.toml`
- 啟動服務：`uv run run.py` 或 `uv run -m uvicorn app.main:app --host 0.0.0.0 --port 8002`
- 資料庫遷移：`uv run -m alembic upgrade head`

---

如有問題請參考 todo.md 或聯絡開發團隊。
