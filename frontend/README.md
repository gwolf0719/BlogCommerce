# BlogCommerce 前端

基於 Vue 3 + Vite 的現代化部落格電商系統前端，採用 Tailwind CSS 進行樣式設計。

## 🛠️ 技術棧

- **Vue 3** - 漸進式 JavaScript 框架
- **Vite** - 快速建置工具
- **Vue Router** - 官方路由管理
- **Pinia** - 現代化狀態管理
- **Tailwind CSS** - 實用優先的 CSS 框架
- **TypeScript** - JavaScript 的超集合 (可選)

## 🚀 快速開始

### 1. 安裝依賴

```bash
cd frontend
npm install
```

### 2. 環境設定

建立環境變數檔案：
```bash
cp .env.example .env
```

編輯 `.env` 檔案：
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=BlogCommerce
VITE_SITE_URL=http://localhost:3000
```

### 3. 啟動開發伺服器

```bash
npm run dev
```

應用程式將在 http://localhost:3000 啟動

### 4. 建置生產版本

```bash
npm run build
```

## 📁 專案結構

```
frontend/
├── public/              # 靜態檔案
│   ├── favicon.ico
│   └── index.html
├── src/
│   ├── assets/          # 資源檔案
│   │   ├── images/      # 圖片資源
│   │   ├── styles/      # 樣式檔案
│   │   └── main.css     # 主要樣式
│   ├── components/      # Vue 組件
│   │   ├── common/      # 通用組件
│   │   ├── layout/      # 佈局組件
│   │   ├── blog/        # 部落格組件
│   │   ├── shop/        # 商城組件
│   │   └── admin/       # 管理後台組件
│   ├── views/           # 頁面組件
│   │   ├── Home.vue     # 首頁
│   │   ├── Blog.vue     # 部落格列表
│   │   ├── BlogPost.vue # 文章詳情
│   │   ├── Products.vue # 商品列表
│   │   ├── Product.vue  # 商品詳情
│   │   ├── Cart.vue     # 購物車
│   │   ├── Checkout.vue # 結帳頁面
│   │   └── admin/       # 管理後台頁面
│   ├── stores/          # Pinia 狀態管理
│   │   ├── auth.js      # 認證狀態
│   │   ├── blog.js      # 部落格狀態
│   │   ├── shop.js      # 商城狀態
│   │   └── cart.js      # 購物車狀態
│   ├── router/          # 路由配置
│   │   └── index.js     # 路由定義
│   ├── utils/           # 工具函數
│   │   ├── api.js       # API 請求工具
│   │   ├── auth.js      # 認證工具
│   │   ├── format.js    # 格式化工具
│   │   └── constants.js # 常數定義
│   ├── composables/     # Vue 3 組合式函數
│   │   ├── useApi.js    # API 呼叫
│   │   ├── useAuth.js   # 認證邏輯
│   │   └── useCart.js   # 購物車邏輯
│   ├── App.vue          # 根組件
│   └── main.js          # 應用程式入口
├── .env.example         # 環境變數範例
├── vite.config.js       # Vite 配置
├── tailwind.config.js   # Tailwind 配置
├── postcss.config.js    # PostCSS 配置
├── package.json         # 專案配置
└── README.md            # 本檔案
```

## 🎨 設計系統

### 色彩主題

使用 Tailwind CSS 預設色彩，可在 `tailwind.config.js` 中自訂：

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        // 更多自訂色彩
      }
    }
  }
}
```

### 組件庫

專案包含預設的組件：

- **佈局組件**: Header、Footer、Sidebar
- **通用組件**: Button、Card、Modal、Form
- **部落格組件**: PostCard、PostList、CategoryFilter
- **商城組件**: ProductCard、ProductGrid、AddToCart
- **管理組件**: DataTable、Form、Sidebar

## 🔄 狀態管理

使用 Pinia 進行狀態管理：

### 認證狀態 (auth.js)
```javascript
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: false
  }),
  actions: {
    async login(credentials) {
      // 登入邏輯
    },
    logout() {
      // 登出邏輯
    }
  }
})
```

### 購物車狀態 (cart.js)
```javascript
export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    total: 0
  }),
  actions: {
    addItem(product, quantity) {
      // 加入商品邏輯
    },
    removeItem(productId) {
      // 移除商品邏輯
    }
  }
})
```

## 🛣️ 路由配置

### 公開路由
- `/` - 首頁
- `/blog` - 部落格列表
- `/blog/:slug` - 文章詳情
- `/products` - 商品列表
- `/product/:slug` - 商品詳情
- `/cart` - 購物車
- `/checkout` - 結帳

### 管理後台路由 (需認證)
- `/admin` - 管理首頁
- `/admin/posts` - 文章管理
- `/admin/products` - 商品管理
- `/admin/orders` - 訂單管理
- `/admin/users` - 使用者管理

### 路由守衛

```javascript
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!authStore.isAuthenticated) {
      next('/admin/login')
    } else {
      next()
    }
  } else {
    next()
  }
})
```

## 🔧 API 整合

### API 工具函數

```javascript
// utils/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 請求攔截器
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
```

### 使用範例

```javascript
// 在組件中使用
import { onMounted, ref } from 'vue'
import api from '@/utils/api'

export default {
  setup() {
    const posts = ref([])
    
    const fetchPosts = async () => {
      try {
        const response = await api.get('/api/v1/posts')
        posts.value = response.data
      } catch (error) {
        console.error('Error fetching posts:', error)
      }
    }
    
    onMounted(fetchPosts)
    
    return { posts }
  }
}
```

## 🎯 SEO 優化

### Meta 標籤管理

```javascript
// 在組件中設定 meta 標籤
export default {
  setup() {
    // 使用 Vue Meta 或 vue-head
    useMeta({
      title: '文章標題',
      meta: [
        { name: 'description', content: '文章描述' },
        { property: 'og:title', content: '文章標題' },
        { property: 'og:description', content: '文章描述' }
      ]
    })
  }
}
```

### Sitemap 和 RSS

前端會自動生成：
- `/sitemap.xml` - 網站地圖
- `/rss.xml` - RSS 訂閱

## 🧪 測試

### 單元測試

```bash
# 執行測試
npm run test

# 執行測試並監視檔案變更
npm run test:watch

# 執行測試並產生覆蓋率報告
npm run test:coverage
```

### E2E 測試

```bash
# 執行端對端測試
npm run test:e2e

# 在 headless 模式執行
npm run test:e2e:headless
```

## 🚀 部署

### 靜態檔案部署

```bash
# 建置生產版本
npm run build

# 預覽建置結果
npm run preview
```

建置檔案將在 `dist/` 目錄中，可部署到任何靜態檔案伺服器。

### Netlify 部署

1. 連接 Git 儲存庫
2. 設定建置命令：`npm run build`
3. 設定發布目錄：`dist`
4. 設定環境變數

### Vercel 部署

```bash
# 安裝 Vercel CLI
npm i -g vercel

# 部署
vercel --prod
```

### Docker 部署

```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## ⚙️ 環境變數

| 變數名稱 | 說明 | 預設值 |
|---------|------|--------|
| `VITE_API_BASE_URL` | 後端 API 基礎網址 | `http://localhost:8000` |
| `VITE_APP_NAME` | 應用程式名稱 | `BlogCommerce` |
| `VITE_SITE_URL` | 網站網址 | `http://localhost:3000` |
| `VITE_ENABLE_PWA` | 是否啟用 PWA | `false` |
| `VITE_GOOGLE_ANALYTICS_ID` | Google Analytics ID | - |

## 🔧 自訂配置

### 新增頁面

1. 在 `src/views/` 建立新的 Vue 檔案
2. 在 `src/router/index.js` 加入路由
3. 如需要，建立對應的 store

### 新增組件

1. 在 `src/components/` 對應目錄建立組件
2. 在需要的地方引入使用

### 新增樣式

1. 在 `src/assets/styles/` 加入自訂樣式
2. 在 `main.css` 中引入
3. 或在 `tailwind.config.js` 中擴展 Tailwind

## 🎨 主題客製化

### 色彩主題

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#your-color',
          secondary: '#your-color',
        }
      }
    }
  }
}
```

### 字型設定

```css
/* main.css */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
  font-family: 'Inter', sans-serif;
}
```

## 📚 相關文件

- [Vue 3 官方文件](https://vuejs.org/)
- [Vite 官方文件](https://vitejs.dev/)
- [Vue Router 官方文件](https://router.vuejs.org/)
- [Pinia 官方文件](https://pinia.vuejs.org/)
- [Tailwind CSS 官方文件](https://tailwindcss.com/) 