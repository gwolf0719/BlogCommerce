import api from './axios'
import { message } from 'ant-design-vue'

/**
 * 前端錯誤處理器
 * 自動捕獲各種類型的錯誤並發送到後端記錄
 */
class ErrorHandler {
  constructor() {
    this.isInitialized = false
    this.errorQueue = []
    this.isOnline = navigator.onLine
    
    // 監聽網路狀態變化
    window.addEventListener('online', () => {
      this.isOnline = true
      this.flushErrorQueue()
    })
    
    window.addEventListener('offline', () => {
      this.isOnline = false
    })
  }

  /**
   * 初始化錯誤處理器
   */
  init() {
    if (this.isInitialized) return
    
    // 捕獲未處理的 JavaScript 錯誤
    window.addEventListener('error', this.handleError.bind(this))
    
    // 捕獲未處理的 Promise 拒絕
    window.addEventListener('unhandledrejection', this.handlePromiseRejection.bind(this))
    
    // 捕獲 Vue.js 錯誤（如果使用 Vue.js）
    if (window.Vue && window.Vue.config) {
      window.Vue.config.errorHandler = this.handleVueError.bind(this)
    }
    
    // 捕獲網路錯誤
    this.interceptXHRErrors()
    
    this.isInitialized = true
    console.log('ErrorHandler 已初始化')
  }

  /**
   * 處理一般 JavaScript 錯誤
   */
  handleError(event) {
    const error = {
      error_type: 'JavaScriptError',
      error_message: event.message || '未知錯誤',
      stack_trace: event.error?.stack || null,
      url: window.location.href,
      severity: 'medium',
      browser_info: this.getBrowserInfo(),
      device_info: this.getDeviceInfo(),
      tags: ['javascript', 'runtime'],
      additional_info: {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      }
    }
    
    this.logError(error)
  }

  /**
   * 處理 Promise 拒絕
   */
  handlePromiseRejection(event) {
    const error = {
      error_type: 'PromiseRejection',
      error_message: event.reason?.message || event.reason || 'Promise 被拒絕',
      stack_trace: event.reason?.stack || null,
      url: window.location.href,
      severity: 'medium',
      browser_info: this.getBrowserInfo(),
      device_info: this.getDeviceInfo(),
      tags: ['promise', 'async'],
      additional_info: {
        reason: event.reason
      }
    }
    
    this.logError(error)
  }

  /**
   * 處理 Vue.js 錯誤
   */
  handleVueError(err, vm, info) {
    const error = {
      error_type: 'VueError',
      error_message: err.message || err,
      stack_trace: err.stack || null,
      url: window.location.href,
      severity: 'high',
      browser_info: this.getBrowserInfo(),
      device_info: this.getDeviceInfo(),
      tags: ['vue', 'component'],
      additional_info: info
    }
    
    this.logError(error)
  }

  /**
   * 攔截 XHR 和 Fetch 錯誤
   */
  interceptXHRErrors() {
    // 攔截 XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open
    const originalXHRSend = XMLHttpRequest.prototype.send
    
    XMLHttpRequest.prototype.open = function(method, url, ...args) {
      this._errorHandler_method = method
      this._errorHandler_url = url
      return originalXHROpen.apply(this, [method, url, ...args])
    }
    
    XMLHttpRequest.prototype.send = function(data) {
      this.addEventListener('error', () => {
        errorHandler.handleNetworkError('XMLHttpRequest', this._errorHandler_method, this._errorHandler_url, this.status)
      })
      
      this.addEventListener('load', () => {
        if (this.status >= 400) {
          errorHandler.handleNetworkError('XMLHttpRequest', this._errorHandler_method, this._errorHandler_url, this.status, this.responseText)
        }
      })
      
      return originalXHRSend.apply(this, [data])
    }

    // 攔截 Fetch API
    const originalFetch = window.fetch
    window.fetch = async function(...args) {
      try {
        const response = await originalFetch.apply(this, args)
        
        if (!response.ok) {
          const url = typeof args[0] === 'string' ? args[0] : args[0].url
          const method = args[1]?.method || 'GET'
          const responseText = await response.text().catch(() => '')
          
          errorHandler.handleNetworkError('Fetch', method, url, response.status, responseText)
        }
        
        return response
      } catch (error) {
        const url = typeof args[0] === 'string' ? args[0] : args[0].url
        const method = args[1]?.method || 'GET'
        
        errorHandler.handleNetworkError('Fetch', method, url, 0, error.message)
        throw error
      }
    }
  }

  /**
   * 處理網路錯誤
   */
  handleNetworkError(type, method, url, status, responseText = '') {
    // 僅記錄到控制台，不發送到後端
    const error = {
      error_type: 'NetworkError',
      error_message: `${type} 請求失敗: ${method} ${url} (${status})`,
      stack_trace: null,
      url: window.location.href,
      severity: status >= 500 ? 'critical' : 'medium',
      browser_info: this.getBrowserInfo(),
      device_info: this.getDeviceInfo(),
      tags: ['network', 'api'],
      request_data: {
        method,
        url,
        status,
        response: responseText?.substring(0, 1000) // 限制響應內容長度
      }
    }
    
    console.warn('網路錯誤:', error)
  }

  /**
   * 手動記錄錯誤
   */
  logManualError(errorType, errorMessage, additionalData = {}) {
    const error = {
      error_type: errorType,
      error_message: errorMessage,
      stack_trace: new Error().stack,
      url: window.location.href,
      severity: additionalData.severity || 'medium',
      browser_info: this.getBrowserInfo(),
      device_info: this.getDeviceInfo(),
      tags: additionalData.tags || ['manual'],
      ...additionalData
    }
    
    console.warn('手動記錄錯誤:', error)
  }

  /**
   * 記錄錯誤到後端
   */
  async logError(error) {
    if (!this.isOnline) {
      this.errorQueue.push(error)
      return
    }

    try {
      await api.post('/api/errors/log', error)
    } catch (logError) {
      console.error('記錄錯誤失敗:', logError)
      this.errorQueue.push(error)
    }
  }

  /**
   * 發送錯誤隊列
   */
  async flushErrorQueue() {
    if (this.errorQueue.length === 0) return

    const errorsToSend = [...this.errorQueue]
    this.errorQueue = []

    for (const error of errorsToSend) {
      try {
        await api.post('/api/errors/log', error)
      } catch (logError) {
        console.error('發送錯誤隊列失敗:', logError)
        this.errorQueue.push(error)
      }
    }
  }

  /**
   * 獲取瀏覽器信息
   */
  getBrowserInfo() {
    return {
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      cookieEnabled: navigator.cookieEnabled,
      onLine: navigator.onLine
    }
  }

  /**
   * 獲取設備信息
   */
  getDeviceInfo() {
    return {
      screenWidth: screen.width,
      screenHeight: screen.height,
      viewportWidth: window.innerWidth,
      viewportHeight: window.innerHeight,
      colorDepth: screen.colorDepth,
      pixelDepth: screen.pixelDepth
    }
  }
}

// 創建全局實例
const errorHandler = new ErrorHandler()

/**
 * 統一的API錯誤處理函數
 * 用於處理所有API請求的錯誤響應
 */
export const handleApiError = async (response, defaultMessage = '操作失敗') => {
  let errorMessage = defaultMessage
  
  try {
    const errorData = await response.json()
    
    // 處理 FastAPI 驗證錯誤格式
    if (errorData.detail && Array.isArray(errorData.detail)) {
      const errors = errorData.detail.map(err => err.msg || err.message || '未知錯誤')
      errorMessage = errors.join(', ')
    } else if (errorData.detail && typeof errorData.detail === 'string') {
      errorMessage = errorData.detail
    } else if (errorData.message) {
      errorMessage = errorData.message
    } else if (errorData.msg) {
      errorMessage = errorData.msg
    }
  } catch (parseError) {
    console.error('解析錯誤響應失敗:', parseError)
    // 如果無法解析JSON，使用HTTP狀態碼的默認訊息
    switch (response.status) {
      case 400:
        errorMessage = '請求格式錯誤'
        break
      case 401:
        errorMessage = '未授權，請重新登入'
        break
      case 403:
        errorMessage = '權限不足'
        break
      case 404:
        errorMessage = '資源不存在'
        break
      case 422:
        errorMessage = '資料驗證失敗'
        break
      case 500:
        errorMessage = '伺服器內部錯誤'
        break
      default:
        errorMessage = `請求失敗 (${response.status})`
    }
  }
  
  // 顯示錯誤訊息
  message.error(errorMessage)
  
  // 記錄錯誤
  errorHandler.logManualError('ApiError', errorMessage, {
    status: response.status,
    url: response.url,
    severity: response.status >= 500 ? 'critical' : 'medium',
    tags: ['api', 'http']
  })
  
  return new Error(errorMessage)
}

/**
 * 統一的API請求包裝函數
 * 自動處理錯誤並顯示提示
 */
export const apiRequest = async (requestFn, successMessage = null) => {
  try {
    const response = await requestFn()
    
    if (!response.ok) {
      throw await handleApiError(response)
    }
    
    const data = await response.json()
    
    if (successMessage) {
      message.success(successMessage)
    }
    
    return data
  } catch (error) {
    // 錯誤已經在 handleApiError 中處理過了
    throw error
  }
}

/**
 * 統一的fetch請求包裝函數
 * 自動添加認證頭和錯誤處理
 */
export const authenticatedFetch = async (url, options = {}) => {
  const token = localStorage.getItem('admin_token')
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers
    }
  }
  
  const finalOptions = { ...defaultOptions, ...options }
  
  return fetch(url, finalOptions)
}

export default errorHandler 