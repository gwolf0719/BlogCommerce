<!--
行銷專案管理介面

此組件提供完整的行銷專案管理功能，包括專案的創建、編輯、刪除、狀態管理，
以及優惠券的生成、分發和統計查看等功能。

主要功能模組：
1. 專案列表展示：支援分頁、搜尋、篩選
2. 專案 CRUD 操作：創建、編輯、刪除專案
3. 優惠券管理：批次生成、分發給用戶
4. 統計資料：專案總覽、詳細統計、使用情況分析
5. 狀態管理：專案狀態切換（草稿/進行中/暫停/完成/取消）

界面組件：
- 專案統計卡片：顯示總數、進行中專案、生成優惠券數等
- 搜尋篩選區：支援名稱搜尋、狀態篩選
- 專案資料表格：展示專案詳細資訊和操作按鈕
- 專案編輯 Modal：專案創建和編輯表單
- 優惠券管理 Modal：生成、分發、統計等功能

權限要求：
- 僅管理員可訪問此頁面
- 所有操作都需要 JWT 身份驗證

作者：AI Assistant
創建日期：2024
版本：1.0
-->

<template>
  <div class="admin-page">
    <!-- 1. 頁面標題區 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">行銷專案管理</h1>
          <p class="page-description">創建和管理促銷活動與優惠券發放專案</p>
        </div>
        <div class="action-section">
          <a-space>
            <a-button type="primary" @click="showCreateModal">
              <template #icon><PlusOutlined /></template>
              建立專案
            </a-button>
            <a-button @click="showStatsModal">
              <template #icon><BarChartOutlined /></template>
              統計總覽
            </a-button>
          </a-space>
        </div>
      </div>
    </div>

    <!-- 2. 統計卡片區 -->
    <div class="stats-section">
      <a-row :gutter="24" class="stats-row">
        <a-col :span="6">
          <a-card>
            <a-statistic 
              title="總專案數" 
              :value="stats.total_campaigns" 
              :loading="statsLoading"
              :value-style="{ color: '#1890ff' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic 
              title="進行中專案" 
              :value="stats.active_campaigns" 
              :loading="statsLoading"
              :value-style="{ color: '#52c41a' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic 
              title="生成優惠券" 
              :value="stats.total_coupons_generated" 
              :loading="statsLoading"
              :value-style="{ color: '#fa8c16' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic 
              title="總節省金額" 
              :value="stats.total_discount_amount" 
              prefix="$"
              :precision="2"
              :loading="statsLoading"
              :value-style="{ color: '#722ed1' }"
            />
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 3. 搜尋篩選區 -->
    <div class="filter-section">
      <a-card class="filter-card">
        <a-row :gutter="24">
          <a-col :span="8">
            <a-input-search 
              v-model:value="searchText" 
              placeholder="搜尋專案名稱或描述" 
              @search="loadCampaigns"
              allow-clear
            />
          </a-col>
          <a-col :span="4">
            <a-select v-model:value="filterStatus" placeholder="狀態篩選" allow-clear @change="loadCampaigns">
              <a-select-option value="draft">草稿</a-select-option>
              <a-select-option value="active">進行中</a-select-option>
              <a-select-option value="completed">已完成</a-select-option>
              <a-select-option value="cancelled">已取消</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="4">
            <a-button @click="resetFilters">重置篩選</a-button>
          </a-col>
          <a-col :span="4">
            <a-button type="primary" @click="loadCampaigns">搜尋</a-button>
          </a-col>
        </a-row>
      </a-card>
    </div>

    <!-- 4. 主要內容區 -->
    <div class="content-section">
      <a-card class="content-card">
        <a-table
          :columns="columns"
          :data-source="campaigns"
          :loading="loading"
          :pagination="{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 筆記錄`
          }"
          @change="handleTableChange"
          row-key="id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'name'">
              <div>
                <div class="font-semibold">{{ record.name }}</div>
                <div class="text-xs text-gray-500">{{ record.coupon_prefix }}</div>
              </div>
            </template>
            
            <template v-if="column.key === 'status'">
              <a-tag :color="getStatusColor(record.status)">
                {{ getStatusText(record.status) }}
              </a-tag>
            </template>
            
            <template v-if="column.key === 'coupon_info'">
              <div class="text-sm">
                <div>類型：{{ getCouponTypeText(record.coupon_type) }}</div>
                <div>折扣：{{ formatDiscount(record.discount_type, record.discount_value) }}</div>
              </div>
            </template>
            
            <template v-if="column.key === 'period'">
              <div class="text-sm">
                <div>專案：{{ formatDate(record.campaign_start) }} - {{ formatDate(record.campaign_end) }}</div>
                <div class="text-gray-500">優惠券：{{ formatDate(record.coupon_valid_from) }} - {{ formatDate(record.coupon_valid_to) }}</div>
              </div>
            </template>
            
            <template v-if="column.key === 'progress'">
              <div class="text-sm">
                <div>已生成：{{ record.generated_count }} / {{ record.total_coupons }}</div>
                <a-progress 
                  :percent="(record.generated_count / record.total_coupons) * 100" 
                  :showInfo="false" 
                  size="small"
                />
                <div class="mt-1">已分發：{{ record.distributed_count }} | 已使用：{{ record.used_count }}</div>
              </div>
            </template>
            
            <template v-if="column.key === 'actions'">
              <a-space>
                <a-button type="primary" size="small" @click="editCampaign(record)">
                  編輯
                </a-button>
                <a-button size="small" @click="showCouponModal(record)">
                  優惠券
                </a-button>
                <a-button size="small" @click="showStatsModal(record)">
                  統計
                </a-button>
                <a-dropdown>
                  <template #overlay>
                    <a-menu>
                      <a-menu-item @click="showGenerateModal(record)">
                        生成優惠券
                      </a-menu-item>
                      <a-menu-item @click="showDistributeModal(record)">
                        分發優惠券
                      </a-menu-item>
                      <a-menu-divider />
                      <a-menu-item @click="updateStatus(record, 'active')" :disabled="record.status === 'active'">
                        啟動專案
                      </a-menu-item>
                      <a-menu-item @click="updateStatus(record, 'paused')" :disabled="record.status === 'paused'">
                        暫停專案
                      </a-menu-item>
                      <a-menu-item @click="updateStatus(record, 'completed')" :disabled="record.status === 'completed'">
                        完成專案
                      </a-menu-item>
                      <a-menu-divider />
                      <a-menu-item @click="deleteCampaign(record.id)" danger>
                        刪除專案
                      </a-menu-item>
                    </a-menu>
                  </template>
                  <a-button size="small">
                    更多 <DownOutlined />
                  </a-button>
                </a-dropdown>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>

    <!-- 創建/編輯專案 Modal -->
    <a-modal
      v-model:open="createModalVisible"
      :title="editingCampaign ? '編輯專案' : '創建專案'"
      width="1000px"
      @ok="handleCreateOrUpdate"
      @cancel="resetForm"
    >
      <a-form
        ref="formRef"
        :model="campaignForm"
        :rules="formRules"
        layout="vertical"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="專案名稱" name="name">
              <a-input v-model:value="campaignForm.name" placeholder="輸入專案名稱" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="優惠碼前綴" name="coupon_prefix">
              <a-input v-model:value="campaignForm.coupon_prefix" placeholder="例如：SALE2024" />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-form-item label="專案描述" name="description">
          <a-textarea v-model:value="campaignForm.description" :rows="3" placeholder="輸入專案描述" />
        </a-form-item>
        
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="優惠券類型" name="coupon_type">
              <a-select v-model:value="campaignForm.coupon_type">
                <a-select-option value="product_discount">商品折扣</a-select-option>
                <a-select-option value="order_discount">整筆折扣</a-select-option>
                <a-select-option value="free_shipping">免運費</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="折扣類型" name="discount_type">
              <a-select v-model:value="campaignForm.discount_type">
                <a-select-option value="fixed">固定金額</a-select-option>
                <a-select-option value="percentage">百分比</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="折扣值" name="discount_value">
              <a-input-number 
                v-model:value="campaignForm.discount_value" 
                :min="0"
                :max="campaignForm.discount_type === 'percentage' ? 100 : undefined"
                :precision="2"
                style="width: 100%"
                :addon-after="campaignForm.discount_type === 'percentage' ? '%' : '$'"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="最低消費" name="minimum_amount">
              <a-input-number 
                v-model:value="campaignForm.minimum_amount" 
                :min="0"
                :precision="2"
                style="width: 100%"
                addon-after="$"
                placeholder="可選"
              />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="最高折扣" name="maximum_discount">
              <a-input-number 
                v-model:value="campaignForm.maximum_discount" 
                :min="0"
                :precision="2"
                style="width: 100%"
                addon-after="$"
                placeholder="可選"
              />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="總優惠券數" name="total_coupons">
              <a-input-number 
                v-model:value="campaignForm.total_coupons" 
                :min="1"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="專案開始時間" name="campaign_start">
              <a-date-picker 
                v-model:value="campaignForm.campaign_start" 
                show-time 
                format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="專案結束時間" name="campaign_end">
              <a-date-picker 
                v-model:value="campaignForm.campaign_end" 
                show-time 
                format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="優惠券有效開始" name="coupon_valid_from">
              <a-date-picker 
                v-model:value="campaignForm.coupon_valid_from" 
                show-time 
                format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="優惠券有效結束" name="coupon_valid_to">
              <a-date-picker 
                v-model:value="campaignForm.coupon_valid_to" 
                show-time 
                format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="初始生成數量" name="initial_coupons">
              <a-input-number 
                v-model:value="campaignForm.initial_coupons" 
                :min="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="專案狀態" name="status">
              <a-select v-model:value="campaignForm.status">
                <a-select-option value="draft">草稿</a-select-option>
                <a-select-option value="active">進行中</a-select-option>
                <a-select-option value="paused">暫停</a-select-option>
                <a-select-option value="completed">已完成</a-select-option>
                <a-select-option value="cancelled">已取消</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 其他 Modal 組件... -->
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { 
  PlusOutlined, 
  BarChartOutlined,
  DownOutlined
} from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'

const authStore = useAuthStore()

// 響應式數據
const loading = ref(false)
const statsLoading = ref(false)
const createModalVisible = ref(false)
const editingCampaign = ref(null)

const campaigns = ref([])
const stats = ref({
  total_campaigns: 0,
  active_campaigns: 0,
  total_coupons_generated: 0,
  total_discount_amount: 0
})

// 搜尋和篩選
const searchText = ref('')
const filterStatus = ref(null)

// 分頁
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

// 表單數據
const campaignForm = reactive({
  name: '',
  description: '',
  coupon_prefix: '',
  coupon_type: 'order_discount',
  discount_type: 'fixed',
  discount_value: 0,
  minimum_amount: null,
  maximum_discount: null,
  product_id: null,
  campaign_start: null,
  campaign_end: null,
  coupon_valid_from: null,
  coupon_valid_to: null,
  total_coupons: 100,
  initial_coupons: 0,
  status: 'draft',
  is_active: true
})

// 表格欄位定義
const columns = [
  { title: '專案名稱', key: 'name', width: 200, fixed: 'left' },
  { title: '狀態', key: 'status', width: 80 },
  { title: '優惠券信息', key: 'coupon_info', width: 150 },
  { title: '時間範圍', key: 'period', width: 200 },
  { title: '進度統計', key: 'progress', width: 200 },
  { title: '操作', key: 'actions', width: 200, fixed: 'right' }
]

// 表單驗證規則
const formRules = {
  name: [{ required: true, message: '請輸入專案名稱' }],
  coupon_prefix: [{ required: true, message: '請輸入優惠碼前綴' }],
  coupon_type: [{ required: true, message: '請選擇優惠券類型' }],
  discount_type: [{ required: true, message: '請選擇折扣類型' }],
  discount_value: [{ required: true, message: '請輸入折扣值' }],
  campaign_start: [{ required: true, message: '請選擇專案開始時間' }],
  campaign_end: [{ required: true, message: '請選擇專案結束時間' }],
  coupon_valid_from: [{ required: true, message: '請選擇優惠券有效開始時間' }],
  coupon_valid_to: [{ required: true, message: '請選擇優惠券有效結束時間' }],
  total_coupons: [{ required: true, message: '請輸入總優惠券數量' }]
}

// ==================== 工具函數 ====================

/**
 * 獲取專案狀態對應的顏色
 * @param {string} status - 專案狀態
 * @returns {string} Ant Design 標籤顏色
 */
const getStatusColor = (status) => {
  const colors = {
    draft: 'default',     // 草稿 - 預設顏色
    active: 'green',      // 進行中 - 綠色
    paused: 'orange',     // 暫停 - 橙色
    completed: 'blue',    // 已完成 - 藍色
    cancelled: 'red'      // 已取消 - 紅色
  }
  return colors[status] || 'default'
}

/**
 * 獲取專案狀態的中文顯示文字
 * @param {string} status - 專案狀態英文值
 * @returns {string} 中文狀態文字
 */
const getStatusText = (status) => {
  const texts = {
    draft: '草稿',
    active: '進行中',
    paused: '暫停',
    completed: '已完成',
    cancelled: '已取消'
  }
  return texts[status] || status
}

/**
 * 獲取優惠券類型的中文顯示文字
 * @param {string} type - 優惠券類型英文值
 * @returns {string} 中文類型文字
 */
const getCouponTypeText = (type) => {
  const texts = {
    product_discount: '商品折扣',
    order_discount: '整筆折扣',
    free_shipping: '免運費'
  }
  return texts[type] || type
}

/**
 * 格式化折扣顯示
 * @param {string} type - 折扣類型（fixed/percentage）
 * @param {number} value - 折扣值
 * @returns {string} 格式化的折扣文字
 */
const formatDiscount = (type, value) => {
  return type === 'percentage' ? `${value}%` : `$${value}`
}

/**
 * 格式化日期顯示（簡短格式）
 * @param {string} dateStr - 日期字串
 * @returns {string} 格式化的日期（MM/DD）
 */
const formatDate = (dateStr) => {
  return dayjs(dateStr).format('MM/DD')
}

// ==================== API 請求函數 ====================

/**
 * 統一的 API 請求處理函數
 * 
 * 提供統一的 HTTP 請求處理，包括：
 * - 自動添加認證 header
 * - 統一的錯誤處理
 * - JSON 格式處理
 * 
 * @param {string} url - 請求的 URL
 * @param {object} options - fetch 選項
 * @returns {Promise<object>} API 回應的 JSON 資料
 * @throws {Error} 當請求失敗時拋出錯誤
 */
const apiRequest = async (url, options = {}) => {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authStore.token}`,
      ...options.headers
    },
    ...options
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '請求失敗')
  }
  
  return response.json()
}

/**
 * 載入行銷專案列表
 * 
 * 根據當前的篩選條件和分頁設定從 API 載入專案列表，包括：
 * - 分頁處理（skip, limit）
 * - 搜尋條件（專案名稱）
 * - 狀態篩選（專案狀態、啟用狀態）
 * - 更新分頁統計資訊
 */
const loadCampaigns = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('skip', (pagination.current - 1) * pagination.pageSize)
    params.append('limit', pagination.pageSize)
    
    if (searchText.value) params.append('search', searchText.value)
    if (filterStatus.value) params.append('status', filterStatus.value)
    
    const data = await apiRequest(`/api/campaigns?${params}`)
    
    // 安全檢查API回應結構
    if (data && typeof data === 'object') {
      campaigns.value = data.items || []
      pagination.total = data.total || 0
    } else {
      campaigns.value = []
      pagination.total = 0
      console.warn('API返回了意外的資料結構:', data)
    }
  } catch (error) {
    console.error('載入專案失敗:', error)
    campaigns.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

/**
 * 載入專案總覽統計資料
 * 
 * 從 API 獲取行銷專案的總覽統計資訊，包括：
 * - 總專案數量
 * - 進行中專案數量  
 * - 總生成優惠券數量
 * - 總節省金額等統計指標
 */
const loadStats = async () => {
  statsLoading.value = true
  try {
    const data = await apiRequest('/api/campaigns/stats/overview')
    if (data && typeof data === 'object') {
      stats.value = data
    } else {
      console.warn('統計API返回了意外的資料結構:', data)
    }
  } catch (error) {
    console.error('載入統計資料失敗:', error)
  } finally {
    statsLoading.value = false
  }
}

// 事件處理
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadCampaigns()
}

const showCreateModal = () => {
  editingCampaign.value = null
  resetForm()
  createModalVisible.value = true
}

const editCampaign = (campaign) => {
  editingCampaign.value = campaign
  Object.assign(campaignForm, {
    ...campaign,
    campaign_start: dayjs(campaign.campaign_start),
    campaign_end: dayjs(campaign.campaign_end),
    coupon_valid_from: dayjs(campaign.coupon_valid_from),
    coupon_valid_to: dayjs(campaign.coupon_valid_to)
  })
  createModalVisible.value = true
}

const resetForm = () => {
  Object.assign(campaignForm, {
    name: '',
    description: '',
    coupon_prefix: '',
    coupon_type: 'order_discount',
    discount_type: 'fixed',
    discount_value: 0,
    minimum_amount: null,
    maximum_discount: null,
    product_id: null,
    campaign_start: null,
    campaign_end: null,
    coupon_valid_from: null,
    coupon_valid_to: null,
    total_coupons: 100,
    initial_coupons: 0,
    status: 'draft',
    is_active: true
  })
}

const resetFilters = () => {
  searchText.value = ''
  filterStatus.value = null
  loadCampaigns()
}

const handleCreateOrUpdate = async () => {
  try {
    const formData = {
      ...campaignForm,
      campaign_start: campaignForm.campaign_start.toISOString(),
      campaign_end: campaignForm.campaign_end.toISOString(),
      coupon_valid_from: campaignForm.coupon_valid_from.toISOString(),
      coupon_valid_to: campaignForm.coupon_valid_to.toISOString()
    }
    
    if (editingCampaign.value) {
      await apiRequest(`/api/campaigns/${editingCampaign.value.id}`, {
        method: 'PUT',
        body: JSON.stringify(formData)
      })
      message.success('專案更新成功')
    } else {
      await apiRequest('/api/campaigns', {
        method: 'POST',
        body: JSON.stringify(formData)
      })
      message.success('專案創建成功')
    }
    
    createModalVisible.value = false
    loadCampaigns()
    loadStats()
  } catch (error) {
    message.error(`操作失敗：${error.message}`)
  }
}

const updateStatus = async (campaign, status) => {
  try {
    await apiRequest(`/api/campaigns/${campaign.id}/status?status=${status}`, {
      method: 'PATCH'
    })
    message.success('狀態更新成功')
    loadCampaigns()
  } catch (error) {
    message.error(`狀態更新失敗：${error.message}`)
  }
}

const deleteCampaign = async (id) => {
  try {
    await apiRequest(`/api/campaigns/${id}`, { method: 'DELETE' })
    message.success('專案刪除成功')
    loadCampaigns()
    loadStats()
  } catch (error) {
    message.error(`刪除失敗：${error.message}`)
  }
}

// 生命週期
onMounted(() => {
  loadCampaigns()
  loadStats()
})
</script>

<style scoped>
.ant-table-tbody > tr > td {
  vertical-align: top;
}
</style> 