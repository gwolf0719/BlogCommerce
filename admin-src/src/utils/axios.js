import axios from 'axios'
import { handleApiError } from './errorHandler'

// 建立 axios 實例
const api = axios.create({
  baseURL: 'http://localhost:8002',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    // 可以在這裡加入 token 或其他認證資訊
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
      // 未授權，清除 token 並跳轉到登入頁面
      localStorage.removeItem('admin_token')
      window.location.href = '/admin/login'
      return Promise.reject(error)
    }
    
    // 對於其他錯誤，使用統一的錯誤處理
    if (error.response) {
      await handleApiError(error.response)
    }
    
    return Promise.reject(error)
  }
)

export default api 