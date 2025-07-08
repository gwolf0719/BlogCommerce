# BlogCommerce 後台頁面結構標準化測試計畫

## 測試目標
驗證所有後台頁面都遵循統一的admin-page結構標準，確保DOM階層一致性。

## 標準頁面結構
每個後台頁面應該包含以下標準結構：

```
.admin-page
├── .page-header
│   └── .header-content
│       ├── .title-section
│       │   ├── .page-title (h1)
│       │   └── .page-description (p)
│       └── .action-section (操作按鈕)
├── .stats-section
│   └── .stats-row (gutter="24")
├── .filter-section
│   └── .filter-card
└── .content-section
    └── .content-card
```

## 測試頁面清單

### 1. 儀表板 (Dashboard) ✓
- URL: `/admin/dashboard` 
- 狀態: 已確認符合標準
- 結構: admin-page ✓

### 2. 文章管理 (Posts) ✓  
- URL: `/admin/posts`
- 狀態: 已修復並確認
- 結構: admin-page ✓

### 3. 商品管理 (Products)
- URL: `/admin/products`
- 狀態: 待測試
- 預期: 應該符合標準

### 4. 訂單管理 (Orders)
- URL: `/admin/orders`
- 狀態: 待測試
- 預期: 應該符合標準

### 5. 行銷專案 (Campaigns)
- URL: `/admin/campaigns`
- 狀態: 待測試（API問題已修復）
- 預期: 應該符合標準

### 6. 優惠券管理 (Coupons)
- URL: `/admin/coupons`
- 狀態: 待測試
- 預期: 應該符合標準

### 7. 會員管理 (Users)
- URL: `/admin/users`
- 狀態: 待測試
- 預期: 應該符合標準

### 8. 數據分析 (Analytics)
- URL: `/admin/analytics`
- 狀態: 已修復並確認
- 結構: admin-page ✓

### 9. 系統設定 (Settings)
- URL: `/admin/settings`
- 狀態: 已修復並確認
- 結構: admin-page ✓

### 10. 錯誤日誌 (Error Logs)
- URL: `/admin/error-logs`
- 狀態: 已修復並確認
- 結構: admin-page ✓

## 測試檢查項目

### DOM結構檢查
- [ ] 頁面根容器是否為 `.admin-page`
- [ ] 是否包含 `.page-header` 區域
- [ ] 是否包含 `.stats-section` 區域
- [ ] 是否包含 `.filter-section` 區域
- [ ] 是否包含 `.content-section` 區域

### 統一性檢查
- [ ] 所有 `gutter` 值是否統一為 24
- [ ] 頁面標題是否使用 `h1` 標籤
- [ ] 是否有統一的間距和佈局

### 功能檢查
- [ ] 頁面是否正常載入
- [ ] API調用是否成功
- [ ] 操作按鈕是否可用
- [ ] 數據顯示是否正常

## 測試執行

測試將使用Playwright自動化測試工具，逐一檢查每個頁面的結構和功能。

### 測試步驟
1. 登入管理員帳號
2. 逐一訪問每個後台頁面
3. 檢查DOM結構是否符合標準
4. 驗證功能是否正常運作
5. 記錄任何結構差異或問題
6. 生成測試報告

## 預期結果
所有後台頁面都應該：
- 使用統一的admin-page結構
- 具有一致的視覺外觀和操作體驗
- API調用正常，數據顯示正確
- 無任何JavaScript錯誤或功能異常 