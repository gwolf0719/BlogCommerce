import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('admin_token'),
    user: null,
    isAuthenticated: false
  }),

  actions: {
    async login(credentials) {
      try {
        const response = await axios.post('/api/auth/login', credentials)
        const { access_token, user } = response.data
        
        // 檢查是否為管理員
        if (user.role !== 'admin') {
          throw new Error('權限不足，需要管理員權限')
        }
        
        this.token = access_token
        this.user = user
        this.isAuthenticated = true
        
        localStorage.setItem('admin_token', access_token)
        
        // 設置 axios 預設 header
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        return response.data
      } catch (error) {
        this.logout()
        if (error.response?.data?.detail) {
          throw new Error(error.response.data.detail)
        }
        throw error
      }
    },

    async checkAuth() {
      if (!this.token) {
        return false
      }

      try {
        const response = await axios.get('/api/auth/me', {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        
        const user = response.data
        if (user.role !== 'admin') {
          this.logout()
          return false
        }
        
        this.user = user
        this.isAuthenticated = true
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        return true
      } catch (error) {
        this.logout()
        return false
      }
    },

    logout() {
      this.token = null
      this.user = null
      this.isAuthenticated = false
      localStorage.removeItem('admin_token')
      delete axios.defaults.headers.common['Authorization']
    }
  }
}) 