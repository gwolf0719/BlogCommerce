/**
 * 前台系統統一錯誤處理工具
 * 用於處理所有API請求的錯誤響應
 */

/**
 * 顯示通知訊息
 * @param {string} message - 訊息內容
 * @param {string} type - 訊息類型 (success, error, info)
 */
function showNotification(message, type = 'info') {
  // 創建通知元素
  const notification = document.createElement('div');
  notification.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-xl shadow-lg transition-all duration-300 transform translate-x-full ${
    type === 'success' ? 'bg-green-500 text-white' : 
    type === 'error' ? 'bg-red-500 text-white' : 
    'bg-blue-500 text-white'
  }`;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  // 顯示動畫
  setTimeout(() => {
    notification.classList.remove('translate-x-full');
  }, 100);
  
  // 自動隱藏
  setTimeout(() => {
    notification.classList.add('translate-x-full');
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 300);
  }, 5000);
}

/**
 * 統一的API錯誤處理函數
 * @param {Response} response - fetch響應對象
 * @param {string} defaultMessage - 默認錯誤訊息
 * @returns {Error} 錯誤對象
 */
async function handleApiError(response, defaultMessage = '操作失敗') {
  let errorMessage = defaultMessage;
  
  try {
    const errorData = await response.json();
    
    // 處理 FastAPI 驗證錯誤格式
    if (errorData.detail && Array.isArray(errorData.detail)) {
      const errors = errorData.detail.map(err => err.msg || err.message || '未知錯誤');
      errorMessage = errors.join(', ');
    } else if (errorData.detail && typeof errorData.detail === 'string') {
      errorMessage = errorData.detail;
    } else if (errorData.message) {
      errorMessage = errorData.message;
    } else if (errorData.msg) {
      errorMessage = errorData.msg;
    }
  } catch (parseError) {
    console.error('解析錯誤響應失敗:', parseError);
    // 如果無法解析JSON，使用HTTP狀態碼的默認訊息
    switch (response.status) {
      case 400:
        errorMessage = '請求格式錯誤';
        break;
      case 401:
        errorMessage = '未授權，請重新登入';
        break;
      case 403:
        errorMessage = '權限不足';
        break;
      case 404:
        errorMessage = '資源不存在';
        break;
      case 422:
        errorMessage = '資料驗證失敗';
        break;
      case 500:
        errorMessage = '伺服器內部錯誤';
        break;
      default:
        errorMessage = `請求失敗 (${response.status})`;
    }
  }
  
  // 顯示錯誤訊息
  showNotification(errorMessage, 'error');
  
  // 記錄錯誤到控制台
  console.error('API錯誤:', {
    status: response.status,
    url: response.url,
    message: errorMessage
  });
  
  return new Error(errorMessage);
}

/**
 * 統一的API請求包裝函數
 * @param {Function} requestFn - 請求函數
 * @param {string} successMessage - 成功訊息
 * @returns {Promise} 請求結果
 */
async function apiRequest(requestFn, successMessage = null) {
  try {
    const response = await requestFn();
    
    if (!response.ok) {
      throw await handleApiError(response);
    }
    
    const data = await response.json();
    
    if (successMessage) {
      showNotification(successMessage, 'success');
    }
    
    return data;
  } catch (error) {
    // 錯誤已經在 handleApiError 中處理過了
    throw error;
  }
}

/**
 * 統一的fetch請求包裝函數
 * @param {string} url - 請求URL
 * @param {Object} options - 請求選項
 * @returns {Promise} fetch響應
 */
async function authenticatedFetch(url, options = {}) {
  const token = localStorage.getItem('access_token');
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers
    }
  };
  
  const finalOptions = { ...defaultOptions, ...options };
  
  return fetch(url, finalOptions);
}

/**
 * 檢查用戶是否已登入
 * @returns {boolean} 是否已登入
 */
function isLoggedIn() {
  return !!localStorage.getItem('access_token');
}

/**
 * 重定向到登入頁面
 * @param {string} returnUrl - 登入後重定向的URL
 */
function redirectToLogin(returnUrl = null) {
  if (returnUrl) {
    localStorage.setItem('redirect_after_login', returnUrl);
  }
  window.location.href = '/login';
}

// 導出函數供其他模組使用
window.ErrorHandler = {
  showNotification,
  handleApiError,
  apiRequest,
  authenticatedFetch,
  isLoggedIn,
  redirectToLogin
}; 