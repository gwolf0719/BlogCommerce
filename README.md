# 🛍️ BlogCommerce - 部落格電商整合平台

一個現代化的**部落格 + 電商整合系統**，採用 FastAPI + Jinja2 + Tailwind CSS + Alpine.js 技術架構，提供完整的內容管理和電商功能。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

---

## ✨ 專案特色

### 🎯 核心功能
- 🔍 **SEO 優化**：自動 sitemap.xml、meta 標籤管理、結構化資料
- 📝 **部落格系統**：文章管理、分類標籤、Markdown 編輯器、留言系統
- 🛒 **電商模組**：商品管理、購物車、訂單處理、庫存管理
- 👥 **會員系統**：註冊登入、個人資料、訂單查詢、密碼管理
- 🔐 **管理後台**：用戶管理、內容管理、訂單管理、數據分析
- 📊 **流量分析**：實時用戶追蹤、頁面瀏覽統計、用戶行為分析

### 🚀 技術特色
- **現代化架構**：FastAPI + SQLAlchemy + Jinja2
- **響應式設計**：Tailwind CSS + Alpine.js，支援 RWD
- **安全機制**：JWT 認證、密碼加密、權限控制
- **資料庫彈性**：支援 SQLite、MySQL、PostgreSQL
- **即開即用**：包含範例資料和測試帳號

---

## 📁 專案架構

```
blogcommerce/
├── app/                    # 主應用程式
│   ├── main.py            # FastAPI 應用程式入口
│   ├── config.py          # 應用程式設定
│   ├── database.py        # 資料庫連線設定
│   ├── auth.py            # 認證相關功能
│   ├── models/            # SQLAlchemy 資料模型
│   │   ├── base.py       # 基礎模型
│   │   ├── user.py       # 用戶模型
│   │   ├── post.py       # 文章模型
│   │   ├── product.py    # 商品模型
│   │   ├── order.py      # 訂單模型
│   │   ├── category.py   # 分類模型
│   │   ├── tag.py        # 標籤模型
│   │   └── analytics.py  # 分析模型
│   ├── routes/            # API 路由
│   │   ├── auth.py       # 認證路由
│   │   ├── posts.py      # 文章路由
│   │   ├── products.py   # 商品路由
│   │   ├── orders.py     # 訂單路由
│   │   ├── admin.py      # 管理員路由
│   │   ├── cart.py       # 購物車路由
│   │   ├── categories.py # 分類路由
│   │   ├── tags.py       # 標籤路由
│   │   └── analytics.py  # 分析路由
│   ├── schemas/           # Pydantic 資料驗證模型
│   ├── templates/         # Jinja2 HTML 模板
│   │   ├── base.html     # 基礎模板
│   │   ├── index.html    # 首頁模板
│   │   ├── auth/         # 認證相關頁面
│   │   ├── blog/         # 部落格頁面
│   │   ├── shop/         # 電商頁面
│   │   ├── pages/        # 靜態頁面
│   │   └── tags/         # 標籤頁面
│   └── static/            # 靜態資源
│       ├── css/          # 樣式檔案
│       ├── js/           # JavaScript 檔案
│       └── images/       # 圖片資源
├── frontend/             # Vue3 + Ant Design 管理前端
├── venv/                  # Python 虛擬環境
├── requirements.txt       # Python 相依套件
├── .env                   # 環境變數設定
├── .env.example          # 環境變數範例
├── run.py                # 應用程式啟動檔
├── init_db.py            # 資料庫初始化腳本
└── create_test_data.py   # 測試資料建立腳本
```

---

## 🚀 快速開始

### 📋 系統需求

- Python 3.8 或以上版本
- 作業系統：Windows、macOS、Linux
- 記憶體：最少 512MB（建議 1GB 以上）
- 硬碟空間：最少 100MB

### ⚡ 一鍵安裝

1. **複製專案**
   ```bash
   git clone <your-repo-url>
   cd blogcommerce
   ```

2. **設定虛擬環境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或者 Windows: venv\Scripts\activate
   ```

3. **安裝相依套件**
   ```bash
   pip install -r requirements.txt
   ```

4. **設定環境變數**
   ```bash
   cp .env.example .env
   # 編輯 .env 檔案設定您的參數
   ```

5. **初始化資料庫**
   ```bash
   python init_db.py
   python create_test_data.py  # 建立測試資料（可選）
   ```

6. **編譯前端**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

7. **啟動應用程式**
   ```bash
   python run.py
   ```

8. **開啟瀏覽器**
   - 前台網站：http://localhost:8000
   - API 文檔：http://localhost:8000/docs
   - 管理後台：http://localhost:8000/admin

---

## 🔐 預設帳號

### 管理員帳號
- **帳號**：admin
- **密碼**：admin123456
- **登入網址**：http://localhost:8000/admin

### 測試會員帳號
- **帳號**：user@example.com
- **密碼**：password123

---

## 🌐 主要功能路由

### 前台路由
| 路由 | 說明 |
|------|------|
| `/` | 首頁 |
| `/login` | 會員登入 |
| `/register` | 會員註冊 |
| `/profile` | 個人資料 |
| `/blog` | 部落格文章列表 |
| `/blog/{slug}` | 文章詳情頁 |
| `/products` | 商品列表 |
| `/product/{slug}` | 商品詳情頁 |
| `/cart` | 購物車 |
| `/checkout` | 結帳頁面 |
| `/orders` | 訂單查詢 |
| `/tags` | 標籤總覽 |
| `/about` | 關於我們 |
| `/contact` | 聯絡我們 |

### 管理後台路由
| 路由 | 說明 |
|------|------|
| `/admin` | 控制台首頁 |
| `/admin/users` | 用戶管理 |
| `/admin/posts` | 文章管理 |
| `/admin/products` | 商品管理 |
| `/admin/orders` | 訂單管理 |
| `/admin/categories` | 分類管理 |
| `/admin/analytics` | 數據分析 |
| `/admin/settings` | 系統設定 |

### API 路由
| Method | 路徑 | 說明 |
|--------|------|------|
| GET | `/api/posts` | 取得文章列表 |
| POST | `/api/posts` | 建立新文章 |
| GET | `/api/products` | 取得商品列表 |
| POST | `/api/orders` | 建立訂單 |
| GET | `/api/admin/tags` | 取得標籤列表（管理） |
| POST | `/api/admin/tags` | 新增標籤（管理） |
| PUT | `/api/admin/tags/{id}` | 更新標籤（管理） |
| DELETE | `/api/admin/tags/{id}` | 刪除標籤（管理） |
| GET | `/api/admin/newsletter/subscribers` | 取得訂閱者列表 |
| POST | `/api/admin/newsletter/subscribers` | 新增訂閱者 |
| PUT | `/api/admin/newsletter/subscribers/{id}` | 更新訂閱者 |
| DELETE | `/api/admin/newsletter/subscribers/{id}` | 刪除訂閱者 |
| POST | `/api/auth/login` | 用戶登入 |
| POST | `/api/auth/register` | 用戶註冊 |
| GET | `/api/cart` | 取得購物車 |
| POST | `/api/cart/add` | 加入購物車 |
| POST | `/api/analytics/track` | 記錄頁面瀏覽 |
| POST | `/api/analytics/heartbeat` | 用戶活動心跳 |
| GET | `/api/analytics/stats/overview` | 流量統計概覽 |
| GET | `/api/analytics/realtime` | 實時統計數據 |
| GET | `/health` | 健康檢查 |

---

## 🔧 設定說明

### 資料庫設定
支援多種資料庫類型，在 `.env` 檔案中設定：

```bash
# SQLite（預設）
DATABASE_URL=sqlite:///./blogcommerce.db

# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/blogcommerce

# PostgreSQL
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/blogcommerce
```

### 重要環境變數
```bash
# 基本設定
SITE_NAME=BlogCommerce
SITE_DESCRIPTION=部落格與電商整合平台
DEBUG=False
SECRET_KEY=your-secret-key-here

# JWT 設定
JWT_SECRET_KEY=jwt-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 管理員帳號
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123456

# 電商設定
DEFAULT_CURRENCY=TWD
FREE_SHIPPING_THRESHOLD=1000.0
DEFAULT_SHIPPING_FEE=60.0
```

---

## 📊 系統功能

### 🛒 電商功能
- ✅ 商品展示和分類
- ✅ 購物車和結帳流程
- ✅ 訂單管理和狀態追蹤
- ✅ 庫存管理
- ✅ 運費計算
- ✅ 優惠碼系統

### 📝 部落格功能
- ✅ Markdown 文章編輯
- ✅ 分類和標籤系統
- ✅ 文章搜尋功能
- ✅ SEO 優化
- ✅ 社群分享功能

### 👥 會員系統
- ✅ 註冊登入機制
- ✅ 個人資料管理
- ✅ 訂單歷史查詢
- ✅ 密碼重設功能
- ✅ JWT 安全認證

### 🔐 管理後台
- ✅ 儀表板數據概覽
- ✅ 用戶管理
- ✅ 內容管理（文章/商品）
- ✅ 訂單管理
- ✅ 系統設定
- ✅ 數據分析

### 📊 流量分析系統
- ✅ 實時用戶追蹤
- ✅ 頁面瀏覽統計
- ✅ 用戶行為分析
- ✅ 設備類型統計
- ✅ 熱門內容分析
- ✅ 用戶會話管理

---

## 🚀 部署選項

### 開發環境
```bash
python run.py
```

### 生產環境
```bash
# 使用 Gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# 使用 Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker 部署
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🧪 測試

### 運行測試
```bash
pytest
```

### API 測試
```bash
# 健康檢查
curl http://localhost:8000/health

# 取得文章列表
curl http://localhost:8000/api/posts

# 取得商品列表
curl http://localhost:8000/api/products
```

---

## 📚 開發文檔

### API 文檔
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

### 資料庫結構
詳細的資料庫 schema 可在 `app/models/` 目錄中查看各個模型定義。

### 自訂設定
所有設定選項都在 `app/config.py` 中定義，可透過環境變數覆蓋預設值。

---

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支：`git checkout -b feature/new-feature`
3. 提交變更：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 建立 Pull Request

---

## 📝 版本記錄

### v1.0.0 (2025-06-07)
- ✅ 基礎部落格和電商功能
- ✅ 會員系統和管理後台
- ✅ 響應式設計
- ✅ API 文檔
- ✅ 完整的流量分析系統
- ✅ 實時用戶追蹤功能
- ✅ 全面系統測試 (25/25 項目通過)

---

## 📄 授權條款

本專案採用 MIT 授權條款。詳細內容請查看 [LICENSE](LICENSE) 檔案。

---

## 🆘 技術支援

如有問題或建議，請：
1. 查看 [API 文檔](http://localhost:8000/docs)
2. 搜尋 [Issues](../../issues)
3. 建立新的 [Issue](../../issues/new)

---

**🎉 感謝使用 BlogCommerce！**
