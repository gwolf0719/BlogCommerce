# BlogCommerce 部署指南

BlogCommerce 是一個整合部落格與電商功能的現代化平台，基於 FastAPI 和 Jinja2 建構，支援快速部署和多站點複製。

## 🚀 快速開始

### 1. 環境需求

- Python 3.8+
- pip 套件管理器

### 2. 安裝步驟

```bash
# 1. 克隆或下載專案
git clone <repository-url>
cd blogcommerce

# 2. 建立虛擬環境（建議）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安裝相依套件
pip install -r requirements.txt

# 4. 初始化資料庫
python init_db.py

# 5. 啟動應用程式
python run.py
```

### 3. 預設管理員帳號

- **管理後台網址**: http://localhost:8000/admin
- **使用者名稱**: admin
- **電子郵件**: admin@blogcommerce.com
- **密碼**: admin123456

## ⚙️ 環境變數設定

複製 `.env.example` 為 `.env` 並修改設定：

```bash
cp .env.example .env
```

### 關鍵設定項目

#### 網站基本資訊
```env
SITE_NAME=您的網站名稱
SITE_DESCRIPTION=網站描述
SITE_URL=https://yourdomain.com
SITE_LOGO=/static/images/your-logo.png
```

#### 資料庫連線
```env
# SQLite (開發用)
DATABASE_URL=sqlite:///./blogcommerce.db

# MySQL (生產用)
DATABASE_URL=mysql+pymysql://username:password@localhost/database_name

# PostgreSQL (生產用)
DATABASE_URL=postgresql://username:password@localhost/database_name
```

#### 管理員帳號
```env
ADMIN_USERNAME=your_admin
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your_secure_password
ADMIN_FULL_NAME=管理員姓名
```

#### 安全設定
```env
SECRET_KEY=your-super-secret-key-very-long-and-random
JWT_SECRET_KEY=jwt-secret-key-very-long-and-random
```

## 🌐 多站點部署

### 方法一：複製整個專案

1. 複製專案資料夾
2. 修改 `.env` 檔案中的網站設定
3. 修改資料庫連線設定
4. 重新執行 `python init_db.py`
5. 啟動應用程式

### 方法二：使用不同環境變數檔案

```bash
# 站點 A
cp .env .env.site-a
# 修改 .env.site-a 中的設定

# 站點 B  
cp .env .env.site-b
# 修改 .env.site-b 中的設定

# 啟動不同站點
ENV_FILE=.env.site-a python run.py
ENV_FILE=.env.site-b python run.py --port 8001
```

## 🎨 客製化

### 修改網站外觀

1. 編輯 `app/templates/base.html` 修改基礎版面
2. 修改 `app/static/css/style.css` 調整樣式
3. 替換 `app/static/images/` 中的圖片

### 修改首頁內容

編輯 `app/templates/index.html` 自訂首頁內容。

### 新增功能

1. 在 `app/models/` 新增資料模型
2. 在 `app/schemas/` 新增 API 結構定義
3. 在 `app/routes/` 新增路由處理
4. 在 `app/templates/` 新增頁面模板

## 📦 生產環境部署

### 1. 使用 Gunicorn

```bash
# 安裝 gunicorn
pip install gunicorn

# 啟動服務
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. 使用 Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python init_db.py

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 3. Nginx 反向代理設定

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /path/to/blogcommerce/app/static/;
    }
}
```

## 🛠️ 功能特色

### 後台管理
- **儀表板**: 系統統計和快速操作
- **會員管理**: 會員列表、權限管理、狀態控制
- **文章管理**: 文章 CRUD、分類標籤管理
- **商品管理**: 商品 CRUD、庫存管理、價格設定
- **訂單管理**: 訂單查詢、狀態更新、銷售統計

### 前台功能
- **部落格系統**: 文章展示、分類瀏覽、搜尋功能
- **電商系統**: 商品展示、購物車、訂單流程
- **會員系統**: 註冊登入、個人資料管理
- **響應式設計**: 支援桌面和行動裝置

### 技術特色
- **SEO 友善**: 伺服器端渲染、自動 sitemap
- **API 完整**: RESTful API 設計，支援前後端分離
- **模組化架構**: 易於擴展和維護
- **資料庫通用**: 支援 SQLite、MySQL、PostgreSQL

## 🔧 常見問題

### Q: 如何重設管理員密碼？

修改 `.env` 檔案中的 `ADMIN_PASSWORD`，然後執行：

```bash
python init_db.py
```

### Q: 如何更換資料庫？

1. 修改 `.env` 檔案中的 `DATABASE_URL`
2. 安裝對應的資料庫驅動套件
3. 執行 `python init_db.py` 重建資料表

### Q: 如何新增商品分類？

在管理後台 `/admin/categories` 頁面新增，或使用 API：

```bash
curl -X POST "http://localhost:8000/api/categories/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "新分類", "type": "product"}'
```

## 📞 支援

如有問題或建議，請透過以下方式聯繫：

- 提交 Issue 到專案儲存庫
- 發送郵件到技術支援信箱

## 📄 授權

本專案採用 MIT 授權條款。 