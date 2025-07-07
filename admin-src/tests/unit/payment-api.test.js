import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock payment API functions
class PaymentAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL
    this.token = null
  }

  setToken(token) {
    this.token = token
  }

  async createPayment(orderData) {
    const response = await fetch(`${this.baseURL}/api/payment/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify(orderData)
    })
    return response.json()
  }

  async getPaymentStatus(orderId) {
    const response = await fetch(`${this.baseURL}/api/payment/status/${orderId}`)
    return response.json()
  }

  async confirmPayment(orderData) {
    const response = await fetch(`${this.baseURL}/api/payment/manual-confirm`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify(orderData)
    })
    return response.json()
  }

  async testPaymentMethod(method) {
    const response = await fetch(`${this.baseURL}/api/payment/test/${method}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    })
    return response.json()
  }
}

describe('Payment API', () => {
  let api
  let mockFetch

  beforeEach(() => {
    api = new PaymentAPI('http://localhost:8000')
    api.setToken('test-token')
    
    mockFetch = vi.fn()
    global.fetch = mockFetch
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Payment Creation', () => {
    it('should create payment order successfully', async () => {
      const mockResponse = {
        success: true,
        message: '付款訂單建立成功',
        data: {
          payment_method: 'transfer',
          order_id: 'TEST001',
          amount: '399.00',
          bank_info: {
            bank: '國泰世華銀行',
            account: '1234567890',
            name: 'BlogCommerce 商店'
          }
        }
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const orderData = {
        order_id: 'TEST001',
        payment_method: 'transfer'
      }

      const result = await api.createPayment(orderData)

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/payment/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        },
        body: JSON.stringify(orderData)
      })

      expect(result.success).toBe(true)
      expect(result.data.payment_method).toBe('transfer')
      expect(result.data.order_id).toBe('TEST001')
    })

    it('should handle payment creation failure', async () => {
      const mockErrorResponse = {
        success: false,
        message: '付款方式設定錯誤'
      }

      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve(mockErrorResponse)
      })

      const orderData = {
        order_id: 'TEST002',
        payment_method: 'invalid_method'
      }

      const result = await api.createPayment(orderData)

      expect(result.success).toBe(false)
      expect(result.message).toContain('錯誤')
    })
  })

  describe('Payment Status', () => {
    it('should get payment status successfully', async () => {
      const mockStatusResponse = {
        order_id: 'TEST001',
        payment_method: 'transfer',
        payment_status: 'pending',
        payment_info: {
          bank_info: {
            bank: '國泰世華銀行',
            account: '1234567890'
          }
        },
        updated_at: '2025-06-25T12:00:00Z'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockStatusResponse)
      })

      const result = await api.getPaymentStatus('TEST001')

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/payment/status/TEST001')
      expect(result.order_id).toBe('TEST001')
      expect(result.payment_status).toBe('pending')
    })

    it('should handle order not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ detail: '訂單不存在' })
      })

      const result = await api.getPaymentStatus('NONEXISTENT')

      expect(result.detail).toBe('訂單不存在')
    })
  })

  describe('Manual Payment Confirmation', () => {
    it('should confirm payment manually', async () => {
      const mockConfirmResponse = {
        success: true,
        message: '付款已手動確認',
        order_id: 'TEST001'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockConfirmResponse)
      })

      const confirmData = {
        order_id: 'TEST001',
        notes: '客戶已轉帳，手動確認'
      }

      const result = await api.confirmPayment(confirmData)

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/payment/manual-confirm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        },
        body: JSON.stringify(confirmData)
      })

      expect(result.success).toBe(true)
      expect(result.order_id).toBe('TEST001')
    })

    it('should handle unauthorized access', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: 'Unauthorized' })
      })

      const confirmData = {
        order_id: 'TEST001',
        notes: '測試確認'
      }

      const result = await api.confirmPayment(confirmData)

      expect(result.detail).toBe('Unauthorized')
    })
  })

  describe('Payment Method Testing', () => {
    const paymentMethods = ['transfer', 'linepay', 'ecpay', 'paypal']

    paymentMethods.forEach(method => {
      it(`should test ${method} payment method`, async () => {
        const mockTestResponse = {
          success: true,
          message: `${method} 金流測試成功`,
          test_data: {
            payment_method: method,
            order_id: `TEST_${method.toUpperCase()}_001`,
            amount: '1.00'
          }
        }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockTestResponse)
        })

        const result = await api.testPaymentMethod(method)

        expect(mockFetch).toHaveBeenCalledWith(`http://localhost:8000/api/payment/test/${method}`, {
          headers: {
            'Authorization': 'Bearer test-token'
          }
        })

        expect(result.success).toBe(true)
        expect(result.test_data.payment_method).toBe(method)
      })
    })

    it('should handle unsupported payment method', async () => {
      const mockErrorResponse = {
        success: false,
        message: 'unsupported_method 金流測試失敗: 不支援的付款方式'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockErrorResponse)
      })

      const result = await api.testPaymentMethod('unsupported_method')

      expect(result.success).toBe(false)
      expect(result.message).toContain('不支援的付款方式')
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'))

      try {
        await api.createPayment({ order_id: 'TEST', payment_method: 'transfer' })
      } catch (error) {
        expect(error.message).toBe('Network error')
      }
    })

    it('should handle invalid JSON responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.reject(new Error('Invalid JSON'))
      })

      try {
        await api.getPaymentStatus('TEST001')
      } catch (error) {
        expect(error.message).toBe('Invalid JSON')
      }
    })

    it('should handle server errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: '內部服務器錯誤' })
      })

      const result = await api.createPayment({ order_id: 'TEST', payment_method: 'transfer' })

      expect(result.detail).toBe('內部服務器錯誤')
    })
  })

  describe('Authentication', () => {
    it('should include authorization header when token is set', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true })
      })

      api.setToken('new-test-token')
      await api.createPayment({ order_id: 'TEST', payment_method: 'transfer' })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer new-test-token'
          })
        })
      )
    })

    it('should work without token for public endpoints', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ order_id: 'TEST001' })
      })

      api.setToken(null)
      await api.getPaymentStatus('TEST001')

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/payment/status/TEST001')
    })
  })
})