<template>
  <div class="admin-page">
    <!-- 1. 頁面標題區 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">優惠券管理</h1>
          <p class="page-description">管理系統中的所有優惠券，包括創建、分發和使用記錄</p>
        </div>
        <div class="action-section">
          <a-space>
            <a-button type="primary" @click="showCreateModal">
              <template #icon><PlusOutlined /></template>
              建立優惠券
            </a-button>
            <a-button @click="showBatchCreateModal">
              <template #icon><AppstoreAddOutlined /></template>
              批次建立
            </a-button>
            <a-button @click="showStatsModal">
              <template #icon><BarChartOutlined /></template>
              統計資料
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
              title="總優惠券數" 
              :value="stats.total_coupons" 
              :loading="statsLoading"
              :value-style="{ color: '#1890ff' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic 
              title="有效優惠券" 
              :value="stats.active_coupons" 
              :loading="statsLoading"
              :value-style="{ color: '#52c41a' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic 
              title="已使用" 
              :value="stats.used_coupons" 
              :loading="statsLoading"
              :value-style="{ color: '#fa8c16' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic 
              title="總折扣金額" 
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
              placeholder="搜尋優惠券代碼或名稱" 
              @search="loadCoupons"
              allow-clear
            />
          </a-col>
          <a-col :span="4">
            <a-select v-model:value="filterType" placeholder="類型篩選" allow-clear @change="loadCoupons">
              <a-select-option value="product_discount">商品折扣</a-select-option>
              <a-select-option value="order_discount">整筆折扣</a-select-option>
              <a-select-option value="free_shipping">免運費</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="4">
            <a-select v-model:value="filterStatus" placeholder="狀態篩選" allow-clear @change="loadCoupons">
              <a-select-option :value="true">啟用</a-select-option>
              <a-select-option :value="false">停用</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="4">
            <a-select v-model:value="filterExpired" placeholder="過期狀態" allow-clear @change="loadCoupons">
              <a-select-option :value="false">有效</a-select-option>
              <a-select-option :value="true">已過期</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="4">
            <a-button @click="resetFilters">重置篩選</a-button>
          </a-col>
        </a-row>
      </a-card>
    </div>

    <!-- 4. 主要內容區 -->
    <div class="content-section">
      <a-card class="content-card">
        <a-table 
          :columns="columns" 
          :data-source="coupons" 
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
            <template v-if="column.key === 'code'">
              <a-typography-text :copyable="{ text: record.code }">
                {{ record.code }}
              </a-typography-text>
            </template>
            
            <template v-if="column.key === 'type'">
              <a-tag :color="getCouponTypeColor(record.coupon_type)">
                {{ getCouponTypeText(record.coupon_type) }}
              </a-tag>
            </template>
            
            <template v-if="column.key === 'discount'">
              <span v-if="record.discount_type === 'fixed'">
                ${{ record.discount_value }}
              </span>
              <span v-else>
                {{ record.discount_value }}%
              </span>
            </template>
            
            <template v-if="column.key === 'status'">
              <a-tag :color="record.is_active ? 'green' : 'red'">
                {{ record.is_active ? '啟用' : '停用' }}
              </a-tag>
            </template>
            
            <template v-if="column.key === 'validity'">
              <div class="text-sm">
                <div>{{ formatDate(record.valid_from) }}</div>
                <div class="text-gray-500">至 {{ formatDate(record.valid_to) }}</div>
              </div>
            </template>
            
            <template v-if="column.key === 'usage'">
              <div class="text-center">
                <div class="text-lg font-semibold">{{ record.usage_count }}</div>
                <a-button 
                  type="link" 
                  size="small" 
                  @click="showUsageModal(record)"
                  v-if="record.usage_count > 0"
                >
                  查看記錄
                </a-button>
              </div>
            </template>
            
            <template v-if="column.key === 'actions'">
              <a-space>
                <a-button type="primary" size="small" @click="editCoupon(record)">
                  編輯
                </a-button>
                <a-button size="small" @click="showDistributeModal(record)">
                  分發
                </a-button>
                <a-popconfirm
                  title="確定要刪除這個優惠券嗎？"
                  @confirm="deleteCoupon(record.id)"
                  ok-text="是"
                  cancel-text="否"
                >
                  <a-button 
                    danger 
                    size="small"
                    :disabled="record.usage_count > 0"
                  >
                    刪除
                  </a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>

    <!-- 建立/編輯優惠券 Modal -->
    <a-modal
      v-model:open="createModalVisible"
      :title="editingCoupon ? '編輯優惠券' : '建立優惠券'"
      width="800px"
      @ok="handleCreateOrUpdate"
      @cancel="resetForm"
    >
      <a-form
        ref="formRef"
        :model="couponForm"
        :rules="formRules"
        layout="vertical"
      >
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="優惠券名稱" name="name">
              <a-input v-model:value="couponForm.name" placeholder="輸入優惠券名稱" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="優惠券類型" name="coupon_type">
              <a-select v-model:value="couponForm.coupon_type" @change="onCouponTypeChange">
                <a-select-option value="product_discount">單一商品折扣</a-select-option>
                <a-select-option value="order_discount">整筆消費折扣</a-select-option>
                <a-select-option value="free_shipping">免運費折扣</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-form-item label="描述" name="description">
          <a-textarea v-model:value="couponForm.description" :rows="3" placeholder="輸入優惠券描述" />
        </a-form-item>
        
        <a-row :gutter="24">
          <a-col :span="8">
            <a-form-item label="折扣類型" name="discount_type">
              <a-select v-model:value="couponForm.discount_type">
                <a-select-option value="fixed">固定金額</a-select-option>
                <a-select-option value="percentage">百分比</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="折扣值" name="discount_value">
              <a-input-number 
                v-model:value="couponForm.discount_value" 
                :min="0"
                :max="couponForm.discount_type === 'percentage' ? 100 : undefined"
                :precision="2"
                style="width: 100%"
                :addon-after="couponForm.discount_type === 'percentage' ? '%' : '$'"
              />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="最低消費" name="minimum_amount">
              <a-input-number 
                v-model:value="couponForm.minimum_amount" 
                :min="0"
                :precision="2"
                style="width: 100%"
                addon-after="$"
                placeholder="可選"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="24" v-if="couponForm.discount_type === 'percentage'">
          <a-col :span="12">
            <a-form-item label="最高折扣金額" name="maximum_discount">
              <a-input-number 
                v-model:value="couponForm.maximum_discount" 
                :min="0"
                :precision="2"
                style="width: 100%"
                addon-after="$"
                placeholder="可選"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="狀態" name="is_active">
              <a-switch v-model:checked="couponForm.is_active" checked-children="啟用" un-checked-children="停用" />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="24" v-if="couponForm.coupon_type === 'product_discount'">
          <a-col :span="24">
            <a-form-item label="適用商品" name="product_id">
              <a-select 
                v-model:value="couponForm.product_id" 
                placeholder="選擇適用的商品"
                show-search
                :filter-option="filterProduct"
              >
                <a-select-option 
                  v-for="product in products" 
                  :key="product.id" 
                  :value="product.id"
                >
                  {{ product.name }} (${{ product.price }})
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="有效期開始" name="valid_from">
              <a-date-picker 
                v-model:value="couponForm.valid_from" 
                show-time 
                format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="有效期結束" name="valid_to">
              <a-date-picker 
                v-model:value="couponForm.valid_to" 
                show-time 
                format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 批次建立 Modal -->
    <a-modal
      v-model:open="batchCreateModalVisible"
      title="批次建立優惠券"
      width="600px"
      @ok="handleBatchCreate"
    >
      <a-form layout="vertical">
        <a-form-item label="代碼前綴">
          <a-input v-model:value="batchForm.code_prefix" placeholder="如: SALE2024" />
        </a-form-item>
        <a-form-item label="建立數量">
          <a-input-number v-model:value="batchForm.count" :min="1" :max="1000" style="width: 100%" />
        </a-form-item>
        <a-form-item label="是否自動分發">
          <a-switch v-model:checked="batchForm.auto_distribute" />
        </a-form-item>
        <div v-if="batchForm.auto_distribute">
          <a-form-item label="目標用戶">
            <a-select 
              v-model:value="batchForm.target_users" 
              mode="multiple"
              placeholder="選擇用戶"
              style="width: 100%"
            >
              <a-select-option v-for="user in users" :key="user.id" :value="user.id">
                {{ user.username }} ({{ user.email }})
              </a-select-option>
            </a-select>
          </a-form-item>
        </div>
      </a-form>
    </a-modal>

    <!-- 分發 Modal -->
    <a-modal
      v-model:open="distributeModalVisible"
      title="分發優惠券"
      @ok="handleDistribute"
    >
      <a-form layout="vertical">
        <a-form-item label="選擇用戶">
          <a-select 
            v-model:value="distributeForm.user_ids" 
            mode="multiple"
            placeholder="選擇要分發的用戶"
            style="width: 100%"
            show-search
            :filter-option="filterUser"
          >
            <a-select-option v-for="user in users" :key="user.id" :value="user.id">
              {{ user.username }} ({{ user.email }})
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="備註">
          <a-textarea v-model:value="distributeForm.notes" placeholder="分發備註（可選）" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 使用記錄 Modal -->
    <a-modal
      v-model:open="usageModalVisible"
      title="使用記錄"
      width="800px"
      :footer="null"
    >
      <a-table 
        :columns="usageColumns" 
        :data-source="usageRecords" 
        :loading="usageLoading"
        :pagination="false"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'user'">
            {{ record.user_name || '訪客' }}
          </template>
          <template v-if="column.key === 'amount'">
            ${{ record.discount_amount }}
          </template>
          <template v-if="column.key === 'time'">
            {{ formatDateTime(record.used_at) }}
          </template>
        </template>
      </a-table>
    </a-modal>

    <!-- 統計資料 Modal -->
    <a-modal
      v-model:open="statsModalVisible"
      title="優惠券統計資料"
      width="1000px"
      :footer="null"
    >
      <a-row :gutter="24">
        <a-col :span="12">
          <a-card title="按類型統計">
            <div v-for="(count, type) in stats.by_type" :key="type" class="mb-2">
              <span>{{ getCouponTypeText(type) }}: </span>
              <span class="font-semibold">{{ count }}</span>
            </div>
          </a-card>
        </a-col>
        <a-col :span="12">
          <a-card title="月度趨勢">
            <div v-for="(count, month) in stats.by_month" :key="month" class="mb-2">
              <span>{{ month }}: </span>
              <span class="font-semibold">{{ count }}</span>
            </div>
          </a-card>
        </a-col>
      </a-row>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { 
  PlusOutlined, 
  AppstoreAddOutlined, 
  BarChartOutlined 
} from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'

const authStore = useAuthStore()

// 響應式數據
const loading = ref(false)
const statsLoading = ref(false)
const createModalVisible = ref(false)
const batchCreateModalVisible = ref(false)
const distributeModalVisible = ref(false)
const usageModalVisible = ref(false)
const statsModalVisible = ref(false)
const editingCoupon = ref(null)

const coupons = ref([])
const products = ref([])
const users = ref([])
const usageRecords = ref([])

// 搜尋和篩選
const searchText = ref('')
const filterType = ref(null)
const filterStatus = ref(null)
const filterExpired = ref(null)

// 分頁
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

// 統計資料
const stats = ref({
  total_coupons: 0,
  active_coupons: 0,
  used_coupons: 0,
  total_discount_amount: 0,
  by_type: {},
  by_month: {}
})

// 表單數據
const couponForm = reactive({
  name: '',
  description: '',
  coupon_type: 'order_discount',
  discount_type: 'fixed',
  discount_value: 0,
  minimum_amount: null,
  maximum_discount: null,
  product_id: null,
  valid_from: null,
  valid_to: null,
  is_active: true
})

const batchForm = reactive({
  code_prefix: '',
  count: 10,
  auto_distribute: false,
  target_users: []
})

const distributeForm = reactive({
  coupon_id: null,
  user_ids: [],
  notes: ''
})

// 表格欄位定義
const columns = [
  { title: '代碼', dataIndex: 'code', key: 'code', width: 120 },
  { title: '名稱', dataIndex: 'name', key: 'name', width: 150 },
  { title: '類型', key: 'type', width: 100 },
  { title: '折扣', key: 'discount', width: 80 },
  { title: '狀態', key: 'status', width: 80 },
  { title: '有效期', key: 'validity', width: 160 },
  { title: '使用次數', key: 'usage', width: 100 },
  { title: '操作', key: 'actions', width: 200, fixed: 'right' }
]

const usageColumns = [
  { title: '用戶', key: 'user', width: 150 },
  { title: '訂單號', dataIndex: 'order_number', key: 'order', width: 150 },
  { title: '折扣金額', key: 'amount', width: 100 },
  { title: '使用時間', key: 'time', width: 180 }
]

// 表單驗證規則
const formRules = {
  name: [{ required: true, message: '請輸入優惠券名稱' }],
  coupon_type: [{ required: true, message: '請選擇優惠券類型' }],
  discount_type: [{ required: true, message: '請選擇折扣類型' }],
  discount_value: [{ required: true, message: '請輸入折扣值' }],
  valid_from: [{ required: true, message: '請選擇有效期開始時間' }],
  valid_to: [{ required: true, message: '請選擇有效期結束時間' }],
  product_id: [{ 
    required: true, 
    message: '商品折扣券必須選擇商品',
    validator: (rule, value) => {
      if (couponForm.coupon_type === 'product_discount' && !value) {
        return Promise.reject('商品折扣券必須選擇商品')
      }
      return Promise.resolve()
    }
  }]
}

// 工具函數
const getCouponTypeColor = (type) => {
  const colors = {
    'product_discount': 'blue',
    'order_discount': 'green',
    'free_shipping': 'orange'
  }
  return colors[type] || 'default'
}

const getCouponTypeText = (type) => {
  const texts = {
    'product_discount': '商品折扣',
    'order_discount': '整筆折扣',
    'free_shipping': '免運費'
  }
  return texts[type] || type
}

const formatDate = (dateStr) => {
  return dayjs(dateStr).format('YYYY-MM-DD')
}

const formatDateTime = (dateStr) => {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}

const filterProduct = (input, option) => {
  return option.children[0].children.toLowerCase().includes(input.toLowerCase())
}

const filterUser = (input, option) => {
  return option.children[0].children.toLowerCase().includes(input.toLowerCase())
}

// API 請求函數
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

// 載入數據
const loadCoupons = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('skip', (pagination.current - 1) * pagination.pageSize)
    params.append('limit', pagination.pageSize)
    
    if (filterType.value !== null) params.append('coupon_type', filterType.value)
    if (filterStatus.value !== null) params.append('active_only', filterStatus.value)
    if (filterExpired.value !== null) params.append('expired_only', filterExpired.value)
    
    const data = await apiRequest(`/api/coupons?${params}`)
    coupons.value = data
    // pagination.total = data.total
  } catch (error) {
    message.error(`載入優惠券失敗：${error.message}`)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  statsLoading.value = true
  try {
    const data = await apiRequest('/api/coupons/stats/overview')
    stats.value = data
  } catch (error) {
    message.error(`載入統計資料失敗：${error.message}`)
  } finally {
    statsLoading.value = false
  }
}

const loadProducts = async () => {
  try {
    const data = await apiRequest('/api/products?active_only=true&limit=1000')
    products.value = data
  } catch (error) {
    console.error('載入商品失敗:', error)
  }
}

const loadUsers = async () => {
  try {
    const data = await apiRequest('/api/admin/users?limit=1000')
    users.value = data
  } catch (error) {
    console.error('載入用戶失敗:', error)
  }
}

// 事件處理
const handleTableChange = (pag, filters, sorter) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadCoupons()
}

const showCreateModal = () => {
  editingCoupon.value = null
  resetForm()
  createModalVisible.value = true
}

const showBatchCreateModal = () => {
  Object.assign(batchForm, {
    code_prefix: '',
    count: 10,
    auto_distribute: false,
    target_users: []
  })
  batchCreateModalVisible.value = true
}

const showStatsModal = () => {
  statsModalVisible.value = true
}

const showDistributeModal = (coupon) => {
  distributeForm.coupon_id = coupon.id
  distributeForm.user_ids = []
  distributeForm.notes = ''
  distributeModalVisible.value = true
}

const showUsageModal = async (coupon) => {
  usageModalVisible.value = true
  try {
    const data = await apiRequest(`/api/coupons/${coupon.id}/usage`)
    usageRecords.value = data
  } catch (error) {
    message.error(`載入使用記錄失敗：${error.message}`)
  }
}

const editCoupon = (coupon) => {
  editingCoupon.value = coupon
  Object.assign(couponForm, {
    ...coupon,
    valid_from: dayjs(coupon.valid_from),
    valid_to: dayjs(coupon.valid_to)
  })
  createModalVisible.value = true
}

const resetForm = () => {
  Object.assign(couponForm, {
    name: '',
    description: '',
    coupon_type: 'order_discount',
    discount_type: 'fixed',
    discount_value: 0,
    minimum_amount: null,
    maximum_discount: null,
    product_id: null,
    valid_from: null,
    valid_to: null,
    is_active: true
  })
}

const resetFilters = () => {
  searchText.value = ''
  filterType.value = null
  filterStatus.value = null
  filterExpired.value = null
  loadCoupons()
}

const onCouponTypeChange = () => {
  if (couponForm.coupon_type !== 'product_discount') {
    couponForm.product_id = null
  }
}

const handleCreateOrUpdate = async () => {
  try {
    const formData = {
      ...couponForm,
      valid_from: couponForm.valid_from.toISOString(),
      valid_to: couponForm.valid_to.toISOString()
    }
    
    if (editingCoupon.value) {
      await apiRequest(`/api/coupons/${editingCoupon.value.id}`, {
        method: 'PUT',
        body: JSON.stringify(formData)
      })
      message.success('優惠券更新成功')
    } else {
      await apiRequest('/api/coupons', {
        method: 'POST',
        body: JSON.stringify(formData)
      })
      message.success('優惠券建立成功')
    }
    
    createModalVisible.value = false
    loadCoupons()
    loadStats()
  } catch (error) {
    message.error(`操作失敗：${error.message}`)
  }
}

const handleBatchCreate = async () => {
  try {
    const data = await apiRequest('/api/coupons/batch', {
      method: 'POST',
      body: JSON.stringify({
        base_coupon: {
          ...couponForm,
          valid_from: couponForm.valid_from.toISOString(),
          valid_to: couponForm.valid_to.toISOString()
        },
        ...batchForm
      })
    })
    
    message.success(`批次建立完成：成功 ${data.success_count} 筆`)
    if (data.errors.length > 0) {
      console.warn('建立錯誤:', data.errors)
    }
    
    batchCreateModalVisible.value = false
    loadCoupons()
    loadStats()
  } catch (error) {
    message.error(`批次建立失敗：${error.message}`)
  }
}

const handleDistribute = async () => {
  try {
    await apiRequest(`/api/coupons/${distributeForm.coupon_id}/distribute/batch`, {
      method: 'POST',
      body: JSON.stringify(distributeForm)
    })
    
    message.success('優惠券分發成功')
    distributeModalVisible.value = false
  } catch (error) {
    message.error(`分發失敗：${error.message}`)
  }
}

const deleteCoupon = async (id) => {
  try {
    await apiRequest(`/api/coupons/${id}`, { method: 'DELETE' })
    message.success('優惠券刪除成功')
    loadCoupons()
    loadStats()
  } catch (error) {
    message.error(`刪除失敗：${error.message}`)
  }
}

// 生命週期
onMounted(() => {
  loadCoupons()
  loadStats()
  loadProducts()
  loadUsers()
})
</script>

<style scoped>
.admin-page {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #262626;
}

.page-description {
  color: #8c8c8c;
  margin: 0;
  font-size: 14px;
}

.stats-section {
  margin-bottom: 24px;
}

.stats-row {
  margin-bottom: 24px;
}

.filter-section {
  margin-bottom: 24px;
}

.content-section {
  margin-bottom: 24px;
}

.ant-table-tbody > tr > td {
  vertical-align: top;
}
</style> 