import { test, expect } from '@playwright/test';

test.describe('優惠券管理流程', () => {
  let adminLoginData = {
    username: 'admin',
    password: 'admin123'
  };

  let testCouponData = {
    name: '測試優惠券',
    description: '這是一個端到端測試用的優惠券',
    coupon_type: 'order_discount',
    discount_type: 'percentage',
    discount_value: 15.0,
    minimum_amount: 100.0,
    valid_from: new Date().toISOString(),
    valid_to: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
    is_active: true
  };

  test.beforeEach(async ({ page }) => {
    // 啟動開發服務器
    await page.goto('http://localhost:8002');
    
    // 管理員登入
    await page.click('text=登入');
    await page.fill('input[name="username"]', adminLoginData.username);
    await page.fill('input[name="password"]', adminLoginData.password);
    await page.click('button[type="submit"]');
    
    // 等待登入完成
    await page.waitForSelector('text=管理後台');
  });

  test('管理員創建優惠券流程', async ({ page }) => {
    // 導航到優惠券管理頁面
    await page.click('text=優惠券管理');
    await page.waitForSelector('h1:has-text("優惠券管理")');

    // 檢查頁面基本元素
    await expect(page.locator('h1')).toContainText('優惠券管理');
    await expect(page.locator('button:has-text("建立優惠券")')).toBeVisible();

    // 點擊建立優惠券按鈕
    await page.click('button:has-text("建立優惠券")');
    
    // 等待模態框出現
    await page.waitForSelector('.ant-modal');
    await expect(page.locator('.ant-modal-title')).toContainText('建立優惠券');

    // 填寫優惠券表單
    await page.fill('input[placeholder="請輸入優惠券名稱"]', testCouponData.name);
    await page.fill('textarea[placeholder="請輸入優惠券描述"]', testCouponData.description);
    
    // 選擇優惠券類型
    await page.click('.ant-select-selector:has-text("選擇優惠券類型")');
    await page.click('text=整筆消費折扣');
    
    // 選擇折扣類型
    await page.click('.ant-select-selector:has-text("選擇折扣類型")');
    await page.click('text=百分比折扣');
    
    // 填寫折扣值
    await page.fill('input[placeholder="請輸入折扣值"]', testCouponData.discount_value.toString());
    
    // 填寫最低消費金額
    await page.fill('input[placeholder="請輸入最低消費金額"]', testCouponData.minimum_amount.toString());

    // 設定有效期（簡化版，實際可能需要使用日期選擇器）
    // 這裡假設已經有預設的有效期設定

    // 提交表單
    await page.click('button:has-text("確定")');
    
    // 等待創建成功的通知
    await page.waitForSelector('.ant-notification-notice-success');
    await expect(page.locator('.ant-notification-notice-message')).toContainText('創建成功');

    // 驗證優惠券出現在列表中
    await page.waitForSelector('table');
    await expect(page.locator('table tbody tr')).toContainText(testCouponData.name);
  });

  test('管理員批次創建優惠券流程', async ({ page }) => {
    // 導航到優惠券管理頁面
    await page.click('text=優惠券管理');
    await page.waitForSelector('h1:has-text("優惠券管理")');

    // 點擊批次建立按鈕
    await page.click('button:has-text("批次建立")');
    
    // 等待批次建立模態框出現
    await page.waitForSelector('.ant-modal');
    await expect(page.locator('.ant-modal-title')).toContainText('批次建立優惠券');

    // 填寫基礎優惠券資訊
    await page.fill('input[placeholder="請輸入優惠券名稱"]', '批次優惠券');
    await page.fill('textarea[placeholder="請輸入優惠券描述"]', '批次創建的測試優惠券');
    
    // 設定優惠券類型和折扣
    await page.click('.ant-select-selector:has-text("選擇優惠券類型")');
    await page.click('text=整筆消費折扣');
    
    await page.click('.ant-select-selector:has-text("選擇折扣類型")');
    await page.click('text=固定金額');
    
    await page.fill('input[placeholder="請輸入折扣值"]', '20');

    // 設定批次參數
    await page.fill('input[placeholder="請輸入建立數量"]', '5');
    await page.fill('input[placeholder="請輸入代碼前綴"]', 'BATCH');

    // 提交批次建立
    await page.click('button:has-text("確定")');
    
    // 等待創建成功
    await page.waitForSelector('.ant-notification-notice-success');
    await expect(page.locator('.ant-notification-notice-message')).toContainText('批次創建成功');

    // 驗證批次創建的優惠券
    await page.waitForSelector('table');
    const batchCoupons = page.locator('table tbody tr:has-text("BATCH-")');
    await expect(batchCoupons).toHaveCount(5);
  });

  test('管理員分發優惠券流程', async ({ page }) => {
    // 先創建一個優惠券
    await page.click('text=優惠券管理');
    await page.waitForSelector('h1:has-text("優惠券管理")');

    // 假設已經有優惠券存在，點擊分發按鈕
    await page.click('table tbody tr:first-child button:has-text("分發")');
    
    // 等待分發模態框出現
    await page.waitForSelector('.ant-modal');
    await expect(page.locator('.ant-modal-title')).toContainText('分發優惠券');

    // 選擇用戶（假設有用戶選擇器）
    await page.click('.ant-select-selector:has-text("選擇用戶")');
    await page.click('.ant-select-item:first-child');

    // 填寫分發備註
    await page.fill('textarea[placeholder="請輸入分發備註"]', '測試分發優惠券');

    // 確認分發
    await page.click('button:has-text("確定")');
    
    // 等待分發成功
    await page.waitForSelector('.ant-notification-notice-success');
    await expect(page.locator('.ant-notification-notice-message')).toContainText('分發成功');
  });

  test('管理員查看優惠券統計', async ({ page }) => {
    // 導航到優惠券管理頁面
    await page.click('text=優惠券管理');
    await page.waitForSelector('h1:has-text("優惠券管理")');

    // 檢查統計卡片
    await expect(page.locator('.ant-statistic-title:has-text("總優惠券數")')).toBeVisible();
    await expect(page.locator('.ant-statistic-title:has-text("有效優惠券")')).toBeVisible();
    await expect(page.locator('.ant-statistic-title:has-text("已使用")')).toBeVisible();
    await expect(page.locator('.ant-statistic-title:has-text("總折扣金額")')).toBeVisible();

    // 點擊統計資料按鈕
    await page.click('button:has-text("統計資料")');
    
    // 等待統計模態框出現
    await page.waitForSelector('.ant-modal');
    await expect(page.locator('.ant-modal-title')).toContainText('優惠券統計');

    // 檢查統計圖表或數據
    await expect(page.locator('.ant-modal-body')).toContainText('統計');
  });

  test('管理員篩選和搜尋優惠券', async ({ page }) => {
    // 導航到優惠券管理頁面
    await page.click('text=優惠券管理');
    await page.waitForSelector('h1:has-text("優惠券管理")');

    // 使用搜尋功能
    await page.fill('input[placeholder="搜尋優惠券代碼或名稱"]', '測試');
    await page.click('button[aria-label="search"]');
    
    // 等待搜尋結果
    await page.waitForTimeout(1000);

    // 使用類型篩選
    await page.click('.ant-select-selector:has-text("類型篩選")');
    await page.click('text=整筆折扣');
    
    // 等待篩選結果
    await page.waitForTimeout(1000);

    // 使用狀態篩選
    await page.click('.ant-select-selector:has-text("狀態篩選")');
    await page.click('text=啟用');
    
    // 等待篩選結果
    await page.waitForTimeout(1000);

    // 重置篩選
    await page.click('button:has-text("重置篩選")');
    
    // 等待重置完成
    await page.waitForTimeout(1000);
  });

  test('管理員編輯優惠券', async ({ page }) => {
    // 導航到優惠券管理頁面
    await page.click('text=優惠券管理');
    await page.waitForSelector('h1:has-text("優惠券管理")');

    // 點擊第一個優惠券的編輯按鈕
    await page.click('table tbody tr:first-child button:has-text("編輯")');
    
    // 等待編輯模態框出現
    await page.waitForSelector('.ant-modal');
    await expect(page.locator('.ant-modal-title')).toContainText('編輯優惠券');

    // 修改優惠券名稱
    await page.fill('input[placeholder="請輸入優惠券名稱"]', '已編輯的優惠券');
    
    // 修改折扣值
    await page.fill('input[placeholder="請輸入折扣值"]', '25');

    // 保存修改
    await page.click('button:has-text("確定")');
    
    // 等待更新成功
    await page.waitForSelector('.ant-notification-notice-success');
    await expect(page.locator('.ant-notification-notice-message')).toContainText('更新成功');

    // 驗證修改後的資料
    await expect(page.locator('table tbody')).toContainText('已編輯的優惠券');
  });

  test('管理員查看優惠券使用記錄', async ({ page }) => {
    // 導航到優惠券管理頁面
    await page.click('text=優惠券管理');
    await page.waitForSelector('h1:has-text("優惠券管理")');

    // 查找有使用記錄的優惠券並點擊查看記錄
    const usageButton = page.locator('button:has-text("查看記錄")').first();
    if (await usageButton.isVisible()) {
      await usageButton.click();
      
      // 等待使用記錄模態框出現
      await page.waitForSelector('.ant-modal');
      await expect(page.locator('.ant-modal-title')).toContainText('使用記錄');

      // 檢查使用記錄表格
      await expect(page.locator('.ant-modal-body table')).toBeVisible();
    }
  });

  test('用戶查看可用優惠券', async ({ page }) => {
    // 登出管理員
    await page.click('text=登出');
    
    // 以普通用戶身份登入
    await page.click('text=登入');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testuser123');
    await page.click('button[type="submit"]');
    
    // 等待登入完成
    await page.waitForSelector('text=用戶中心');

    // 導航到我的優惠券頁面
    await page.click('text=我的優惠券');
    await page.waitForSelector('h1:has-text("我的優惠券")');

    // 檢查優惠券列表
    await expect(page.locator('.coupon-list')).toBeVisible();
    
    // 如果有優惠券，檢查優惠券卡片
    const couponCards = page.locator('.coupon-card');
    if (await couponCards.count() > 0) {
      await expect(couponCards.first()).toBeVisible();
      await expect(couponCards.first()).toContainText('優惠券');
    }
  });

  test('優惠券驗證流程', async ({ page }) => {
    // 模擬在購物車頁面使用優惠券
    await page.goto('http://localhost:8002/cart');
    
    // 假設購物車中有商品
    // 查找優惠券輸入框
    const couponInput = page.locator('input[placeholder*="優惠券"]');
    if (await couponInput.isVisible()) {
      // 輸入優惠券代碼
      await couponInput.fill('TEST123');
      
      // 點擊驗證按鈕
      await page.click('button:has-text("使用優惠券")');
      
      // 等待驗證結果
      await page.waitForTimeout(2000);
      
      // 檢查驗證結果（成功或失敗）
      const successMessage = page.locator('.ant-message-success');
      const errorMessage = page.locator('.ant-message-error');
      
      // 驗證有響應（成功或失敗都算是正常的測試結果）
      const hasResponse = await successMessage.isVisible() || await errorMessage.isVisible();
      expect(hasResponse).toBeTruthy();
    }
  });

  test('優惠券過期處理', async ({ page }) => {
    // 導航到優惠券管理頁面
    await page.click('text=優惠券管理');
    await page.waitForSelector('h1:has-text("優惠券管理")');

    // 篩選過期優惠券
    await page.click('.ant-select-selector:has-text("過期狀態")');
    await page.click('text=已過期');
    
    // 等待篩選結果
    await page.waitForTimeout(1000);

    // 檢查是否有過期優惠券顯示
    const expiredCoupons = page.locator('table tbody tr');
    if (await expiredCoupons.count() > 0) {
      // 驗證過期優惠券的狀態顯示
      await expect(page.locator('table tbody')).toContainText('已過期');
    }
  });

  test('響應式設計測試', async ({ page }) => {
    // 導航到優惠券管理頁面
    await page.click('text=優惠券管理');
    await page.waitForSelector('h1:has-text("優惠券管理")');

    // 測試手機尺寸
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    
    // 檢查手機版本的元素是否正確顯示
    await expect(page.locator('h1')).toBeVisible();
    
    // 測試平板尺寸
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    
    // 檢查平板版本的元素是否正確顯示
    await expect(page.locator('h1')).toBeVisible();
    
    // 恢復桌面尺寸
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(1000);
  });

  test('優惠券功能性能測試', async ({ page }) => {
    // 導航到優惠券管理頁面
    await page.click('text=優惠券管理');
    
    // 測量頁面載入時間
    const startTime = Date.now();
    await page.waitForSelector('h1:has-text("優惠券管理")');
    const loadTime = Date.now() - startTime;
    
    // 驗證頁面載入時間合理（5秒內）
    expect(loadTime).toBeLessThan(5000);

    // 測試表格渲染性能
    await page.waitForSelector('table');
    const tableRows = page.locator('table tbody tr');
    
    // 如果有優惠券，測試排序性能
    if (await tableRows.count() > 0) {
      const sortStart = Date.now();
      await page.click('table th:has-text("創建時間")');
      await page.waitForTimeout(500);
      const sortTime = Date.now() - sortStart;
      
      // 驗證排序時間合理（2秒內）
      expect(sortTime).toBeLessThan(2000);
    }
  });
}); 