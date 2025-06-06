import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // 狀態
  const token = ref(localStorage.getItem('auth_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('auth_user') || 'null'))
  const loading = ref(false)
  const error = ref(null)

  // 計算屬性
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin || false)

  // API 基礎 URL
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

  // 動作
  const login = async (username, password) => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username,
          password,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '登入失敗')
      }

      const data = await response.json()
      
      // 儲存 token
      token.value = data.access_token
      localStorage.setItem('auth_token', data.access_token)

      // 獲取用戶資訊
      await fetchUser()

      return { success: true }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }

  const fetchUser = async () => {
    if (!token.value) return

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token.value}`,
        },
      })

      if (response.ok) {
        const userData = await response.json()
        user.value = userData
        localStorage.setItem('auth_user', JSON.stringify(userData))
      } else {
        // Token 可能已過期
        await logout()
      }
    } catch (err) {
      console.error('獲取用戶資訊失敗:', err)
      await logout()
    }
  }

  const checkAuth = () => {
    if (token.value) {
      fetchUser()
    }
  }

  const register = async (userData) => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '註冊失敗')
      }

      const data = await response.json()
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // API 請求工具函數
  const apiRequest = async (url, options = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (token.value) {
      headers.Authorization = `Bearer ${token.value}`
    }

    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers,
      })

      if (response.status === 401) {
        // Token 過期，自動登出
        await logout()
        throw new Error('認證已過期，請重新登入')
      }

      return response
    } catch (err) {
      throw err
    }
  }

  return {
    // 狀態
    token,
    user,
    loading,
    error,
    
    // 計算屬性
    isLoggedIn,
    isAdmin,
    
    // 動作
    login,
    logout,
    register,
    fetchUser,
    checkAuth,
    apiRequest,
  }
}) 