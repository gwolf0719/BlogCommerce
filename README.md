# 🛍 BlogCommerce — Vue 3 + FastAPI + PostgreSQL

一個注重 SEO、速度快、原生設計的 **部落格 + 電商系統**。前端使用 Vue 3 + Vite，後端使用 FastAPI + PostgreSQL，整體架構採用單一倉庫「Monorepo」設計，適合部封於雲端、VPS 或 Docker 環境中。

---

## 📆 專案特色

* 🔍 **高效能 SEO**：支援靜態頁面、meta tag 管理、結構化資料、sitemap.xml、RSS。
* 📰 **部落格系統**：文章 CRUD、分類、標籤、Markdown 編輯器。
* 🛍️ **電商模組**：商品管理、購物車、訂單管理、結帳流程。
* ⚙️ **單一倉庫架構**：前後端整合開發，易於維護與部署。
* 🚀 **現代化技術棒**：Vue 3 + Pinia + Tailwind + FastAPI + PostgreSQL。

---

## 📁 專案結構

```
blogcommerce/
├── frontend/         # Vue 3 + Vite 前端
│   ├── public/
│   ├── src/
│   └── vite.config.js
├── backend/          # FastAPI 後端
│   ├── main.py
│   ├── api/
│   ├── models/
│   └── database.py
├── shared/           # 可選：前後端共用 schema/常數
├── .env              # 環境變數設定
├── requirements.txt  # Python 套件清單
├── package.json      # 前端套件清單
└── README.md         # 本說明文件
```

---

## ✅ 主要功能模組

### 📖 部落格系統

* 文章列表、詳情頁
* 分類、標籤系統
* SEO meta 設定
* Markdown 編輯器
* 自動 sitemap.xml / RSS

### 🛍️ 電商系統

* 商品管理、前端列表 + 詳情
* 購物車 (localStorage)
* 結帳、下單流程
* 訂單狀態跟蹤 + 後台管理

### 🔐 後台管理

* 管理者登入 (JWT)
* 文章、商品、訂單後台介面
* 權限管制 (管理員 / 編輯者)

---

## 🧪 快速啟動

### 🔹 安裝前端

```bash
cd frontend
npm install
npm run dev
```

### 🔹 安裝後端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
uvicorn backend.main:app --reload
```

### 🔹 資料庫初始化 (PostgreSQL)

```bash
# 可用 SQL 工具匯入 / 使用 Alembic 管理遷移
createdb blogcommerce
```

---

## 🌐 路由規劃

### 前端頁面 (Vue Router)

| 路由               | 說明     |
| ---------------- | ------ |
| `/`              | 首頁     |
| `/blog`          | 文章列表   |
| `/blog/:slug`    | 文章詳情頁  |
| `/products`      | 商品列表   |
| `/product/:slug` | 商品詳情頁  |
| `/cart`          | 購物車    |
| `/checkout`      | 結帳流程   |
| `/admin/login`   | 後台登入頁  |
| `/admin/*`       | 後台管理介面 |

### API 路由 (FastAPI)

| Method | 路徑                | 說明         |
| ------ | ----------------- | ---------- |
| GET    | `/api/posts`      | 取得文章列表     |
| POST   | `/api/posts`      | 新增文章       |
| GET    | `/api/products`   | 商品清單       |
| POST   | `/api/orders`     | 提交訂單       |
| POST   | `/api/auth/login` | 使用者登入（JWT） |
| GET    | `/sitemap.xml`    | 自動 sitemap |

---

## 🔐 環境變數 (`.env`)

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/blogcommerce
JWT_SECRET=your_secret_key
```

---

## 🚀 未來規劃

* [ ] 第三方付款串接（TapPay、綢界）
* [ ] SSR 或 Nuxt 預渲染版本
* [ ] 多語系支援（i18n）
* [ ] 商品庫存同步機制
* [ ] 單元測試與 CI/CD 工作流

---

## 🧑‍💻 貢獻方式

歡迎 Issue、PR 或 Fork 本專案協作！
可依模組進行功能貢獻：文章管理 / 商品功能 / 訂單流程 / SEO 最佳化。

---

## 📄 授權 License

本專案採用 MIT 授權釋出。自由商用 / 修改 / 整合，但請保留原作者名稱 🙌
