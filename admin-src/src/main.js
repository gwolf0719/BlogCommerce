import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'
import routes from './router'
import errorHandler from './utils/errorHandler'
import { useAuthStore } from './stores/auth'

const router = createRouter({
  history: createWebHistory('/admin'),
  routes
})

const pinia = createPinia()
const app = createApp(App)

// 先初始化pinia和app
app.use(pinia)

// 設置路由守衛（在pinia初始化之後）
router.beforeEach(async (to, from, next) => {
  // 如果是登入頁面，直接放行
  if (to.path === '/login') {
    next()
    return
  }
  
  try {
    // 創建store實例
    const authStore = useAuthStore()
    
    // 檢查認證狀態
    const isAuthenticated = await authStore.checkAuth()
    
    if (isAuthenticated) {
      next() // 認證成功，繼續訪問
    } else {
      next('/login') // 認證失敗，跳轉到登入頁面
    }
  } catch (error) {
    console.error('認證檢查失敗:', error)
    next('/login') // 發生錯誤，跳轉到登入頁面
  }
})

app.use(router)
app.use(Antd)
app.mount('#app')
