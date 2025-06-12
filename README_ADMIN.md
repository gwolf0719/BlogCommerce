# BlogCommerce 管理後台

## 🏗️ 架構設計

本專案採用 **FastAPI + Vue3 + Ant Design Vue** 整合架構，實現前後端分離開發、統一部署的方案。

### 特色
- ✅ 開發階段：前後端完全分離，支援熱重載
- ✅ 部署階段：前端靜態檔案內嵌到 FastAPI
- ✅ 共用版本控制和資源路徑
- ✅ 無需 nginx 或獨立前端服務器

## 📁 專案結構

```
BlogCommerce/
├── app/                    # FastAPI 後端
│   ├── static/            # Vue 建置後的靜態檔案
│   │   ├── index.html     # 管理後台入口
│   │   └── assets/        # JS/CSS 檔案
│   └── main.py            # 路由配置
├── frontend/              # Vue 3 前端專案
│   ├── src/
│   │   ├── components/    # Vue 組件
│   │   ├── views/         # 頁面組件
│   │   ├── stores/        # Pinia 狀態管理
│   │   ├── router/        # Vue Router 配置
│   │   └── main.js        # 入口檔案
│   ├── package.json
│   └── vite.config.js     # Vite 配置
└── build.sh               # 自動建置腳本
```

## 🚀 開發流程

### 1. 開發模式（前後端分離）

```bash
# 啟動後端 API 服務
python run.py

# 另開終端，啟動前端開發服務器
cd frontend
npm run dev
```

前端開發服務器：http://localhost:3000
後端 API 服務：http://127.0.0.1:8001

### 2. 生產模式（前端內嵌）

```bash
# 建置並部署
./build.sh

# 啟動 FastAPI 服務
python run.py
```

管理後台：http://127.0.0.1:8001/admin

## 🔧 核心技術棧

### 後端
- **FastAPI**: 現代高性能 Python Web 框架
- **SQLAlchemy**: ORM 資料庫操作
- **Pydantic**: 資料驗證和序列化

### 前端
- **Vue 3**: 漸進式 JavaScript 框架
- **Ant Design Vue**: 企業級 UI 組件庫
- **Vue Router**: 單頁應用路由
- **Pinia**: Vue 狀態管理
- **Vite**: 極快的前端建置工具

## 📋 可用指令

```bash
# 前端相關
cd frontend
npm install          # 安裝依賴
npm run dev          # 開發模式
npm run build        # 建置生產版本
npm run build:watch  # 監視建置

# 專案建置
./build.sh           # 自動建置並部署

# 後端啟動
python run.py        # 啟動 FastAPI 服務
```

## 🔐 管理員認證

### 預設帳號
- **用戶名**: admin
- **密碼**: admin123

### 認證流程
1. 登入頁面：`/admin/login`
2. JWT Token 認證
3. 權限檢查（僅限 admin 角色）
4. 重定向到儀表板

## 🎯 頁面路由

| 路由 | 說明 | 組件 |
|------|------|------|
| `/admin/login` | 登入頁面 | Login.vue |
| `/admin/dashboard` | 儀表板 | Dashboard.vue |
| `/admin/posts` | 文章管理 | Posts.vue |
| `/admin/products` | 商品管理 | Products.vue |
| `/admin/orders` | 訂單管理 | Orders.vue |
| `/admin/users` | 會員管理 | Users.vue |
| `/admin/analytics` | 數據分析 | Analytics.vue |
| `/admin/settings` | 系統設定 | Settings.vue |

## 🔄 開發工作流

1. **前端開發**：在 `frontend/` 目錄下使用 Vue 開發
2. **API 開發**：在 `app/api/` 目錄下開發 FastAPI 路由
3. **整合測試**：執行 `./build.sh` 建置並測試
4. **部署**：生產環境只需啟動 FastAPI 服務

## 📚 進階配置

### Vite 配置特點
- **Base Path**: `/static/` 配合 FastAPI 靜態檔案服務
- **API Proxy**: 開發模式下代理 `/api` 請求到後端
- **自動路徑修正**: 建置後自動調整資源路徑

### FastAPI 路由配置
```python
# Admin SPA routes
@app.get("/admin", include_in_schema=False)
@app.get("/admin/{path:path}", include_in_schema=False)
async def admin_spa(path: str = ""):
    return FileResponse(Path("app/static/index.html"))
```

這個架構實現了理想的前後端整合方案，既保持了開發階段的靈活性，又確保了部署的簡潔性。 