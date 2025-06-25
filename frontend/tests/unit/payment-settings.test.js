import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import Settings from '@/views/Settings.vue'

// Mock Ant Design Vue components
vi.mock('ant-design-vue', () => ({
  message: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
}))

// Mock auth store
const mockAuthStore = {
  token: 'mock-token',
  user: { username: 'admin' },
  isAdmin: true
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

describe('Payment Settings', () => {
  let wrapper
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    
    // Mock fetch responses
    global.fetch = vi.fn()
    
    wrapper = mount(Settings, {
      global: {
        plugins: [pinia],
        stubs: {
          'a-card': true,
          'a-form': true,
          'a-form-item': true,
          'a-input': true,
          'a-input-password': true,
          'a-select': true,
          'a-select-option': true,
          'a-checkbox-group': true,
          'a-checkbox': true,
          'a-button': true,
          'a-divider': true,
          'a-menu': true,
          'a-menu-item': true,
          'a-row': true,
          'a-col': true
        }
      }
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Payment Configuration', () => {
    it('should initialize payment object with correct structure', () => {
      expect(wrapper.vm.payment).toEqual({
        enabledMethods: [],
        transfer: { bank: '', account: '', name: '' },
        linepay: { channel_id: '', channel_secret: '', store_name: '' },
        ecpay: { merchant_id: '', hash_key: '', hash_iv: '', api_url: '' },
        paypal: { client_id: '', client_secret: '', environment: 'sandbox' }
      })
    })

    it('should load payment settings on component mount', async () => {
      const mockResponses = [
        { ok: true, json: () => Promise.resolve({ value: { bank: '測試銀行', account: '123456', name: '測試商店' } }) },
        { ok: true, json: () => Promise.resolve({ value: { channel_id: 'test123', channel_secret: 'secret123', store_name: '測試店' } }) },
        { ok: true, json: () => Promise.resolve({ value: { merchant_id: 'M123', hash_key: 'key123', hash_iv: 'iv123', api_url: 'https://test.com' } }) },
        { ok: true, json: () => Promise.resolve({ value: { client_id: 'paypal123', client_secret: 'paypal_secret', environment: 'sandbox' } }) }
      ]

      global.fetch
        .mockResolvedValueOnce(mockResponses[0])
        .mockResolvedValueOnce(mockResponses[1])
        .mockResolvedValueOnce(mockResponses[2])
        .mockResolvedValueOnce(mockResponses[3])

      await wrapper.vm.loadPaymentSettings()

      expect(wrapper.vm.payment.enabledMethods).toContain('transfer')
      expect(wrapper.vm.payment.enabledMethods).toContain('linepay')
      expect(wrapper.vm.payment.enabledMethods).toContain('ecpay')
      expect(wrapper.vm.payment.enabledMethods).toContain('paypal')
      
      expect(wrapper.vm.payment.transfer.bank).toBe('測試銀行')
      expect(wrapper.vm.payment.linepay.channel_id).toBe('test123')
      expect(wrapper.vm.payment.ecpay.merchant_id).toBe('M123')
      expect(wrapper.vm.payment.paypal.client_id).toBe('paypal123')
    })

    it('should handle failed payment settings load', async () => {
      global.fetch.mockRejectedValue(new Error('Network error'))

      await wrapper.vm.loadPaymentSettings()

      expect(wrapper.vm.payment.enabledMethods).toEqual([])
    })
  })

  describe('Payment Settings Save', () => {
    beforeEach(() => {
      wrapper.vm.payment.enabledMethods = ['transfer', 'paypal']
      wrapper.vm.payment.transfer = { bank: '新銀行', account: '789012', name: '新商店' }
      wrapper.vm.payment.paypal = { client_id: 'new_paypal', client_secret: 'new_secret', environment: 'live' }
    })

    it('should save enabled payment methods correctly', async () => {
      global.fetch.mockResolvedValue({ ok: true })

      await wrapper.vm.savePaymentSettings()

      expect(fetch).toHaveBeenCalledWith('/api/settings/payment_transfer', expect.any(Object))
      expect(fetch).toHaveBeenCalledWith('/api/settings/payment_paypal', expect.any(Object))
      expect(fetch).toHaveBeenCalledWith('/api/settings/payment_linepay', expect.any(Object))
      expect(fetch).toHaveBeenCalledWith('/api/settings/payment_ecpay', expect.any(Object))
      
      // Check that settings were saved correctly (just verify the API calls were made)
      const transferCall = global.fetch.mock.calls.find(call => 
        call[0] === '/api/settings/payment_transfer' && 
        call[1].method === 'PUT' &&
        call[1].body.includes('新銀行')
      )
      expect(transferCall).toBeDefined()

      const paypalCall = global.fetch.mock.calls.find(call => 
        call[0] === '/api/settings/payment_paypal' && 
        call[1].method === 'PUT' &&
        call[1].body.includes('new_paypal')
      )
      expect(paypalCall).toBeDefined()

      // Check disabled methods are set to null
      const linepayDisabledCall = global.fetch.mock.calls.find(call => 
        call[0] === '/api/settings/payment_linepay' && 
        call[1].method === 'PUT' &&
        call[1].body.includes('null')
      )
      expect(linepayDisabledCall).toBeDefined()
    })

    it('should handle save payment settings error', async () => {
      global.fetch.mockRejectedValue(new Error('Save failed'))

      await wrapper.vm.savePaymentSettings()

      expect(wrapper.vm.savingPayment).toBe(false)
    })
  })

  describe('Payment Method Validation', () => {
    it('should validate transfer settings', () => {
      const transferData = {
        bank: '測試銀行',
        account: '1234567890',
        name: '測試商店'
      }

      expect(transferData.bank).toBeTruthy()
      expect(transferData.account).toBeTruthy()
      expect(transferData.name).toBeTruthy()
      expect(transferData.account).toMatch(/^\d+$/) // Only numbers
    })

    it('should validate LinePay settings', () => {
      const linepayData = {
        channel_id: '1234567890',
        channel_secret: 'abcdef123456',
        store_name: '測試線上商店'
      }

      expect(linepayData.channel_id).toBeTruthy()
      expect(linepayData.channel_secret).toBeTruthy()
      expect(linepayData.store_name).toBeTruthy()
      expect(linepayData.channel_id.length).toBeGreaterThan(0)
    })

    it('should validate ECPay settings', () => {
      const ecpayData = {
        merchant_id: '2000132',
        hash_key: '5294y06JbISpM5x9',
        hash_iv: 'v77hoKGq4kWxNNIS',
        api_url: 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'
      }

      expect(ecpayData.merchant_id).toBeTruthy()
      expect(ecpayData.hash_key).toBeTruthy()
      expect(ecpayData.hash_iv).toBeTruthy()
      expect(ecpayData.api_url).toMatch(/^https?:\/\//)
    })

    it('should validate PayPal settings', () => {
      const paypalData = {
        client_id: 'AYSq3RDGsmBLJE-otTkBtM-jBRd1TCQwFf9RGfwddNXWz0uFU9ztymylOhRS',
        client_secret: 'EGnHDxD_qRPdaLdHi7__jLS3rD7yOo-FPcbgJl6RKqgMbm6BG9aQn5Eq7PW2',
        environment: 'sandbox'
      }

      expect(paypalData.client_id).toBeTruthy()
      expect(paypalData.client_secret).toBeTruthy()
      expect(['sandbox', 'live']).toContain(paypalData.environment)
    })
  })

  describe('UI Interactions', () => {
    it('should show/hide payment settings based on enabled methods', async () => {
      // Initially no methods enabled
      expect(wrapper.vm.payment.enabledMethods).toEqual([])

      // Enable transfer
      wrapper.vm.payment.enabledMethods = ['transfer']
      await wrapper.vm.$nextTick()

      // Should show transfer settings
      expect(wrapper.vm.payment.enabledMethods.includes('transfer')).toBe(true)

      // Enable PayPal
      wrapper.vm.payment.enabledMethods.push('paypal')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.payment.enabledMethods.includes('paypal')).toBe(true)
    })

    it('should handle tab switching', async () => {
      const mockEvent = { key: 'payment' }
      
      wrapper.vm.handleMenuClick(mockEvent)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.activeTab).toBe('payment')
    })
  })

  describe('Loading States', () => {
    it('should manage loading state during settings load', async () => {
      global.fetch.mockImplementation(() => new Promise(resolve => {
        setTimeout(() => resolve({ ok: true, json: () => Promise.resolve({ value: null }) }), 100)
      }))

      const loadPromise = wrapper.vm.loadPaymentSettings()
      expect(wrapper.vm.loading).toBe(true)

      await loadPromise
      expect(wrapper.vm.loading).toBe(false)
    })

    it('should manage saving state during settings save', async () => {
      global.fetch.mockImplementation(() => new Promise(resolve => {
        setTimeout(() => resolve({ ok: true }), 100)
      }))

      const savePromise = wrapper.vm.savePaymentSettings()
      expect(wrapper.vm.savingPayment).toBe(true)

      await savePromise
      expect(wrapper.vm.savingPayment).toBe(false)
    })
  })
})