import { test, expect } from '@playwright/test'

test.describe('Payment API E2E Tests', () => {
  let adminToken
  let baseURL = 'http://localhost:8000'

  test.beforeAll(async ({ request }) => {
    // Login as admin
    try {
      const loginResponse = await request.post(`${baseURL}/api/auth/login`, {
        data: {
          username: 'admin',
          password: 'admin123'
        }
      })
      
      if (loginResponse.ok()) {
        const loginData = await loginResponse.json()
        adminToken = loginData.access_token
      }
    } catch (error) {
      console.log('Admin login failed, continuing with tests')
    }
  })

  test.describe('Payment Settings API', () => {
    test('should get and update transfer settings', async ({ request }) => {
      if (!adminToken) {
        test.skip('Admin token not available')
      }

      // Test GET payment settings
      const getResponse = await request.get(`${baseURL}/api/settings/payment_transfer`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      })

      expect(getResponse.status()).toBe(200)
      const getResult = await getResponse.json()
      expect(getResult).toHaveProperty('key', 'payment_transfer')

      // Test PUT payment settings
      const newSettings = {
        bank: '測試銀行 API',
        account: '9876543210',
        name: '測試商店 API'
      }

      const putResponse = await request.put(`${baseURL}/api/settings/payment_transfer`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        data: newSettings
      })

      expect(putResponse.status()).toBe(200)
      const putResult = await putResponse.json()
      expect(putResult.message).toContain('轉帳設定已更新')

      // Verify the settings were saved
      const verifyResponse = await request.get(`${baseURL}/api/settings/payment_transfer`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      })

      expect(verifyResponse.status()).toBe(200)
      const verifyResult = await verifyResponse.json()
      expect(verifyResult.value.bank).toBe('測試銀行 API')
    })

    test('should handle all payment method settings', async ({ request }) => {
      if (!adminToken) {
        test.skip('Admin token not available')
      }

      const paymentMethods = [
        {
          key: 'payment_linepay',
          data: {
            channel_id: 'test_channel_api',
            channel_secret: 'test_secret_api',
            store_name: '測試商店 API'
          }
        },
        {
          key: 'payment_ecpay',
          data: {
            merchant_id: 'TEST_MERCHANT_API',
            hash_key: 'test_hash_key_api',
            hash_iv: 'test_hash_iv_api',
            api_url: 'https://test-api.ecpay.com'
          }
        },
        {
          key: 'payment_paypal',
          data: {
            client_id: 'test_paypal_client_api',
            client_secret: 'test_paypal_secret_api',
            environment: 'sandbox'
          }
        }
      ]

      for (const method of paymentMethods) {
        // Test PUT
        const putResponse = await request.put(`${baseURL}/api/settings/${method.key}`, {
          headers: {
            'Authorization': `Bearer ${adminToken}`,
            'Content-Type': 'application/json'
          },
          data: method.data
        })

        expect(putResponse.status()).toBe(200)

        // Test GET
        const getResponse = await request.get(`${baseURL}/api/settings/${method.key}`, {
          headers: {
            'Authorization': `Bearer ${adminToken}`
          }
        })

        expect(getResponse.status()).toBe(200)
        const result = await getResponse.json()
        expect(result.key).toBe(method.key)
      }
    })
  })

  test.describe('Payment Processing API', () => {
    test('should create payment order', async ({ request }) => {
      if (!adminToken) {
        test.skip('Admin token not available')
      }

      // First setup transfer settings
      await request.put(`${baseURL}/api/settings/payment_transfer`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          bank: '測試銀行',
          account: '1234567890',
          name: '測試商店'
        }
      })

      // Create payment order
      const orderData = {
        order_id: `TEST_API_${Date.now()}`,
        payment_method: 'transfer'
      }

      const response = await request.post(`${baseURL}/api/payment/create`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        data: orderData
      })

      if (response.status() === 200) {
        const result = await response.json()
        expect(result.success).toBe(true)
        expect(result.data.payment_method).toBe('transfer')
        expect(result.data.order_id).toBe(orderData.order_id)
        expect(result.data.bank_info).toBeDefined()
        expect(result.data.bank_info.bank).toBe('測試銀行')
      } else {
        // Handle case where order doesn't exist
        expect(response.status()).toBe(404)
      }
    })

    test('should get payment status', async ({ request }) => {
      const orderId = 'TEST_STATUS_001'

      const response = await request.get(`${baseURL}/api/payment/status/${orderId}`)

      // Either order exists and returns status, or returns 404
      expect([200, 404]).toContain(response.status())

      if (response.status() === 200) {
        const result = await response.json()
        expect(result.order_id).toBe(orderId)
        expect(result).toHaveProperty('payment_status')
      }
    })

    test('should handle manual payment confirmation', async ({ request }) => {
      if (!adminToken) {
        test.skip('Admin token not available')
      }

      const confirmData = {
        order_id: 'TEST_MANUAL_API_001',
        notes: 'API 測試手動確認'
      }

      const response = await request.post(`${baseURL}/api/payment/manual-confirm`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        data: confirmData
      })

      // Either succeeds or order not found
      expect([200, 404]).toContain(response.status())

      if (response.status() === 200) {
        const result = await response.json()
        expect(result.success).toBe(true)
        expect(result.order_id).toBe(confirmData.order_id)
      }
    })
  })

  test.describe('Payment Testing API', () => {
    test('should test all payment methods', async ({ request }) => {
      if (!adminToken) {
        test.skip('Admin token not available')
      }

      const paymentMethods = ['transfer', 'linepay', 'ecpay', 'paypal']

      for (const method of paymentMethods) {
        const response = await request.get(`${baseURL}/api/payment/test/${method}`, {
          headers: {
            'Authorization': `Bearer ${adminToken}`
          }
        })

        expect(response.status()).toBe(200)
        const result = await response.json()
        
        // Should return test result
        expect(result).toHaveProperty('success')
        expect(result).toHaveProperty('message')
        
        if (result.success) {
          expect(result.test_data.payment_method).toBe(method)
        }
      }
    })

    test('should handle invalid payment method test', async ({ request }) => {
      if (!adminToken) {
        test.skip('Admin token not available')
      }

      const response = await request.get(`${baseURL}/api/payment/test/invalid_method`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      })

      expect(response.status()).toBe(200)
      const result = await response.json()
      expect(result.success).toBe(false)
      expect(result.message).toContain('不支援的付款方式')
    })
  })

  test.describe('Error Handling', () => {
    test('should handle unauthorized requests', async ({ request }) => {
      // Test without token
      const response = await request.get(`${baseURL}/api/settings/payment_transfer`)
      expect(response.status()).toBe(401)

      // Test with invalid token
      const invalidResponse = await request.get(`${baseURL}/api/settings/payment_transfer`, {
        headers: {
          'Authorization': 'Bearer invalid_token'
        }
      })
      expect(invalidResponse.status()).toBe(401)
    })

    test('should handle invalid data', async ({ request }) => {
      if (!adminToken) {
        test.skip('Admin token not available')
      }

      // Test with invalid JSON
      const response = await request.put(`${baseURL}/api/settings/payment_transfer`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        data: 'invalid json'
      })

      expect([400, 422]).toContain(response.status())
    })

    test('should handle missing payment settings', async ({ request }) => {
      if (!adminToken) {
        test.skip('Admin token not available')
      }

      // Clear transfer settings
      await request.put(`${baseURL}/api/settings/payment_transfer`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        data: null
      })

      // Try to create payment with missing settings
      const response = await request.post(`${baseURL}/api/payment/create`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          order_id: 'TEST_MISSING_SETTINGS',
          payment_method: 'transfer'
        }
      })

      expect(response.status()).toBe(400)
      const result = await response.json()
      expect(result.detail).toContain('設定')
    })
  })

  test.describe('Performance Tests', () => {
    test('should handle concurrent payment settings updates', async ({ request }) => {
      if (!adminToken) {
        test.skip('Admin token not available')
      }

      // Create multiple concurrent requests
      const requests = []
      for (let i = 0; i < 5; i++) {
        requests.push(
          request.put(`${baseURL}/api/settings/payment_transfer`, {
            headers: {
              'Authorization': `Bearer ${adminToken}`,
              'Content-Type': 'application/json'
            },
            data: {
              bank: `測試銀行 ${i}`,
              account: `12345${i}`,
              name: `測試商店 ${i}`
            }
          })
        )
      }

      const responses = await Promise.all(requests)
      
      // All requests should complete successfully
      responses.forEach(response => {
        expect(response.status()).toBe(200)
      })
    })

    test('should have reasonable response times', async ({ request }) => {
      if (!adminToken) {
        test.skip('Admin token not available')
      }

      const startTime = Date.now()
      
      const response = await request.get(`${baseURL}/api/settings/payment_transfer`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      })

      const endTime = Date.now()
      const responseTime = endTime - startTime

      expect(response.status()).toBe(200)
      expect(responseTime).toBeLessThan(1000) // Should respond within 1 second
    })
  })
})