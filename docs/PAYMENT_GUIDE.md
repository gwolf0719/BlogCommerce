# BlogCommerce 金流系統使用指南

## 📋 目錄

1. [系統概述](#系統概述)
2. [支援的金流方式](#支援的金流方式)
3. [金流設定](#金流設定)
4. [使用流程](#使用流程)
5. [API 文檔](#api-文檔)
6. [測試指南](#測試指南)
7. [故障排除](#故障排除)

## 🎯 系統概述

BlogCommerce 金流系統是一個完整的電商付款解決方案，支援多種付款方式，提供自動和手動金流處理功能。

### 主要特色

- ✅ **多元金流支援**：支援轉帳、Line Pay、綠界、PayPal
- ✅ **自動金流處理**：訂單建立時自動產生付款連結
- ✅ **手動金流管理**：管理員可手動確認付款狀態
- ✅ **完整狀態管理**：詳細的付款狀態追蹤
- ✅ **安全性保障**：支援沙盒測試環境
- ✅ **管理介面**：直觀的後台管理系統

## 💳 支援的金流方式

### 1. 轉帳付款 (Transfer)
- **適用場景**：銀行轉帳、ATM 轉帳
- **處理方式**：客戶轉帳後需手動確認
- **設定項目**：銀行名稱、帳號、戶名

### 2. Line Pay
- **適用場景**：Line App 內付款
- **處理方式**：即時線上付款
- **設定項目**：Channel ID、Channel Secret、商店名稱

### 3. 綠界全方位金流 (ECPay)
- **適用場景**：信用卡、ATM、超商付款
- **處理方式**：即時線上付款
- **設定項目**：Merchant ID、HashKey、HashIV、API URL

### 4. PayPal
- **適用場景**：國際付款、信用卡付款
- **處理方式**：即時線上付款
- **設定項目**：Client ID、Client Secret、環境設定

## ⚙️ 金流設定

### 存取管理後台

1. 登入管理員帳號
2. 進入 `設定` → `金流設定`
3. 選擇要啟用的金流方式

### 轉帳設定

```json
{
  \"bank\": \"國泰世華銀行\",
  \"account\": \"1234567890\",
  \"name\": \"商店名稱\"
}
```

### Line Pay 設定

```json
{
  \"channel_id\": \"你的 Channel ID\",
  \"channel_secret\": \"你的 Channel Secret\",
  \"store_name\": \"商店名稱\"
}
```

**取得 Line Pay 憑證**：
1. 前往 [Line Pay Developer](https://pay.line.me/tw/developers)
2. 建立應用程式
3. 取得 Channel ID 和 Channel Secret

### 綠界設定

```json
{
  \"merchant_id\": \"你的 Merchant ID\",
  \"hash_key\": \"你的 HashKey\",
  \"hash_iv\": \"你的 HashIV\",
  \"api_url\": \"https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5\"
}
```

**取得綠界憑證**：
1. 前往 [綠界科技](https://www.ecpay.com.tw/)
2. 申請商戶帳號
3. 取得測試或正式環境憑證

### PayPal 設定

```json
{
  \"client_id\": \"你的 Client ID\",
  \"client_secret\": \"你的 Client Secret\",
  \"environment\": \"sandbox\"
}
```

**取得 PayPal 憑證**：
1. 前往 [PayPal Developer](https://developer.paypal.com/)
2. 建立應用程式
3. 取得 Client ID 和 Client Secret

## 🔄 使用流程

### 自動金流處理

1. **客戶下單**：選擇商品並填寫訂單資訊
2. **選擇付款方式**：從啟用的金流方式中選擇
3. **自動建立付款**：系統自動產生付款連結或資訊
4. **客戶付款**：根據付款方式完成付款
5. **狀態更新**：付款成功後自動更新訂單狀態

### 手動金流處理

1. **管理員查看訂單**：在管理後台查看待付款訂單
2. **確認付款**：手動確認客戶已完成付款
3. **更新狀態**：將訂單狀態更改為已付款
4. **記錄備註**：可添加確認付款的備註

### 付款狀態說明

- **UNPAID** (未付款)：訂單建立，等待付款
- **PENDING** (等待確認)：付款處理中或等待確認
- **PAID** (已付款)：付款成功確認
- **FAILED** (付款失敗)：付款過程失敗
- **REFUNDED** (已退款)：已處理退款
- **PARTIAL** (部分付款)：部分金額已付款

## 📡 API 文檔

### 金流設定 API

#### 取得金流設定
```http
GET /api/settings/payment_{method}
Authorization: Bearer {admin_token}
```

#### 更新金流設定
```http
PUT /api/settings/payment_{method}
Authorization: Bearer {admin_token}
Content-Type: application/json

{設定資料}
```

### 付款處理 API

#### 建立付款訂單
```http
POST /api/payment/create
Authorization: Bearer {token}
Content-Type: application/json

{
  \"order_id\": \"訂單編號\",
  \"payment_method\": \"付款方式\"
}
```

#### 查詢付款狀態
```http
GET /api/payment/status/{order_id}
```

#### 手動確認付款
```http
POST /api/payment/manual-confirm
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  \"order_id\": \"訂單編號\",
  \"notes\": \"確認備註\"
}
```

### 訂單整合

#### 建立訂單（含付款方式）
```http
POST /api/orders/
Authorization: Bearer {token}
Content-Type: application/json

{
  \"customer_name\": \"客戶姓名\",
  \"customer_email\": \"客戶信箱\",
  \"customer_phone\": \"客戶電話\",
  \"shipping_address\": \"配送地址\",
  \"payment_method\": \"付款方式\",
  \"items\": [
    {
      \"product_id\": 1,
      \"quantity\": 2
    }
  ]
}
```

## 🧪 測試指南

### 測試環境設定

1. **使用沙盒環境**：確保所有金流都設定為測試模式
2. **測試憑證**：使用各金流提供的測試憑證
3. **測試資料**：使用測試用的銀行帳號和信用卡號

### 執行測試

#### 1. 運行展示腳本
```bash
python3 demo_payment.py
```

#### 2. 運行測試套件
```bash
python3 -m pytest tests/test_payment.py -v
```

#### 3. 測試特定金流
```bash
# 測試轉帳
curl -X GET \"http://localhost:8000/api/payment/test/transfer\" \\
  -H \"Authorization: Bearer {admin_token}\"

# 測試 Line Pay
curl -X GET \"http://localhost:8000/api/payment/test/linepay\" \\
  -H \"Authorization: Bearer {admin_token}\"
```

### 測試檢查清單

- [ ] 金流設定可正常儲存和讀取
- [ ] 轉帳訂單可正常建立
- [ ] Line Pay 可正常建立付款連結
- [ ] 綠界可正常建立付款連結
- [ ] PayPal 可正常建立付款連結
- [ ] 手動確認付款功能正常
- [ ] 付款狀態更新正常
- [ ] 訂單與金流整合正常

## 🔧 故障排除

### 常見問題

#### 1. Line Pay 認證錯誤
**錯誤**：`Header information error. authorization is required header.`

**解決方案**：
- 檢查 Channel ID 和 Channel Secret 是否正確
- 確認請求標頭格式正確
- 驗證是否使用正確的 API 端點

#### 2. PayPal 認證失敗
**錯誤**：`Client Authentication failed`

**解決方案**：
- 檢查 Client ID 和 Client Secret 是否正確
- 確認環境設定（sandbox/live）正確
- 驗證 PayPal 應用程式狀態

#### 3. 綠界檢查碼錯誤
**錯誤**：`CheckMacValue verify fail`

**解決方案**：
- 檢查 HashKey 和 HashIV 是否正確
- 確認參數排序和編碼方式正確
- 驗證 MAC 值計算邏輯

#### 4. 資料庫錯誤
**錯誤**：`table orders has no column named payment_method`

**解決方案**：
- 執行資料庫遷移：`alembic upgrade head`
- 檢查模型定義是否正確
- 重新建立資料庫表格

### 偵錯技巧

1. **啟用詳細日誌**：設定 `DEBUG=True`
2. **檢查 API 回應**：使用瀏覽器開發者工具
3. **測試 API 端點**：使用 Postman 或 curl
4. **查看資料庫狀態**：直接查詢資料庫確認資料

### 聯絡支援

如果遇到無法解決的問題，請提供以下資訊：

- 錯誤訊息和堆疊追蹤
- 使用的金流方式和設定
- 測試步驟和預期結果
- 系統環境資訊

## 📝 附錄

### 相關檔案

- **模型定義**：`app/models/order.py`
- **金流服務**：`app/services/payment_service.py`
- **API 路由**：`app/routes/payment.py`
- **前端設定**：`frontend/src/views/Settings.vue`
- **測試檔案**：`tests/test_payment.py`

### 外部資源

- [Line Pay API 文檔](https://pay.line.me/file/guidebook/technicaldocument/LINE_Pay_Integration_Guide_for_Merchant.pdf)
- [綠界 API 文檔](https://developers.ecpay.com.tw/)
- [PayPal API 文檔](https://developer.paypal.com/docs/api/)

---

**版本**：1.0.0  
**更新日期**：2025-06-25  
**維護者**：BlogCommerce 開發團隊