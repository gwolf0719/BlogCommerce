# 🛍️ BlogCommerce - 部落格電商整合平台

一個現代化的**部落格 + 電商整合系統**，採用 FastAPI + Vue.js + Tailwind CSS 技術架構，提供完整的內容管理和電商功能。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4+-brightgreen.svg)](https://vuejs.org)
[![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

## ✨ 功能特色

> **設計理念**: 本系統採用簡潔設計，專注於核心功能。為了提供更好的用戶體驗，**已移除分類和標籤功能**，改採智能搜尋和推薦機制來幫助用戶發現內容。

### 📝 內容管理
- **部落格系統**：文章發布、Markdown 編輯、SEO 優化
- **富文本編輯器**：所見即所得的內容創作體驗
- **響應式設計**：完美適配桌面、平板、手機
- **電子報管理**：訂閱管理、郵件發送功能

### 🛒 電商功能
- **商品管理**：商品上架、庫存管理、價格設定
- **購物車系統**：商品加入、數量調整、結帳流程
- **訂單管理**：訂單處理、狀態追蹤、發貨管理

### 👥 用戶系統
- **會員註冊**：郵箱註冊、密碼加密、身份驗證
- **個人中心**：個人資料管理、訂單查詢、收藏功能
- **權限控制**：管理員、普通用戶角色分離

### 🎛️ 管理後台
- **Vue.js 單頁應用**：流暢的管理體驗
- **數據統計**：用戶行為分析、銷售報表、即時分析
- **系統設定**：全站配置、主題設定、功能開關
- **錯誤監控**：系統錯誤日誌追蹤和管理
- **電子報管理**：訂閱者管理、郵件模板編輯

## 🚀 快速開始

### 📋 系統需求

- Python 3.8+
- Node.js 16+
- 作業系統：Windows、macOS、Linux

### ⚡ 一鍵安裝

```bash
# 1. 複製專案
git clone https://github.com/your-username/blogcommerce.git
cd blogcommerce

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 初始化系統
python init_db.py
python create_test_data.py

# 4. 啟動服務（自動處理埠口衝突）
./start.sh
```

### 🌐 訪問地址

- **前台網站**：http://localhost:8000
- **管理後台**：http://localhost:8000/admin
- **API 文檔**：http://localhost:8000/docs

### 🔐 預設帳號

| 角色 | 帳號 | 密碼 |
|------|------|------|
| 管理員 | admin | admin123456 |
| 會員 | user@example.com | password123 |

## 🎯 啟動選項

```bash
# 生產模式（默認）
./start.sh

# 開發模式（自動重建前端）
./start.sh dev

# 熱重載模式（前後端分離）
./start.sh hot

# 自定義埠口
./start.sh dev 8080          # 後端使用 8080
./start.sh hot 8080 3000     # 後端 8080，前端 3000

# 埠口衝突處理
# 腳本會自動檢測埠口衝突，提供以下選項：
# 1. 自動選擇可用埠口
# 2. 停止佔用該埠口的進程  
# 3. 手動指定新埠口
# 4. 退出
```

## 📁 專案結構

```
blogcommerce/
├── app/                    # 後端應用
│   ├── main.py            # FastAPI 入口
│   ├── models/            # 數據模型 (user, product, order, post, analytics, etc.)
│   ├── routes/            # API 路由 (auth, products, orders, analytics, etc.)
│   ├── schemas/           # Pydantic 數據驗證
│   ├── services/          # 業務邏輯服務 (AI, 錯誤日誌, Markdown, etc.)
│   └── templates/         # Jinja2 HTML 模板
├── frontend/              # Vue.js 管理後台
│   ├── src/
│   │   ├── components/    # Vue 組件 (編輯器, 上傳組件, etc.)
│   │   ├── views/         # 頁面視圖 (Dashboard, Analytics, etc.)
│   │   └── router/        # 路由配置
│   ├── package.json
│   └── watch_build.sh     # 前端監控構建腳本
├── start.sh               # 智能啟動腳本 (支援多種模式)
├── build.sh               # 前端構建腳本
├── init_settings.py       # 系統設定初始化
├── system_health_check.py # 系統健康檢查
└── requirements.txt       # Python 依賴
```

## 🔧 開發指南

### 後端開發
```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動開發服務器
python run.py

# 重置管理員密碼
python reset_admin_password.py
```

### 前端開發
```bash
cd frontend

# 安裝依賴
npm install

# 開發模式
npm run dev

# 構建生產版本
npm run build
```

### 數據庫管理
```bash
# 初始化數據庫
python init_db.py

# 創建測試數據
python create_test_data.py

# 重置資料庫並創建測試數據
python reset_and_create_test_data.py

# 初始化系統設定
python init_settings.py

# 系統健康檢查
python system_health_check.py
```

## 🛠️ 配置說明

主要配置文件在 `app/config.py`：

```python
# 數據庫設定
DATABASE_URL = "sqlite:///./blogcommerce.db"

# 安全設定
SECRET_KEY = "your-secret-key"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 應用設定
SITE_NAME = "BlogCommerce"
SITE_DESCRIPTION = "部落格電商整合平台"
```

## 📊 主要功能

### 內容管理
- ✅ 文章 CRUD 操作
- ✅ Markdown 編輯支持
- ✅ SEO 友好的 URL
- ✅ 響應式圖片處理
- ✅ 電子報訂閱管理

### 電商功能
- ✅ 商品管理
- ✅ 購物車功能
- ✅ 訂單處理
- ✅ 庫存追蹤
- ✅ 商品收藏功能

### 系統管理
- ✅ 用戶權限管理
- ✅ 系統設定配置
- ✅ 錯誤日誌監控
- ✅ 即時數據分析
- ✅ 系統健康檢查

### 用戶體驗
- ✅ 快速載入
- ✅ 行動裝置友好
- ✅ 搜尋功能
- ✅ 分頁導航

## 🚀 部署與維護

### 生產環境部署
```bash
# 1. 設定生產環境變數
export DATABASE_URL="postgresql://user:pass@localhost/blogcommerce"
export SECRET_KEY="your-production-secret-key"

# 2. 構建並啟動生產服務
./start.sh prod
```

### 系統維護
```bash
# 系統健康檢查
python system_health_check.py

# 重置管理員密碼
python reset_admin_password.py

# 查看系統日誌
tail -f logs/app.log

# 查看錯誤日誌（透過管理後台 /admin/error-logs）
```

### 備份與恢復
```bash
# 備份資料庫
cp blogcommerce.db blogcommerce_backup_$(date +%Y%m%d).db

# 查看詳細部署指南
cat README_deployment.md
```

## 🤝 貢獻指南

1. Fork 本專案
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📝 License

本專案採用 MIT License - 詳見 [LICENSE](LICENSE) 文件

## 🙏 致謝

- [FastAPI](https://fastapi.tiangolo.com/) - 現代高性能 Python Web 框架
- [Vue.js](https://vuejs.org/) - 漸進式 JavaScript 框架
- [Tailwind CSS](https://tailwindcss.com/) - 實用優先的 CSS 框架
- [Alpine.js](https://alpinejs.dev/) - 輕量級 JavaScript 框架

---

**⭐ 如果這個專案對您有幫助，請給個 Star 支持！**
