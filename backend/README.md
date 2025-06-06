# BlogCommerce 後端 API

基於 FastAPI 的現代化部落格電商系統後端，支援多種資料庫。

## 🗄️ 支援的資料庫

- **SQLite** - 適合開發和小型專案
- **MySQL** - 適合中型到大型專案  
- **PostgreSQL** - 適合需要進階功能的專案

## 🚀 快速開始

### 1. 建立虛擬環境

```bash
# 在專案根目錄
cd backend
python3 -m venv venv

# 啟動虛擬環境
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 2. 安裝依賴

```bash
pip install -r ../requirements.txt
```

### 3. 環境設定

複製環境變數範例檔案：
```bash
cp ../env.example ../.env
```

編輯 `.env` 檔案，設定資料庫連線：

#### SQLite (預設)
```env
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./blog_shop.db
```

#### MySQL
```env
DATABASE_TYPE=mysql
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/blogcommerce
```

#### PostgreSQL
```env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://username:password@localhost:5432/blogcommerce
```

### 4. 初始化資料庫

```bash
# 建立資料表
python -c "from database import create_tables; create_tables()"

# 或使用 Alembic 進行資料庫遷移
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 5. 啟動開發伺服器

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API 將在 http://localhost:8000 啟動
API 文件將在 http://localhost:8000/docs 提供

## 📁 專案結構

```
backend/
├── main.py              # FastAPI 應用程式主檔案
├── database.py          # 資料庫配置和連線
├── models/              # 資料模型
│   ├── models.py        # SQLAlchemy 模型
│   └── schemas.py       # Pydantic schemas
├── api/                 # API 路由
│   ├── __init__.py
│   ├── auth.py          # 認證相關 API
│   ├── posts.py         # 文章相關 API
│   ├── products.py      # 商品相關 API
│   ├── orders.py        # 訂單相關 API
│   └── admin.py         # 管理後台 API
├── utils/               # 工具函數
│   ├── auth.py          # 認證工具
│   ├── security.py      # 安全相關工具
│   └── helpers.py       # 通用輔助函數
├── venv/                # 虛擬環境
└── README.md            # 本檔案
```

## 🔐 認證系統

使用 JWT (JSON Web Tokens) 進行認證：

- 管理員登入：`POST /api/v1/auth/login`
- Token 驗證：自動在需要認證的端點進行
- Token 過期時間：預設 30 分鐘 (可在環境變數調整)

## 📋 API 端點

### 認證
- `POST /api/v1/auth/login` - 使用者登入
- `POST /api/v1/auth/register` - 使用者註冊 (管理員功能)

### 文章管理
- `GET /api/v1/posts` - 取得文章列表
- `GET /api/v1/posts/{slug}` - 取得單一文章
- `POST /api/v1/posts` - 建立文章 (需認證)
- `PUT /api/v1/posts/{id}` - 更新文章 (需認證)
- `DELETE /api/v1/posts/{id}` - 刪除文章 (需認證)

### 商品管理
- `GET /api/v1/products` - 取得商品列表
- `GET /api/v1/products/{slug}` - 取得單一商品
- `POST /api/v1/products` - 建立商品 (需認證)
- `PUT /api/v1/products/{id}` - 更新商品 (需認證)
- `DELETE /api/v1/products/{id}` - 刪除商品 (需認證)

### 訂單管理
- `GET /api/v1/orders` - 取得訂單列表 (需認證)
- `GET /api/v1/orders/{id}` - 取得單一訂單
- `POST /api/v1/orders` - 建立訂單
- `PUT /api/v1/orders/{id}` - 更新訂單狀態 (需認證)

### 分類和標籤
- `GET /api/v1/categories` - 取得分類列表
- `POST /api/v1/categories` - 建立分類 (需認證)
- `GET /api/v1/tags` - 取得標籤列表
- `POST /api/v1/tags` - 建立標籤 (需認證)

## ⚙️ 環境變數說明

| 變數名稱 | 說明 | 預設值 |
|---------|------|--------|
| `DATABASE_TYPE` | 資料庫類型 | `sqlite` |
| `DATABASE_URL` | 資料庫連線字串 | `sqlite:///./blog_shop.db` |
| `JWT_SECRET` | JWT 密鑰 | 需要設定 |
| `DEBUG` | 除錯模式 | `true` |
| `BACKEND_CORS_ORIGINS` | 允許的跨域來源 | `["http://localhost:3000"]` |

完整的環境變數列表請參考專案根目錄的 `env.example` 檔案。

## 🔄 資料庫遷移

使用 Alembic 進行資料庫版本控制：

```bash
# 初始化 Alembic (只需執行一次)
alembic init alembic

# 建立新的遷移檔案
alembic revision --autogenerate -m "描述變更內容"

# 執行遷移
alembic upgrade head

# 降級到前一版本
alembic downgrade -1

# 查看遷移歷史
alembic history
```

## 🧪 測試

```bash
# 執行測試
pytest

# 執行測試並顯示覆蓋率
pytest --cov=.

# 執行特定測試檔案
pytest tests/test_auth.py
```

## 🚀 部署

### 生產環境設定

1. 修改 `.env` 檔案：
```env
DEBUG=false
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:pass@localhost:5432/blogcommerce_prod
JWT_SECRET=your_production_secret_key
BACKEND_CORS_ORIGINS=["https://your-domain.com"]
```

2. 使用 Gunicorn 啟動：
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker 部署

```dockerfile
# Dockerfile 範例
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔧 常見問題

### Q: 資料庫連線失敗
A: 檢查 `DATABASE_URL` 格式是否正確，確認資料庫服務是否啟動

### Q: JWT Token 過期
A: 調整 `ACCESS_TOKEN_EXPIRE_MINUTES` 環境變數

### Q: CORS 錯誤
A: 確認前端網址已加入 `BACKEND_CORS_ORIGINS` 設定

### Q: 檔案上傳失敗
A: 檢查 `UPLOAD_DIR` 目錄是否存在且有寫入權限

## 📚 相關文件

- [FastAPI 官方文件](https://fastapi.tiangolo.com/)
- [SQLAlchemy 官方文件](https://docs.sqlalchemy.org/)
- [Alembic 官方文件](https://alembic.sqlalchemy.org/)
- [Pydantic 官方文件](https://docs.pydantic.dev/) 