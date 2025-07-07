import { test, expect } from '@playwright/test'

test.describe('Payment Flow E2E Tests', () => {
  let adminToken
  let userToken

  test.beforeAll(async ({ request }) => {
    // Create test user and admin
    try {
      // Try to login as admin
      const adminLogin = await request.post('http://localhost:8000/api/auth/login', {
        data: {
          username: 'admin',
          password: 'admin123'
        }
      })
      
      if (adminLogin.ok()) {
        const adminData = await adminLogin.json()
        adminToken = adminData.access_token
      }

      // Create or login test user
      const userLogin = await request.post('http://localhost:8000/api/auth/login', {
        data: {
          username: 'testuser',
          password: 'test123'
        }
      })

      if (userLogin.ok()) {
        const userData = await userLogin.json()
        userToken = userData.access_token
      }
    } catch (error) {
      console.log('Login setup failed, continuing with tests')
    }
  })

  test('should complete transfer payment flow', async ({ page, request }) => {
    // Setup payment settings first
    if (adminToken) {
      await request.put('http://localhost:8000/api/settings/payment_transfer', {
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
    }

    // Navigate to products page
    await page.goto('/products')
    await page.waitForLoadState('networkidle')

    // Add product to cart (assuming there's at least one product)
    const productCard = page.locator('.product-card').first()
    if (await productCard.count() > 0) {
      await productCard.click()
      await page.waitForLoadState('networkidle')
      
      // Add to cart
      await page.click('button:has-text("加入購物車")')
      await expect(page.locator('text=已加入購物車')).toBeVisible({ timeout: 5000 })
    }

    // Go to cart
    await page.goto('/cart')
    await page.waitForLoadState('networkidle')

    // Proceed to checkout
    await page.click('button:has-text("結帳")')
    await page.waitForLoadState('networkidle')

    // Fill checkout form
    await page.fill('input[name="customer_name"]', '測試客戶')
    await page.fill('input[name="customer_email"]', 'test@example.com')
    await page.fill('input[name="customer_phone"]', '0912345678')
    await page.fill('textarea[name="shipping_address"]', '台北市信義區信義路五段7號')

    // Select transfer payment
    await page.check('input[value="transfer"]')

    // Submit order
    await page.click('button:has-text("送出訂單")')

    // Should show payment information
    await expect(page.locator('text=轉帳資訊')).toBeVisible({ timeout: 10000 })
    await expect(page.locator('text=測試銀行')).toBeVisible()
    await expect(page.locator('text=1234567890')).toBeVisible()
  })

  test('should handle payment status checking', async ({ page, request }) => {
    // Create a test order via API
    let orderId
    if (adminToken) {
      const orderResponse = await request.post('http://localhost:8000/api/payment/create', {
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          order_id: 'TEST_E2E_001',
          payment_method: 'transfer'
        }
      })

      if (orderResponse.ok()) {
        const orderData = await orderResponse.json()
        orderId = orderData.data?.order_id || 'TEST_E2E_001'
      }
    }

    if (orderId) {
      // Navigate to order status page
      await page.goto(`/order-status/${orderId}`)
      await page.waitForLoadState('networkidle')

      // Should show order details
      await expect(page.locator(`text=${orderId}`)).toBeVisible()
      await expect(page.locator('text=待付款')).toBeVisible()
    }
  })

  test('should handle admin manual payment confirmation', async ({ page, request }) => {
    // Create a test order first
    let orderId = 'TEST_MANUAL_001'
    
    if (adminToken) {
      await request.post('http://localhost:8000/api/payment/create', {
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          order_id: orderId,
          payment_method: 'transfer'
        }
      })
    }

    // Login as admin
    if (adminToken) {
      await page.addInitScript((token) => {
        localStorage.setItem('auth_token', token)
        localStorage.setItem('user_role', 'admin')
      }, adminToken)
    }

    // Navigate to admin orders page
    await page.goto('/admin/orders')
    await page.waitForLoadState('networkidle')

    // Find the test order
    const orderRow = page.locator(`tr:has-text("${orderId}")`)
    if (await orderRow.count() > 0) {
      await orderRow.click()
      
      // Should show order details
      await expect(page.locator(`text=${orderId}`)).toBeVisible()
      
      // Confirm payment manually
      await page.click('button:has-text("確認付款")')
      
      // Fill confirmation form
      await page.fill('textarea[name="notes"]', '手動確認轉帳付款')
      await page.click('button:has-text("確認")')
      
      // Should show success message
      await expect(page.locator('text=付款已確認')).toBeVisible({ timeout: 10000 })
    }
  })

  test('should test different payment methods', async ({ page }) => {
    const paymentMethods = [
      { value: 'transfer', name: '轉帳' },
      { value: 'linepay', name: 'Line Pay' },
      { value: 'ecpay', name: '綠界' },
      { value: 'paypal', name: 'PayPal' }
    ]

    for (const method of paymentMethods) {
      // Navigate to checkout page
      await page.goto('/checkout')
      await page.waitForLoadState('networkidle')

      // Fill basic info
      await page.fill('input[name="customer_name"]', '測試客戶')
      await page.fill('input[name="customer_email"]', 'test@example.com')
      await page.fill('textarea[name="shipping_address"]', '測試地址')

      // Select payment method
      const paymentRadio = page.locator(`input[value="${method.value}"]`)
      if (await paymentRadio.count() > 0) {
        await paymentRadio.check()
        
        // Should show payment method selected
        await expect(page.locator(`text=${method.name}`)).toBeVisible()
      }
    }
  })

  test('should handle payment errors gracefully', async ({ page, request }) => {
    // Try to create payment with invalid data
    await page.goto('/checkout')
    await page.waitForLoadState('networkidle')

    // Submit without required fields
    await page.click('button:has-text("送出訂單")')

    // Should show validation errors
    await expect(page.locator('text=請填寫')).toBeVisible({ timeout: 5000 })
  })

  test('should handle payment timeouts', async ({ page }) => {
    // Simulate slow network by intercepting requests
    await page.route('**/api/payment/**', async route => {
      // Delay the response
      await new Promise(resolve => setTimeout(resolve, 2000))
      await route.continue()
    })

    await page.goto('/checkout')
    await page.waitForLoadState('networkidle')

    // Fill form
    await page.fill('input[name="customer_name"]', '測試客戶')
    await page.fill('input[name="customer_email"]', 'test@example.com')
    await page.fill('textarea[name="shipping_address"]', '測試地址')
    await page.check('input[value="transfer"]')

    // Submit order
    await page.click('button:has-text("送出訂單")')

    // Should show loading state
    await expect(page.locator('.loading')).toBeVisible({ timeout: 1000 })
  })

  test('should validate payment forms', async ({ page }) => {
    await page.goto('/checkout')
    await page.waitForLoadState('networkidle')

    // Test email validation
    await page.fill('input[name="customer_email"]', 'invalid-email')
    await page.blur('input[name="customer_email"]')
    await expect(page.locator('text=請輸入有效的電子郵件')).toBeVisible({ timeout: 3000 })

    // Test phone validation
    await page.fill('input[name="customer_phone"]', '123')
    await page.blur('input[name="customer_phone"]')
    await expect(page.locator('text=請輸入有效的電話號碼')).toBeVisible({ timeout: 3000 })

    // Test required fields
    await page.fill('input[name="customer_name"]', '')
    await page.blur('input[name="customer_name"]')
    await expect(page.locator('text=此欄位為必填')).toBeVisible({ timeout: 3000 })
  })

  test('should support mobile responsive design', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })

    await page.goto('/checkout')
    await page.waitForLoadState('networkidle')

    // Should be responsive
    const form = page.locator('form')
    await expect(form).toBeVisible()

    // Test mobile-specific interactions
    await page.fill('input[name="customer_name"]', '手機測試客戶')
    
    // Should handle touch events
    await page.tap('input[value="transfer"]')
    await expect(page.locator('input[value="transfer"]')).toBeChecked()
  })
})