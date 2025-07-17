import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'
// 1. 直接導入已經配置好的 router 實例
import router from './router'
import { useAuthStore } from './stores/auth'

const pinia = createPinia()
const app = createApp(App)

// 2. 先掛載 Pinia，以便路由守衛可以使用 store
app.use(pinia)

// 3. 設置路由守衛
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果目標是登入頁，且使用者已登入，則導向儀表板
  if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }

  // 如果目標不是登入頁，且使用者未登入，則檢查 token
  if (to.name !== 'Login' && !authStore.isAuthenticated) {
    try {
      // 嘗試用 token 驗證
      const hasAuth = await authStore.checkAuth()
      if (hasAuth) {
        next() // 驗證成功
      } else {
        next({ name: 'Login' }) // 驗證失敗，導向登入
      }
    } catch (error) {
      console.error('Authentication check failed:', error)
      next({ name: 'Login' }) // 發生錯誤，導向登入
    }
  } else {
    // 其他情況（已登入訪問非登入頁，或未登入訪問登入頁）直接放行
    next()
  }
})

// 4. 掛載路由和 Ant Design
app.use(router)
app.use(Antd)

app.mount('#app')
