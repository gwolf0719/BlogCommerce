# BlogCommerce 專案概觀

這是一個結合部落格與電子商務功能的全端應用程式。

## 技術棧

### 後端

- **框架**: FastAPI
- **語言**: Python 3
- **資料庫**: SQLAlchemy (搭配 `psycopg2-binary`，應為 PostgreSQL)
- **API 驗證**: 使用 `python-jose` 的 JWT (JSON Web Tokens)
- **伺服器**: Uvicorn
- **主要依賴**:
  - `pydantic`: 資料驗證與設定管理
  - `passlib` & `bcrypt`: 密碼雜湊
  - `alembic`: 資料庫遷移
  - `Jinja2`: 伺服器端模板

### 前端

- **框架**: Vue.js 3 (使用 Composition API)
- **語言**: JavaScript
- **UI 元件庫**: Ant Design Vue
- **狀態管理**: Pinia
- **路由**: Vue Router
- **打包與開發工具**: Vite
- **測試**:
  - **單元測試**: Vitest
  - **E2E 測試**: Playwright
- **主要依賴**:
  - `axios`: HTTP 客戶端
  - `@vueup/vue-quill`: 富文本編輯器
  - `marked`: Markdown 解析

## 專案結構

### 後端 (`app/`)

- `main.py`: FastAPI 應用程式的主要進入點，負責整合中介軟體、掛載路由。
- `database.py`: 設定資料庫連線與 SQLAlchemy Session。
- `run.py`: 啟動 Uvicorn 伺服器的腳本。
- `api/`: (此目錄目前為空)
- `models/`: 定義 SQLAlchemy 的資料庫模型。
- `routes/`: 定義 API 的路由和端點。
- `schemas/`: 定義 Pydantic 的資料結構，用於請求和回應的驗證。
- `services/`: 包含業務邏輯的服務層。
- `static/`: 存放靜態檔案。
- `templates/`: 存放 Jinja2 模板。
- `utils/`: 通用工具函式，如日誌記錄器。

### 前端 (`frontend/`)

- `src/main.js`: Vue 應用程式的進入點，初始化 Vue、Pinia 和 Vue Router。
- `src/App.vue`: 根組件。
- `src/router/index.js`: 定義前端路由。
- `src/views/`: 頁面級組件。
- `src/components/`: 可重用的 UI 組件。
- `src/stores/`: Pinia 狀態管理模組。
- `src/utils/`: 前端通用工具，如 `axios` 實例和錯誤處理。
- `vite.config.js`: Vite 的設定檔。
- `vitest.config.js`: Vitest 的設定檔。
- `playwright.config.js`: Playwright 的設定檔。

## 開發與執行

### 後端

- **啟動開發伺服器**:
  ```bash
  # 根據 run.py 的內容，可能是
  python run.py
  # 或是
  uvicorn app.main:app --reload
  ```
  (建議查看 `start_server.sh` 以獲得確切指令)

### 前端

- **安裝依賴**:
  ```bash
  cd frontend
  npm install
  ```
- **啟動開發伺服器**:
  ```bash
  cd frontend
  npm run dev
  ```
- **建置生產版本**:
  ```bash
  cd frontend
  npm run build
  ```

### 測試

- **執行所有前端測試**:
  ```bash
  cd frontend
  npm run test:all
  ```
- **執行後端測試**:
  (專案根目錄下有 `tests/` 目錄，但需要確認測試框架和執行指令，可能是 `pytest`)
  ```bash
  pytest
  ```

## API 文件

- 根據 FastAPI 的特性，API 文件應該在伺服器啟動後，透過 `/docs` 或 `/redoc` 路徑訪問。

## 主要慣例

- **後端**:
  - 採用分層架構 (路由層、服務層、模型層)。
  - 使用 Pydantic 進行嚴格的資料類型驗證。
  - 透過 Alembic 管理資料庫結構變更。
- **前端**:
  - 使用基於檔案的路由設定。
  - 透過 Pinia 進行集中的狀態管理。
  - 使用 Ant Design Vue 作為主要的 UI 框架。
