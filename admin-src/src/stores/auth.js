import { defineStore } from 'pinia'
import api from '@/utils/axios'
import { message } from 'ant-design-vue'
import { handleApiError } from '@/utils/errorHandler'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('admin_token') || null,
    isAuthenticated: !!localStorage.getItem('admin_token'),
  }),
  getters: {
    isAdmin: (state) => state.user?.role === 'admin',
  },
  actions: {
    async login(credentials) {
      try {
        // 【核心修正點 1】: login 動作一次性完成所有認證流程
        const response = await api.post('/api/auth/login', credentials)
        const { access_token, user } = response.data
        
        if (user.role !== 'admin') {
          this.logout() // 登出以清除任何可能殘留的狀態
          throw new Error('權限不足，需要管理員權限')
        }
        
        this.token = access_token
        this.user = user
        this.isAuthenticated = true
        
        localStorage.setItem('admin_token', access_token)
        
        return response.data

      } catch (error) {
        this.logout() // 確保登入失敗時狀態被清除
        if (error.response) {
          await handleApiError(error.response, '登入失敗')
        } else {
          // 重新拋出非 API 錯誤 (例如網路問題或上面手動拋出的權限錯誤)
          throw error
        }
      }
    },

    async checkAuth() {
      if (!this.token) {
        this.logout()
        return false
      }

      try {
        const response = await api.get('/api/auth/me')
        const user = response.data
        
        if (user.role !== 'admin') {
          this.logout()
          return false
        }
        
        this.user = user
        this.isAuthenticated = true
        return true

      } catch (error) {
        this.logout()
        console.warn('認證檢查失敗:', error)
        // 【核心修正點 2】: 向上拋出錯誤，讓路由守衛可以捕捉到
        throw error
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('admin_token')
    },
  },
})
