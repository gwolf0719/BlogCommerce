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

### ⚡ 統一啟動

```bash
# 1. 複製專案
git clone https://github.com/your-username/blogcommerce.git
cd blogcommerce

# 2. 安裝依賴
# (腳本會自動處理，但建議手動執行一次)
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 3. 初始化系統
python init_db.py
python create_test_data.py

# 4. 啟動服務
./start_server.sh
```

### 🌐 訪問地址

- **網站入口**: `http://localhost:8001` (或您指定的 Port)
- **管理後台**: `http://localhost:8001/admin`
- **API 文檔**: `http://localhost:8001/docs`

### 🔐 預設帳號

| 角色 | 帳號 | 密碼 |
|------|------|------|
| 管理員 | admin | admin123456 |
| 會員 | user@example.com | password123 |

## 🎯 啟動腳本

使用 `start_server.sh` 腳本來啟動整個應用程式。

```bash
./start_server.sh [PORT]
```

- **[PORT]** (可選): 指定一個 Port，預設為 `8001`。

**腳本功能:**
- **自動建置**: 自動建置前端管理後台。
- **Port 衝突處理**: 自動終止佔用指定 Port 的進程。
- **統一服務**: 在單一 Port 上提供所有服務。

## 📁 專案結構

```
blogcommerce/
├── app/                    # 後端應用
│   ├── main.py            # FastAPI 入口
│   ├── models/            # 數據模型
│   ├── routes/            # API 路由
│   ├── schemas/           # Pydantic 數據驗證
│   ├── services/          # 業務邏輯服務
│   └── templates/         # Jinja2 HTML 模板
├── frontend/              # Vue.js 管理後台
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── start_server.sh        # 統一啟動腳本
├── init_settings.py       # 系統設定初始化
├── system_health_check.py # 系統健康檢查
└── requirements.txt       # Python 依賴
```

## 🔧 開發指南

### 後端開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動開發服務器 (建議使用 start_server.sh)
# 或者單獨運行後端:
python -m uvicorn app.main:app --reload --port 8001
```

### 前端開發

```bash
cd frontend

# 安裝依賴
npm install

# 啟動開發模式 (與後端分離)
npm run dev

# 僅建置生產版本
npm run build
```

### 數據庫管理

```bash
# 初始化數據庫
python init_db.py

# 創建測試數據
python create_test_data.py
```

## 🚀 部署與維護

### 生產環境部署

```bash
# 1. 設定生產環境變數 (如果需要)
# export DATABASE_URL="postgresql://user:pass@localhost/blogcommerce"
# export SECRET_KEY="your-production-secret-key"

# 2. 啟動生產服務
./start_server.sh
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
