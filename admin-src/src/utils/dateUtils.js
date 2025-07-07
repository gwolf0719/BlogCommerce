// 通用時間處理工具函數

/**
 * 格式化日期時間，正確處理 UTC 時間轉換為台灣時間
 * @param {string} dateString - 日期時間字串
 * @param {object} options - 格式選項
 * @returns {string} 格式化後的日期時間字串
 */
export const formatDate = (dateString, options = {}) => {
  if (!dateString) return ''
  
  // 確保正確處理 UTC 時間
  let date
  if (dateString.includes('T') && !dateString.includes('Z') && !dateString.includes('+')) {
    // 如果是 ISO 格式但沒有時區，假設它是 UTC 時間
    date = new Date(dateString + 'Z')
  } else {
    date = new Date(dateString)
  }
  
  // 檢查日期是否有效
  if (isNaN(date.getTime())) {
    return '無效日期'
  }
  
  const defaultOptions = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Asia/Taipei'
  }
  
  return date.toLocaleString('zh-TW', { ...defaultOptions, ...options })
}

/**
 * 格式化相對時間（幾分鐘前、幾小時前等）
 * @param {string} dateString - 日期時間字串
 * @returns {string} 相對時間字串
 */
export const formatTimeAgo = (dateString) => {
  if (!dateString) return ''
  
  const now = new Date()
  let date
  if (dateString.includes('T') && !dateString.includes('Z') && !dateString.includes('+')) {
    // 如果是 ISO 格式但沒有時區，假設是 UTC 時間
    date = new Date(dateString + 'Z')
  } else {
    date = new Date(dateString)
  }
  
  // 檢查日期是否有效
  if (isNaN(date.getTime())) {
    return '無效日期'
  }
  
  const diffInMinutes = Math.floor((now - date) / (1000 * 60))
  
  if (diffInMinutes < 1) return '剛剛'
  if (diffInMinutes < 60) return `${diffInMinutes} 分鐘前`
  
  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) return `${diffInHours} 小時前`
  
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 30) return `${diffInDays} 天前`
  
  const diffInMonths = Math.floor(diffInDays / 30)
  return `${diffInMonths} 個月前`
}

/**
 * 格式化僅日期部分
 * @param {string} dateString - 日期時間字串
 * @returns {string} 格式化後的日期字串
 */
export const formatDateOnly = (dateString) => {
  return formatDate(dateString, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    timeZone: 'Asia/Taipei'
  })
}

/**
 * 格式化僅時間部分
 * @param {string} dateString - 日期時間字串
 * @returns {string} 格式化後的時間字串
 */
export const formatTimeOnly = (dateString) => {
  return formatDate(dateString, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZone: 'Asia/Taipei'
  })
}

/**
 * 檢查日期是否為今天
 * @param {string} dateString - 日期時間字串
 * @returns {boolean} 是否為今天
 */
export const isToday = (dateString) => {
  if (!dateString) return false
  
  let date
  if (dateString.includes('T') && !dateString.includes('Z') && !dateString.includes('+')) {
    date = new Date(dateString + 'Z')
  } else {
    date = new Date(dateString)
  }
  
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

/**
 * 取得台灣時區的目前時間
 * @returns {string} ISO 格式的台灣時間字串
 */
export const getCurrentTaiwanTime = () => {
  return new Date().toLocaleString('sv-SE', { timeZone: 'Asia/Taipei' })
} 