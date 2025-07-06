const { test, expect } = require('@playwright/test');
const { faker } = require('@faker-js/faker');

// 測試設置
const BASE_URL = 'http://localhost:8001';
const ADMIN_USERNAME = 'admin';
const ADMIN_PASSWORD = 'admin123';

// 測試用戶資料
const testUser = {
  username: `testuser_${Date.now()}`,
  email: `test_${Date.now()}@example.com`,
  password: 'testpass123',
  fullName: faker.person.fullName(),
  phone: faker.phone.number(),
  address: faker.location.streetAddress()
};

// 測試商品資料
const testProduct = {
  name: `測試商品_${Date.now()}`,
  price: 999,
  description: '這是一個測試商品',
  stock: 10
};

// 測試優惠券資料
const testCoupon = {
  name: `測試優惠券_${Date.now()}`,
  code: `TEST${Date.now()}`,
  discount_type: 'percentage',
  discount_value: 10,
  min_order_amount: 500
};

test.describe('BlogCommerce 完整用戶流程測試', () => {
  
  // 測試前準備
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
  });
  
  test.describe('1. 用戶註冊和登入測試', () => {
    
    test('1.1 用戶註冊流程', async ({ page }) => {
      // 前往註冊頁面
      await page.click('text=註冊');
      await expect(page).toHaveURL(`${BASE_URL}/register`);
      
      // 填寫註冊表單
      await page.fill('input[name="username"]', testUser.username);
      await page.fill('input[name="email"]', testUser.email);
      await page.fill('input[name="password"]', testUser.password);
      await page.fill('input[name="confirm_password"]', testUser.password);
      await page.fill('input[name="full_name"]', testUser.fullName);
      
      // 提交註冊
      await page.click('button[type="submit"]');
      
      // 驗證註冊成功
      await expect(page).toHaveURL(`${BASE_URL}/`);
      await expect(page.locator('text=' + testUser.username)).toBeVisible();
    });
    
    test('1.2 用戶登入流程', async ({ page }) => {
      // 前往登入頁面
      await page.click('text=登入');
      await expect(page).toHaveURL(`${BASE_URL}/login`);
      
      // 填寫登入表單
      await page.fill('input[name="username"]', testUser.username);
      await page.fill('input[name="password"]', testUser.password);
      
      // 提交登入
      await page.click('button[type="submit"]');
      
      // 驗證登入成功
      await expect(page).toHaveURL(`${BASE_URL}/`);
      await expect(page.locator('text=' + testUser.username)).toBeVisible();
    });
    
    test('1.3 登入錯誤處理', async ({ page }) => {
      await page.goto(`${BASE_URL}/login`);
      
      // 使用錯誤的密碼
      await page.fill('input[name="username"]', testUser.username);
      await page.fill('input[name="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');
      
      // 驗證錯誤訊息
      await expect(page.locator('text=登入失敗')).toBeVisible();
    });
  });
  
  test.describe('2. 商品瀏覽和購物車測試', () => {
    
    test.beforeEach(async ({ page }) => {
      // 先登入
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', testUser.username);
      await page.fill('input[name="password"]', testUser.password);
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL(`${BASE_URL}/`);
    });
    
    test('2.1 商品瀏覽', async ({ page }) => {
      // 前往商品列表
      await page.click('text=商品');
      await expect(page).toHaveURL(`${BASE_URL}/products`);
      
      // 驗證商品列表載入
      await expect(page.locator('[data-testid="product-item"]')).toBeVisible();
      
      // 點擊商品進入詳情頁
      await page.click('[data-testid="product-item"]');
      await expect(page).toHaveURL(/\/products\/\d+/);
      
      // 驗證商品詳情頁面
      await expect(page.locator('[data-testid="product-name"]')).toBeVisible();
      await expect(page.locator('[data-testid="product-price"]')).toBeVisible();
      await expect(page.locator('[data-testid="add-to-cart"]')).toBeVisible();
    });
    
    test('2.2 添加商品到購物車', async ({ page }) => {
      await page.goto(`${BASE_URL}/products`);
      
      // 點擊第一個商品
      await page.click('[data-testid="product-item"]');
      
      // 設置數量
      await page.fill('input[name="quantity"]', '2');
      
      // 添加到購物車
      await page.click('[data-testid="add-to-cart"]');
      
      // 驗證添加成功訊息
      await expect(page.locator('text=商品已加入購物車')).toBeVisible();
      
      // 驗證購物車計數更新
      await expect(page.locator('[data-testid="cart-count"]')).toContainText('2');
    });
    
    test('2.3 購物車操作', async ({ page }) => {
      // 先添加商品到購物車
      await page.goto(`${BASE_URL}/products`);
      await page.click('[data-testid="product-item"]');
      await page.click('[data-testid="add-to-cart"]');
      
      // 前往購物車頁面
      await page.click('[data-testid="cart-link"]');
      await expect(page).toHaveURL(`${BASE_URL}/cart`);
      
      // 驗證購物車內容
      await expect(page.locator('[data-testid="cart-item"]')).toBeVisible();
      
      // 修改數量
      await page.click('[data-testid="increase-quantity"]');
      await expect(page.locator('[data-testid="item-quantity"]')).toContainText('2');
      
      // 移除商品
      await page.click('[data-testid="remove-item"]');
      await expect(page.locator('text=您的購物車是空的')).toBeVisible();
    });
  });
  
  test.describe('3. 結帳流程測試', () => {
    
    test.beforeEach(async ({ page }) => {
      // 登入並添加商品到購物車
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', testUser.username);
      await page.fill('input[name="password"]', testUser.password);
      await page.click('button[type="submit"]');
      
      await page.goto(`${BASE_URL}/products`);
      await page.click('[data-testid="product-item"]');
      await page.click('[data-testid="add-to-cart"]');
    });
    
    test('3.1 未登入用戶結帳重定向', async ({ page }) => {
      // 先登出
      await page.click('[data-testid="logout-button"]');
      
      // 前往購物車
      await page.goto(`${BASE_URL}/cart`);
      
      // 點擊結帳按鈕
      await page.click('text=前往結帳');
      
      // 驗證登入提示
      await expect(page.locator('text=您需要先登入才能進行結帳')).toBeVisible();
    });
    
    test('3.2 結帳資料填寫', async ({ page }) => {
      // 前往結帳頁面
      await page.goto(`${BASE_URL}/cart`);
      await page.click('text=前往結帳');
      await expect(page).toHaveURL(`${BASE_URL}/checkout`);
      
      // 驗證訂單明細顯示
      await expect(page.locator('[data-testid="order-items"]')).toBeVisible();
      
      // 填寫收件人資訊
      await page.fill('input[name="customer_name"]', testUser.fullName);
      await page.fill('input[name="customer_phone"]', testUser.phone);
      await page.fill('input[name="customer_email"]', testUser.email);
      await page.fill('textarea[name="shipping_address"]', testUser.address);
      
      // 選擇付款方式
      await page.click('input[value="transfer"]');
      
      // 驗證表單已填寫
      await expect(page.locator('input[name="customer_name"]')).toHaveValue(testUser.fullName);
      await expect(page.locator('input[name="customer_phone"]')).toHaveValue(testUser.phone);
    });
    
    test('3.3 完成訂單', async ({ page }) => {
      await page.goto(`${BASE_URL}/checkout`);
      
      // 填寫必要資訊
      await page.fill('input[name="customer_name"]', testUser.fullName);
      await page.fill('input[name="customer_phone"]', testUser.phone);
      await page.fill('input[name="customer_email"]', testUser.email);
      await page.fill('textarea[name="shipping_address"]', testUser.address);
      await page.click('input[value="transfer"]');
      
      // 提交訂單
      await page.click('button[type="submit"]');
      
      // 驗證訂單創建成功
      await expect(page.locator('text=轉帳資訊')).toBeVisible();
      await expect(page.locator('text=訂單編號')).toBeVisible();
    });
  });
  
  test.describe('4. 優惠券功能測試', () => {
    
    test.beforeEach(async ({ page }) => {
      // 管理員登入創建優惠券
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', ADMIN_USERNAME);
      await page.fill('input[name="password"]', ADMIN_PASSWORD);
      await page.click('button[type="submit"]');
      
      // 前往後台
      await page.goto(`${BASE_URL}/admin`);
    });
    
    test('4.1 創建優惠券', async ({ page }) => {
      // 進入優惠券管理頁面
      await page.click('text=優惠券管理');
      await expect(page).toHaveURL(`${BASE_URL}/admin/coupons`);
      
      // 點擊創建優惠券
      await page.click('text=創建優惠券');
      
      // 填寫優惠券資訊
      await page.fill('input[name="name"]', testCoupon.name);
      await page.fill('input[name="code"]', testCoupon.code);
      await page.selectOption('select[name="discount_type"]', testCoupon.discount_type);
      await page.fill('input[name="discount_value"]', testCoupon.discount_value.toString());
      await page.fill('input[name="min_order_amount"]', testCoupon.min_order_amount.toString());
      
      // 設置有效期
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 30);
      await page.fill('input[name="expires_at"]', futureDate.toISOString().split('T')[0]);
      
      // 提交創建
      await page.click('button[type="submit"]');
      
      // 驗證創建成功
      await expect(page.locator('text=優惠券創建成功')).toBeVisible();
      await expect(page.locator('text=' + testCoupon.name)).toBeVisible();
    });
    
    test('4.2 分發優惠券', async ({ page }) => {
      // 進入優惠券管理頁面
      await page.goto(`${BASE_URL}/admin/coupons`);
      
      // 選擇優惠券並分發
      await page.click(`text=${testCoupon.name}`);
      await page.click('text=分發優惠券');
      
      // 選擇分發對象
      await page.click('text=分發給所有用戶');
      
      // 確認分發
      await page.click('text=確認分發');
      
      // 驗證分發成功
      await expect(page.locator('text=優惠券分發成功')).toBeVisible();
    });
    
    test('4.3 前台使用優惠券', async ({ page }) => {
      // 切換到一般用戶
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', testUser.username);
      await page.fill('input[name="password"]', testUser.password);
      await page.click('button[type="submit"]');
      
      // 添加商品到購物車
      await page.goto(`${BASE_URL}/products`);
      await page.click('[data-testid="product-item"]');
      await page.click('[data-testid="add-to-cart"]');
      
      // 前往結帳頁面
      await page.goto(`${BASE_URL}/checkout`);
      
      // 輸入優惠碼
      await page.fill('input[id="coupon-code"]', testCoupon.code);
      await page.click('button[id="apply-coupon-btn"]');
      
      // 驗證優惠碼套用成功
      await expect(page.locator('text=優惠碼已套用')).toBeVisible();
      await expect(page.locator('[id="coupon-discount"]')).toBeVisible();
      
      // 驗證折扣金額計算
      const discountAmount = await page.locator('[id="discount-amount"]').textContent();
      expect(discountAmount).toContain('-NT$');
    });
    
    test('4.4 無效優惠券處理', async ({ page }) => {
      // 切換到一般用戶
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', testUser.username);
      await page.fill('input[name="password"]', testUser.password);
      await page.click('button[type="submit"]');
      
      // 添加商品到購物車
      await page.goto(`${BASE_URL}/products`);
      await page.click('[data-testid="product-item"]');
      await page.click('[data-testid="add-to-cart"]');
      
      // 前往結帳頁面
      await page.goto(`${BASE_URL}/checkout`);
      
      // 輸入無效優惠碼
      await page.fill('input[id="coupon-code"]', 'INVALID_CODE');
      await page.click('button[id="apply-coupon-btn"]');
      
      // 驗證錯誤訊息
      await expect(page.locator('text=優惠碼無效')).toBeVisible();
    });
  });
  
  test.describe('5. 訂單管理測試', () => {
    
    test('5.1 查看訂單列表', async ({ page }) => {
      // 用戶登入
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', testUser.username);
      await page.fill('input[name="password"]', testUser.password);
      await page.click('button[type="submit"]');
      
      // 前往訂單頁面
      await page.goto(`${BASE_URL}/orders`);
      
      // 驗證訂單列表
      await expect(page.locator('[data-testid="order-list"]')).toBeVisible();
    });
    
    test('5.2 查看訂單詳情', async ({ page }) => {
      // 用戶登入
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', testUser.username);
      await page.fill('input[name="password"]', testUser.password);
      await page.click('button[type="submit"]');
      
      // 前往訂單頁面
      await page.goto(`${BASE_URL}/orders`);
      
      // 點擊訂單查看詳情
      await page.click('[data-testid="order-detail-link"]');
      
      // 驗證訂單詳情頁面
      await expect(page.locator('[data-testid="order-details"]')).toBeVisible();
      await expect(page.locator('text=訂單編號')).toBeVisible();
    });
  });
  
  test.describe('6. 後台管理測試', () => {
    
    test.beforeEach(async ({ page }) => {
      // 管理員登入
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', ADMIN_USERNAME);
      await page.fill('input[name="password"]', ADMIN_PASSWORD);
      await page.click('button[type="submit"]');
      
      // 前往後台
      await page.goto(`${BASE_URL}/admin`);
    });
    
    test('6.1 管理員權限驗證', async ({ page }) => {
      // 驗證管理員可以訪問後台
      await expect(page).toHaveURL(`${BASE_URL}/admin`);
      await expect(page.locator('text=管理面板')).toBeVisible();
    });
    
    test('6.2 一般用戶權限限制', async ({ page }) => {
      // 切換到一般用戶
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', testUser.username);
      await page.fill('input[name="password"]', testUser.password);
      await page.click('button[type="submit"]');
      
      // 嘗試訪問後台
      await page.goto(`${BASE_URL}/admin`);
      
      // 驗證權限不足訊息
      await expect(page.locator('text=權限不足')).toBeVisible();
    });
    
    test('6.3 訂單管理', async ({ page }) => {
      // 進入訂單管理
      await page.click('text=訂單管理');
      await expect(page).toHaveURL(`${BASE_URL}/admin/orders`);
      
      // 驗證訂單列表
      await expect(page.locator('[data-testid="admin-order-list"]')).toBeVisible();
      
      // 點擊訂單詳情
      await page.click('[data-testid="admin-order-detail"]');
      
      // 驗證可以更新訂單狀態
      await expect(page.locator('select[name="status"]')).toBeVisible();
    });
  });
  
  test.describe('7. 系統整合測試', () => {
    
    test('7.1 完整購物流程', async ({ page }) => {
      // 1. 用戶註冊
      await page.goto(`${BASE_URL}/register`);
      const newUser = {
        username: `flow_test_${Date.now()}`,
        email: `flow_test_${Date.now()}@example.com`,
        password: 'testpass123',
        fullName: faker.person.fullName()
      };
      
      await page.fill('input[name="username"]', newUser.username);
      await page.fill('input[name="email"]', newUser.email);
      await page.fill('input[name="password"]', newUser.password);
      await page.fill('input[name="confirm_password"]', newUser.password);
      await page.fill('input[name="full_name"]', newUser.fullName);
      await page.click('button[type="submit"]');
      
      // 2. 瀏覽商品
      await page.goto(`${BASE_URL}/products`);
      await page.click('[data-testid="product-item"]');
      
      // 3. 添加到購物車
      await page.click('[data-testid="add-to-cart"]');
      
      // 4. 結帳
      await page.goto(`${BASE_URL}/cart`);
      await page.click('text=前往結帳');
      
      // 5. 填寫結帳資訊
      await page.fill('input[name="customer_name"]', newUser.fullName);
      await page.fill('input[name="customer_phone"]', faker.phone.number());
      await page.fill('input[name="customer_email"]', newUser.email);
      await page.fill('textarea[name="shipping_address"]', faker.location.streetAddress());
      await page.click('input[value="transfer"]');
      
      // 6. 完成訂單
      await page.click('button[type="submit"]');
      
      // 7. 驗證訂單完成
      await expect(page.locator('text=轉帳資訊')).toBeVisible();
    });
    
    test('7.2 優惠券完整流程', async ({ page }) => {
      // 1. 管理員創建優惠券
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', ADMIN_USERNAME);
      await page.fill('input[name="password"]', ADMIN_PASSWORD);
      await page.click('button[type="submit"]');
      
      await page.goto(`${BASE_URL}/admin/coupons`);
      await page.click('text=創建優惠券');
      
      const flowCoupon = {
        name: `流程測試優惠券_${Date.now()}`,
        code: `FLOW${Date.now()}`,
        discount_value: 15
      };
      
      await page.fill('input[name="name"]', flowCoupon.name);
      await page.fill('input[name="code"]', flowCoupon.code);
      await page.selectOption('select[name="discount_type"]', 'percentage');
      await page.fill('input[name="discount_value"]', flowCoupon.discount_value.toString());
      await page.click('button[type="submit"]');
      
      // 2. 分發優惠券
      await page.click('text=分發優惠券');
      await page.click('text=分發給所有用戶');
      await page.click('text=確認分發');
      
      // 3. 用戶使用優惠券
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', testUser.username);
      await page.fill('input[name="password"]', testUser.password);
      await page.click('button[type="submit"]');
      
      await page.goto(`${BASE_URL}/products`);
      await page.click('[data-testid="product-item"]');
      await page.click('[data-testid="add-to-cart"]');
      
      await page.goto(`${BASE_URL}/checkout`);
      await page.fill('input[id="coupon-code"]', flowCoupon.code);
      await page.click('button[id="apply-coupon-btn"]');
      
      await expect(page.locator('text=優惠碼已套用')).toBeVisible();
      
      // 4. 完成訂單
      await page.fill('input[name="customer_name"]', testUser.fullName);
      await page.fill('input[name="customer_phone"]', testUser.phone);
      await page.fill('input[name="customer_email"]', testUser.email);
      await page.fill('textarea[name="shipping_address"]', testUser.address);
      await page.click('input[value="transfer"]');
      await page.click('button[type="submit"]');
      
      await expect(page.locator('text=轉帳資訊')).toBeVisible();
    });
  });
});

// 測試結果報告
test.afterAll(async () => {
  console.log('完整端到端測試完成');
  console.log('測試用戶:', testUser.username);
  console.log('測試優惠券:', testCoupon.code);
}); 