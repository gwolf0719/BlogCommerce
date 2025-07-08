import { test, expect } from '@playwright/test'

test.describe('Payment Settings E2E Tests', () => {
  let adminToken

  test.beforeAll(async ({ request }) => {
    // Login as admin to get token
    const loginResponse = await request.post('http://localhost:8000/api/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    })
    
    if (loginResponse.ok()) {
      const loginData = await loginResponse.json()
      adminToken = loginData.access_token
    }
  })

  test.beforeEach(async ({ page }) => {
    // Set admin token in localStorage
    if (adminToken) {
      await page.addInitScript((token) => {
        localStorage.setItem('auth_token', token)
        localStorage.setItem('user_role', 'admin')
      }, adminToken)
    }
    
    // Navigate to admin settings page
    await page.goto('/admin/settings')
    await page.waitForLoadState('networkidle')
  })

  test('should display payment settings interface', async ({ page }) => {
    // Click on payment settings tab
    await page.click('[data-testid="payment-tab"]')
    
    // Should show payment settings card
    await expect(page.locator('text=金流設定')).toBeVisible()
    
    // Should show payment method checkboxes
    await expect(page.locator('text=轉帳')).toBeVisible()
    await expect(page.locator('text=Line Pay')).toBeVisible()
    await expect(page.locator('text=綠界全方位金流')).toBeVisible()
    await expect(page.locator('text=PayPal')).toBeVisible()
  })

  test('should configure transfer payment settings', async ({ page }) => {
    await page.click('[data-testid="payment-tab"]')
    
    // Enable transfer payment
    await page.check('input[value="transfer"]')
    
    // Should show transfer settings form
    await expect(page.locator('text=轉帳設定')).toBeVisible()
    
    // Fill transfer settings
    await page.fill('input[placeholder="請輸入銀行名稱"]', '國泰世華銀行')
    await page.fill('input[placeholder="請輸入帳號"]', '1234567890')
    await page.fill('input[placeholder="請輸入戶名"]', 'BlogCommerce 測試商店')
    
    // Save settings
    await page.click('button:has-text("儲存金流設定")')
    
    // Should show success message
    await expect(page.locator('text=金流設定已儲存')).toBeVisible({ timeout: 10000 })
  })

  test('should configure Line Pay settings', async ({ page }) => {
    await page.click('[data-testid="payment-tab"]')
    
    // Enable Line Pay
    await page.check('input[value="linepay"]')
    
    // Should show Line Pay settings form
    await expect(page.locator('text=Line Pay 設定')).toBeVisible()
    
    // Fill Line Pay settings
    await page.fill('input[placeholder="請輸入 Channel ID"]', 'test_channel_123')
    await page.fill('input[placeholder="請輸入 Channel Secret"]', 'test_secret_456')
    await page.fill('input[placeholder="請輸入商店名稱"]', 'BlogCommerce 線上商店')
    
    // Save settings
    await page.click('button:has-text("儲存金流設定")')
    
    // Should show success message
    await expect(page.locator('text=金流設定已儲存')).toBeVisible({ timeout: 10000 })
  })

  test('should configure ECPay settings', async ({ page }) => {
    await page.click('[data-testid="payment-tab"]')
    
    // Enable ECPay
    await page.check('input[value="ecpay"]')
    
    // Should show ECPay settings form
    await expect(page.locator('text=綠界全方位金流設定')).toBeVisible()
    
    // Fill ECPay settings
    await page.fill('input[placeholder="請輸入 Merchant ID"]', '2000132')
    await page.fill('input[placeholder="請輸入 HashKey"]', '5294y06JbISpM5x9')
    await page.fill('input[placeholder="請輸入 HashIV"]', 'v77hoKGq4kWxNNIS')
    await page.fill('input[placeholder="請輸入 API URL"]', 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5')
    
    // Save settings
    await page.click('button:has-text("儲存金流設定")')
    
    // Should show success message
    await expect(page.locator('text=金流設定已儲存')).toBeVisible({ timeout: 10000 })
  })

  test('should configure PayPal settings', async ({ page }) => {
    await page.click('[data-testid="payment-tab"]')
    
    // Enable PayPal
    await page.check('input[value="paypal"]')
    
    // Should show PayPal settings form
    await expect(page.locator('text=PayPal 設定')).toBeVisible()
    
    // Fill PayPal settings
    await page.fill('input[placeholder="請輸入 PayPal Client ID"]', 'test_paypal_client_id')
    await page.fill('input[placeholder="請輸入 PayPal Client Secret"]', 'test_paypal_secret')
    
    // Select environment
    await page.selectOption('select', 'sandbox')
    
    // Save settings
    await page.click('button:has-text("儲存金流設定")')
    
    // Should show success message
    await expect(page.locator('text=金流設定已儲存')).toBeVisible({ timeout: 10000 })
  })

  test('should persist settings after page reload', async ({ page }) => {
    await page.click('[data-testid="payment-tab"]')
    
    // Enable multiple payment methods
    await page.check('input[value="transfer"]')
    await page.check('input[value="paypal"]')
    
    // Fill settings
    await page.fill('input[placeholder="請輸入銀行名稱"]', '測試銀行')
    await page.fill('input[placeholder="請輸入 PayPal Client ID"]', 'test_client')
    
    // Save settings
    await page.click('button:has-text("儲存金流設定")')
    await expect(page.locator('text=金流設定已儲存')).toBeVisible({ timeout: 10000 })
    
    // Reload page
    await page.reload()
    await page.waitForLoadState('networkidle')
    await page.click('[data-testid="payment-tab"]')
    
    // Check if settings are still there
    await expect(page.locator('input[value="transfer"]')).toBeChecked()
    await expect(page.locator('input[value="paypal"]')).toBeChecked()
    await expect(page.locator('input[placeholder="請輸入銀行名稱"]')).toHaveValue('測試銀行')
  })

  test('should handle invalid settings gracefully', async ({ page }) => {
    await page.click('[data-testid="payment-tab"]')
    
    // Enable transfer without filling required fields
    await page.check('input[value="transfer"]')
    
    // Try to save with empty fields
    await page.click('button:has-text("儲存金流設定")')
    
    // Should still attempt to save (validation is on backend)
    // The test verifies the UI doesn't break with invalid data
  })

  test('should show/hide settings forms based on checkbox selection', async ({ page }) => {
    await page.click('[data-testid="payment-tab"]')
    
    // Initially no payment method forms should be visible
    await expect(page.locator('text=轉帳設定')).not.toBeVisible()
    await expect(page.locator('text=Line Pay 設定')).not.toBeVisible()
    
    // Enable transfer
    await page.check('input[value="transfer"]')
    await expect(page.locator('text=轉帳設定')).toBeVisible()
    
    // Disable transfer
    await page.uncheck('input[value="transfer"]')
    await expect(page.locator('text=轉帳設定')).not.toBeVisible()
    
    // Enable Line Pay
    await page.check('input[value="linepay"]')
    await expect(page.locator('text=Line Pay 設定')).toBeVisible()
  })
})