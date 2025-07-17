import axios from 'axios'
import { handleApiError } from './errorHandler'


// 建立 axios 實例
const api = axios.create({
  baseURL: '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 回應攔截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    // 只有在非登錄頁面且收到401錯誤時才自動跳轉
    if (error.response?.status === 401 && !window.location.pathname.includes('/login')) {
      localStorage.removeItem('admin_token')
      // 跳轉路徑也需要是 /admin/login
      window.location.href = '/admin/login'
      return Promise.reject(error)
    }
    
    if (error.response) {
      await handleApiError(error.response)
    }
    
    return Promise.reject(error)
  }
)

export default api 