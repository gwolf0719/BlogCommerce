import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  // 狀態
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 計算屬性
  const itemsCount = computed(() => {
    return items.value.reduce((total, item) => total + item.quantity, 0)
  })

  const totalPrice = computed(() => {
    return items.value.reduce((total, item) => {
      return total + (item.price * item.quantity)
    }, 0)
  })

  const isEmpty = computed(() => items.value.length === 0)

  // 從 localStorage 載入購物車
  const loadCart = () => {
    try {
      const savedCart = localStorage.getItem('cart_items')
      if (savedCart) {
        items.value = JSON.parse(savedCart)
      }
    } catch (err) {
      console.error('載入購物車失敗:', err)
      items.value = []
    }
  }

  // 儲存購物車到 localStorage
  const saveCart = () => {
    try {
      localStorage.setItem('cart_items', JSON.stringify(items.value))
    } catch (err) {
      console.error('儲存購物車失敗:', err)
    }
  }

  // 添加商品到購物車
  const addItem = (product, quantity = 1) => {
    try {
      const existingItem = items.value.find(item => item.id === product.id)
      
      if (existingItem) {
        // 如果商品已存在，增加數量
        existingItem.quantity += quantity
      } else {
        // 新增商品
        items.value.push({
          id: product.id,
          name: product.name,
          price: product.price,
          image: product.image,
          slug: product.slug,
          quantity: quantity,
          stock: product.stock || 999
        })
      }
      
      saveCart()
      return { success: true }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    }
  }

  // 移除購物車商品
  const removeItem = (productId) => {
    try {
      const index = items.value.findIndex(item => item.id === productId)
      if (index > -1) {
        items.value.splice(index, 1)
        saveCart()
      }
      return { success: true }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    }
  }

  // 更新商品數量
  const updateQuantity = (productId, quantity) => {
    try {
      if (quantity <= 0) {
        return removeItem(productId)
      }

      const item = items.value.find(item => item.id === productId)
      if (item) {
        // 檢查庫存
        if (quantity > item.stock) {
          throw new Error(`庫存不足，最多只能購買 ${item.stock} 件`)
        }
        
        item.quantity = quantity
        saveCart()
      }
      return { success: true }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    }
  }

  // 清空購物車
  const clearCart = () => {
    try {
      items.value = []
      saveCart()
      return { success: true }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    }
  }

  // 獲取商品在購物車中的數量
  const getItemQuantity = (productId) => {
    const item = items.value.find(item => item.id === productId)
    return item ? item.quantity : 0
  }

  // 檢查商品是否在購物車中
  const isInCart = (productId) => {
    return items.value.some(item => item.id === productId)
  }

  // 格式化價格
  const formatPrice = (price) => {
    return new Intl.NumberFormat('zh-TW', {
      style: 'currency',
      currency: 'TWD',
      minimumFractionDigits: 0
    }).format(price)
  }

  // 計算運費
  const calculateShipping = () => {
    const freeShippingThreshold = 1000 // 免運門檻
    const shippingCost = 100 // 運費
    
    return totalPrice.value >= freeShippingThreshold ? 0 : shippingCost
  }

  // 計算總金額（含運費）
  const totalWithShipping = computed(() => {
    return totalPrice.value + calculateShipping()
  })

  // 驗證購物車（檢查庫存等）
  const validateCart = async () => {
    loading.value = true
    error.value = null

    try {
      // 這裡可以向後端 API 驗證庫存
      // const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      // const response = await fetch(`${API_BASE_URL}/api/cart/validate`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ items: items.value })
      // })

      // 目前先做本地驗證
      const invalidItems = items.value.filter(item => item.quantity > item.stock)
      
      if (invalidItems.length > 0) {
        const invalidItemNames = invalidItems.map(item => item.name).join(', ')
        throw new Error(`以下商品庫存不足: ${invalidItemNames}`)
      }

      return { success: true, valid: true }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message, valid: false }
    } finally {
      loading.value = false
    }
  }

  // 結帳準備
  const prepareCheckout = () => {
    return {
      items: items.value.map(item => ({
        product_id: item.id,
        quantity: item.quantity,
        price: item.price
      })),
      subtotal: totalPrice.value,
      shipping: calculateShipping(),
      total: totalWithShipping.value
    }
  }

  return {
    // 狀態
    items,
    loading,
    error,
    
    // 計算屬性
    itemsCount,
    totalPrice,
    totalWithShipping,
    isEmpty,
    
    // 動作
    loadCart,
    saveCart,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    getItemQuantity,
    isInCart,
    formatPrice,
    calculateShipping,
    validateCart,
    prepareCheckout
  }
}) 