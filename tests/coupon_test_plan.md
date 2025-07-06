# 優惠券功能測試計畫

## 概述
本測試計畫涵蓋優惠券功能的全面測試，包括單元測試、整合測試、功能測試和端到端測試。

## 測試目標
- 覆蓋率：>90%
- 測試通過率：>95%
- 執行時間：<5分鐘
- API響應時間：<200ms

## 測試架構

### 1. 單元測試 (Unit Tests)
#### 1.1 模型測試 (`app/models/coupon.py`)
- **測試項目**：
  - Coupon 模型創建和屬性驗證
  - CouponUsage 模型創建和關聯
  - CouponDistribution 模型創建和關聯
  - 優惠券有效性檢查 (`is_valid()`)
  - 折扣計算邏輯 (`calculate_discount()`)
  - 時區處理
  - 枚舉類型驗證
- **測試文件**：`tests/unit/test_coupon_models.py`

#### 1.2 服務測試 (`app/services/coupon_service.py`)
- **測試項目**：
  - 優惠券代碼生成 (`generate_coupon_code()`)
  - 單一優惠券創建 (`create_coupon()`)
  - 批次優惠券創建 (`batch_create_coupons()`)
  - 優惠券更新 (`update_coupon()`)
  - 優惠券驗證 (`validate_coupon()`)
  - 優惠券使用 (`use_coupon()`)
  - 優惠券分發 (`distribute_coupon()`)
  - 統計資料生成 (`get_coupon_stats()`)
- **測試文件**：`tests/unit/test_coupon_service.py`

### 2. 整合測試 (Integration Tests)
#### 2.1 API測試 (`app/routes/coupons.py`)
- **測試項目**：
  - 管理員端點權限驗證
  - CRUD操作API
  - 批次操作API
  - 分發和統計API
  - 用戶端點驗證
  - 內部API整合
  - 分頁和篩選功能
- **測試文件**：`tests/integration/test_coupon_api.py`

#### 2.2 資料庫整合測試
- **測試項目**：
  - 事務處理
  - 外鍵約束
  - 索引查詢效能
  - 資料一致性
- **測試文件**：`tests/integration/test_coupon_database.py`

### 3. 功能測試 (Functional Tests)
#### 3.1 優惠券生命週期測試
- **測試項目**：
  - 創建 → 分發 → 使用 → 統計完整流程
  - 不同類型優惠券的完整流程
  - 錯誤處理和回滾
- **測試文件**：`tests/functional/test_coupon_lifecycle.py`

#### 3.2 業務規則測試
- **測試項目**：
  - 最低消費金額檢查
  - 商品適用性檢查
  - 使用次數限制
  - 有效期驗證
  - 折扣計算正確性
- **測試文件**：`tests/functional/test_coupon_business_rules.py`

#### 3.3 批次操作測試
- **測試項目**：
  - 大量優惠券創建效能
  - 批次分發效能
  - 錯誤處理和部分成功
- **測試文件**：`tests/functional/test_coupon_batch_operations.py`

### 4. 前端測試 (Frontend Tests)
#### 4.1 Vue 組件測試
- **測試項目**：
  - Coupons.vue 組件功能
  - 表單驗證
  - 數據展示
  - 用戶交互
- **測試文件**：`frontend/tests/unit/coupons.test.js`

#### 4.2 用戶交互測試
- **測試項目**：
  - 表單提交
  - 列表操作
  - 篩選和搜索
  - 響應式設計
- **測試文件**：`frontend/tests/integration/coupons-interaction.test.js`

### 5. 端到端測試 (E2E Tests)
#### 5.1 管理員流程測試
- **測試項目**：
  - 登入管理後台
  - 創建各類型優惠券
  - 編輯和刪除優惠券
  - 批次操作
  - 分發優惠券
  - 查看統計數據
- **測試文件**：`frontend/tests/e2e/admin-coupon-flow.spec.js`

#### 5.2 用戶流程測試
- **測試項目**：
  - 查看可用優惠券
  - 使用優惠券下單
  - 查看使用記錄
  - 錯誤處理
- **測試文件**：`frontend/tests/e2e/user-coupon-flow.spec.js`

### 6. 性能測試 (Performance Tests)
#### 6.1 負載測試
- **測試項目**：
  - API響應時間
  - 並發用戶處理
  - 資料庫查詢效能
- **測試文件**：`tests/performance/test_coupon_load.py`

#### 6.2 壓力測試
- **測試項目**：
  - 大量數據處理
  - 記憶體使用情況
  - 系統穩定性
- **測試文件**：`tests/performance/test_coupon_stress.py`

### 7. 安全測試 (Security Tests)
#### 7.1 權限測試
- **測試項目**：
  - 未授權訪問防護
  - 角色權限驗證
  - 敏感數據保護
- **測試文件**：`tests/security/test_coupon_permissions.py`

#### 7.2 輸入驗證測試
- **測試項目**：
  - SQL注入防護
  - XSS攻擊防護
  - 輸入數據驗證
- **測試文件**：`tests/security/test_coupon_input_validation.py`

## 測試環境設置

### 後端測試環境
```bash
# 安裝測試依賴
pip install pytest pytest-asyncio pytest-cov faker

# 設置測試資料庫
export TEST_DATABASE_URL="sqlite:///test.db"

# 執行測試
pytest tests/ -v --cov=app --cov-report=html
```

### 前端測試環境
```bash
# 安裝測試依賴
npm install --save-dev @vue/test-utils vitest jsdom playwright

# 執行單元測試
npm run test:unit

# 執行端到端測試
npm run test:e2e
```

## 測試資料準備

### 測試用戶
- 管理員帳戶：admin@test.com / admin123
- 普通用戶：user@test.com / user123

### 測試商品
- 商品1：測試商品A ($100)
- 商品2：測試商品B ($200)
- 商品3：測試商品C ($300)

### 測試優惠券
- 固定金額折扣券：10元折扣
- 百分比折扣券：20%折扣
- 免運費券：免運費
- 商品專用券：特定商品折扣

## 測試執行計畫

### 階段一：單元測試
1. 模型測試
2. 服務測試
3. 覆蓋率檢查

### 階段二：整合測試
1. API測試
2. 資料庫整合測試
3. 系統整合測試

### 階段三：功能測試
1. 業務流程測試
2. 錯誤處理測試
3. 效能測試

### 階段四：前端測試
1. 組件測試
2. 交互測試
3. 響應式測試

### 階段五：端到端測試
1. 管理員流程測試
2. 用戶流程測試
3. 系統整體測試

## 測試結果記錄

### 測試執行記錄
- 執行時間：[待填入]
- 測試總數：[待填入]
- 通過數量：[待填入]
- 失敗數量：[待填入]
- 覆蓋率：[待填入]

### 問題記錄
- 發現的問題：[待填入]
- 修復狀態：[待填入]
- 待處理事項：[待填入]

## 自動化持續整合

### GitHub Actions 設定
```yaml
# .github/workflows/test-coupons.yml
name: Coupon Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest tests/ -v --cov=app
```

### 測試報告
- 測試覆蓋率報告
- 效能測試報告
- 安全測試報告
- 測試執行摘要

## 最佳實踐

### 測試設計原則
1. **獨立性**：每個測試都應該獨立運行
2. **可重複性**：測試結果應該一致
3. **可讀性**：測試代碼應該清晰易懂
4. **全面性**：覆蓋所有關鍵功能和邊界情況

### 測試命名規範
- 測試類：`Test{功能名}`
- 測試方法：`test_{功能}_{情境}_{預期結果}`
- 測試文件：`test_{模組名}.py`

### 測試資料管理
- 使用固定的測試資料
- 每次測試前清理資料
- 避免測試間的資料依賴

## 維護計畫

### 定期檢查
- 每週執行完整測試套件
- 每月檢查測試覆蓋率
- 每季度更新測試計畫

### 更新策略
- 新功能必須包含對應測試
- 修復bug時增加回歸測試
- 定期重構測試代碼

## 結論

本測試計畫提供了優惠券功能的全面測試框架，確保系統的穩定性、可靠性和安全性。通過執行這些測試，可以及早發現問題並提高產品質量。 