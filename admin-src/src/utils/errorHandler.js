import api from './axios'

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
      url: event.filename || window.location.href,
      line_number: event.lineno,
      column_number: event.colno,
      severity: 'high',
      browser_info: this.getBrowserInfo(),
      device_info: this.getDeviceInfo(),
      tags: ['javascript', 'runtime']
    }
    
    this.logError(error)
  }

  /**
   * 處理未處理的 Promise 拒絕
   */
  handlePromiseRejection(event) {
    const error = {
      error_type: 'UnhandledPromiseRejection',
      error_message: event.reason?.message || event.reason || '未處理的 Promise 拒絕',
      stack_trace: event.reason?.stack || null,
      url: window.location.href,
      severity: 'high',
      browser_info: this.getBrowserInfo(),
      device_info: this.getDeviceInfo(),
      tags: ['promise', 'async']
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
   * 記錄錯誤到控制台
   */
  async logError(errorData) {
    // 僅記錄到控制台，不發送到後端
    console.warn('應用程式錯誤:', errorData)
  }

  /**
   * 清空錯誤佇列（已停用）
   */
  async flushErrorQueue() {
    // 錯誤佇列功能已停用，不再需要實作
    console.log('錯誤佇列功能已停用')
  }

  /**
   * 取得瀏覽器資訊
   */
  getBrowserInfo() {
    const navigator = window.navigator
    return {
      userAgent: navigator.userAgent,
      language: navigator.language,
      languages: navigator.languages,
      platform: navigator.platform,
      cookieEnabled: navigator.cookieEnabled,
      onLine: navigator.onLine,
      doNotTrack: navigator.doNotTrack
    }
  }

  /**
   * 取得設備資訊
   */
  getDeviceInfo() {
    return {
      screen: {
        width: window.screen.width,
        height: window.screen.height,
        colorDepth: window.screen.colorDepth
      },
      window: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      devicePixelRatio: window.devicePixelRatio,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      timestamp: new Date().toISOString()
    }
  }

  /**
   * 取得當前用戶資訊（如果已登入）
   */
  getCurrentUser() {
    try {
      const token = localStorage.getItem('admin_token')
      if (token) {
        // 解碼 JWT token 來取得用戶資訊（簡化版本）
        const payload = JSON.parse(atob(token.split('.')[1]))
        return payload.sub // 用戶 ID
      }
    } catch (e) {
      // 忽略錯誤
    }
    return null
  }
}

// 建立全域實例
const errorHandler = new ErrorHandler()

// 自動初始化
document.addEventListener('DOMContentLoaded', () => {
  errorHandler.init()
})

// 如果 DOM 已經載入完成，立即初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => errorHandler.init())
} else {
  errorHandler.init()
}

export default errorHandler 