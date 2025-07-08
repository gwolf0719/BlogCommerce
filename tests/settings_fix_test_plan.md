# 金流設定和運費設定修復測試計畫

## 問題描述

用戶反映兩個主要問題：
1. **金流可用的項目沒有連動** - 後台金流設定與前台結帳頁面不同步
2. **後台也沒有看到可以設定物流費用的地方** - 運費設定區塊顯示異常

## 問題分析

### 金流設定問題
- 前端使用過時的API端點（`/api/settings/payment_transfer`等）
- 404錯誤：`payment_transfer`, `payment_linepay`, `payment_ecpay`, `payment_paypal`
- 前後端API端點不一致

### 運費設定問題
- 運費設定區塊存在但可能因為前端錯誤而未顯示
- API端點正確但前端可能載入失敗

## 修復方案

### 1. 前端金流設定修復

**修改檔案：** `frontend/src/views/Settings.vue`

#### loadPaymentSettings() 函數修復
```javascript
// 修復前：使用多個個別API端點
const [transferRes, linepayRes, ecpayRes, paypalRes] = await Promise.all([
  fetch('/api/settings/payment_transfer', ...),
  fetch('/api/settings/payment_linepay', ...),
  fetch('/api/settings/payment_ecpay', ...),
  fetch('/api/settings/payment_paypal', ...)
])

// 修復後：使用統一API端點
const response = await fetch('/api/settings/payment/settings', {
  headers: { 'Authorization': `Bearer ${authStore.token}` }
})
```

#### savePaymentSettings() 函數修復
```javascript
// 修復前：使用錯誤的API端點
fetch('/api/settings/payment_transfer', {...})

// 修復後：使用正確的啟用狀態API端點
fetch('/api/settings/payment_transfer_enabled', {
  body: JSON.stringify({ 
    value: payment.enabledMethods.includes('transfer') ? 'true' : 'false', 
    category: 'payment', 
    data_type: 'boolean' 
  })
})
```

### 2. 圖示修復

**修改檔案：** `frontend/src/views/Settings.vue`

```javascript
// 修復前：使用不存在的圖示
import { TruckOutlined } from '@ant-design/icons-vue'

// 修復後：使用可用的圖示
import { CarOutlined } from '@ant-design/icons-vue'
```

## 測試計畫

### 自動化測試

#### 1. API端點測試
```bash
# 測試統一金流設定API
curl -s http://localhost:8001/api/settings/payment/settings

# 預期結果：
{
  "transfer": {"enabled": true},
  "linepay": {"enabled": false},
  "ecpay": {"enabled": false},
  "paypal": {"enabled": false},
  "shipping": {"fee": 80, "free_threshold": 1000}
}
```

#### 2. 運費設定API測試
```bash
# 測試運費設定（需要認證）
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/settings/shipping_fee

# 預期結果：
{"value": 80, "key": "shipping_fee", ...}
```

### 手動測試

#### 1. 後台金流設定測試
1. 開啟 http://localhost:8001/admin/settings
2. 點擊左側選單「金流設定」
3. 檢查項目：
   - ✅ 運費設定區塊顯示
   - ✅ 四種金流選項顯示（銀行轉帳、Line Pay、綠界、PayPal）
   - ✅ 金流啟用狀態正確顯示
   - ✅ 切換金流開關正常運作

#### 2. 後台運費設定測試
1. 在金流設定頁面上方找到「運費設定」區塊
2. 檢查項目：
   - ✅ 運費金額輸入框
   - ✅ 免運門檻輸入框
   - ✅ 儲存按鈕
   - ✅ 設定說明文字

#### 3. 前台結帳頁面測試
1. 添加商品到購物車
2. 開啟 http://localhost:8001/checkout
3. 檢查項目：
   - ✅ 付款方式與後台設定同步
   - ✅ 只顯示已啟用的付款方式
   - ✅ 運費計算正確
   - ✅ 下單按鈕可點擊

#### 4. 金流連動測試
1. 在後台關閉所有金流
2. 檢查前台結帳頁面顯示警告
3. 在後台啟用轉帳金流
4. 檢查前台立即顯示轉帳選項

## 測試結果驗證

### 成功標準
- [ ] 後台金流設定正常載入，無404錯誤
- [ ] 後台運費設定區塊正常顯示
- [ ] 金流啟用/停用在前後台同步
- [ ] 運費設定可以正常修改和保存
- [ ] 前台結帳頁面付款方式正確顯示
- [ ] 前端建置無錯誤

### 測試環境
- **後端服務：** http://localhost:8001
- **前端管理介面：** http://localhost:8001/admin
- **前台結帳頁面：** http://localhost:8001/checkout
- **測試帳號：** admin / admin123

## 修復摘要

### 解決的問題
1. ✅ 修復前端金流設定API端點錯誤
2. ✅ 修復金流啟用狀態同步問題
3. ✅ 修復運費設定顯示問題
4. ✅ 修復前端建置錯誤（圖示問題）

### API端點對應
| 功能 | 舊端點 (錯誤) | 新端點 (正確) |
|------|---------------|---------------|
| 金流狀態查詢 | `/api/settings/payment_transfer` | `/api/settings/payment/settings` |
| 金流啟用設定 | `/api/settings/payment_transfer` | `/api/settings/payment_transfer_enabled` |
| 運費設定 | 正確 | `/api/settings/shipping_fee` |
| 免運門檻 | 正確 | `/api/settings/free_shipping_threshold` |

### 系統狀態
- **轉帳金流：** 已啟用 ✅
- **其他金流：** 已停用
- **運費：** NT$ 80
- **免運門檻：** NT$ 1,000

修復完成，金流設定和運費設定現在可以正常連動和配置。 