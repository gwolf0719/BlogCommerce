<template>
  <div class="admin-page">
    <!-- 1. 頁面標題區 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">訂單管理</h1>
          <p class="page-description">管理所有客戶訂單，處理訂單狀態和付款資訊</p>
        </div>
        <div class="action-section">
          <a-button type="primary" @click="refreshOrders">
            <template #icon><ReloadOutlined /></template>
            刷新
          </a-button>
        </div>
      </div>
    </div>

    <!-- 2. 統計卡片區 -->
    <div class="stats-section">
      <a-row :gutter="24" class="stats-row">
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="總訂單數"
              :value="stats.total_orders"
              prefix-icon="OrderedListOutlined"
              :value-style="{ color: '#3f8600' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="待處理"
              :value="stats.processing_orders"
              prefix-icon="ClockCircleOutlined"
              :value-style="{ color: '#cf1322' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="今日訂單"
              :value="stats.today_orders"
              prefix-icon="CalendarOutlined"
              :value-style="{ color: '#1890ff' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="總銷售額"
              :value="stats.total_revenue"
              prefix="$"
              :precision="2"
              :value-style="{ color: '#3f8600' }"
            />
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 3. 搜尋篩選區 -->
    <div class="filter-section">
      <a-card class="filter-card">
        <a-row :gutter="24">
          <a-col :span="6">
            <a-input
              v-model:value="searchForm.search"
              placeholder="搜尋訂單編號 / 會員名稱"
              allowClear
              @change="handleSearch"
            >
              <template #prefix><SearchOutlined /></template>
            </a-input>
          </a-col>
          <a-col :span="6">
            <a-select
              v-model:value="searchForm.status"
              placeholder="狀態篩選"
              allowClear
              @change="handleSearch"
            >
              <a-select-option value="pending">待確認</a-select-option>
              <a-select-option value="confirmed">已確認</a-select-option>
              <a-select-option value="shipped">已出貨</a-select-option>
              <a-select-option value="delivered">已送達</a-select-option>
              <a-select-option value="cancelled">已取消</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="6">
            <a-range-picker 
              v-model:value="searchForm.dateRange"
              :placeholder="['開始日期', '結束日期']"
              @change="handleSearch"
            />
          </a-col>
          <a-col :span="6">
            <a-button @click="resetSearch">重置</a-button>
          </a-col>
        </a-row>
      </a-card>
    </div>

    <!-- 4. 主要內容區 -->
    <div class="content-section">
      <a-card class="content-card">
        <a-table
          :columns="columns"
          :data-source="orders"
          :pagination="paginationConfig"
          :loading="loading"
          row-key="id"
          @change="handleTableChange"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'order_number'">
              <a-button type="link" @click="viewOrderDetail(record)">{{ record.order_number }}</a-button>
            </template>

            <template v-if="column.key === 'customer_info'">
              <div>
                <div class="font-medium">{{ record.customer_name || record.customer_email }}</div>
                <div class="text-gray-500 text-sm">{{ record.customer_phone || record.customer_email }}</div>
              </div>
            </template>

            <template v-if="column.key === 'total_amount'">
              <span class="font-medium">{{ formatCurrency(record.total_amount) }}</span>
            </template>

            <template v-if="column.key === 'status'">
              <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
            </template>

            <template v-if="column.key === 'payment_status'">
              <a-tag :color="getPaymentStatusColor(record.payment_status)">{{ getPaymentStatusText(record.payment_status) }}</a-tag>
            </template>

            <template v-if="column.key === 'payment_method'">
              <span>{{ getPaymentMethodText(record.payment_method) }}</span>
            </template>

            <template v-if="column.key === 'items_count'">
              <a-tag>{{ record.items_count || 0 }} 件商品</a-tag>
            </template>

            <template v-if="column.key === 'created_at'">
              <span>{{ formatDate(record.created_at) }}</span>
            </template>

            <template v-if="column.key === 'action'">
              <a-space>
                <a-button type="link" size="small" @click="viewOrderDetail(record)">
                  <EyeOutlined />
                </a-button>
                <a-dropdown>
                  <template #overlay>
                    <a-menu @click="handleStatusChange($event, record)">
                      <a-menu-item key="confirmed">確認訂單</a-menu-item>
                      <a-menu-item key="shipped">標記為已出貨</a-menu-item>
                      <a-menu-item key="delivered">標記為已送達</a-menu-item>
                      <a-menu-divider />
                      <a-menu-item key="cancelled" class="text-red-600">取消訂單</a-menu-item>
                    </a-menu>
                  </template>
                  <a-button type="link" size="small">
                    更多 <DownOutlined />
                  </a-button>
                </a-dropdown>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>

    <!-- 訂單詳情彈窗 -->
    <a-modal 
      v-model:open="detailModalVisible" 
      title="訂單詳情" 
      width="80%" 
      :footer="null"
    >
      <div v-if="selectedOrder">
        <a-descriptions :column="2" bordered class="mb-4">
          <a-descriptions-item label="訂單編號">{{ selectedOrder.order_number }}</a-descriptions-item>
          <a-descriptions-item label="訂單狀態">
            <a-tag :color="getStatusColor(selectedOrder.status)">{{ getStatusText(selectedOrder.status) }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="客戶姓名">{{ selectedOrder.customer_name }}</a-descriptions-item>
          <a-descriptions-item label="聯絡電話">{{ selectedOrder.customer_phone }}</a-descriptions-item>
          <a-descriptions-item label="客戶信箱">{{ selectedOrder.customer_email }}</a-descriptions-item>
          <a-descriptions-item label="收貨地址">{{ selectedOrder.shipping_address }}</a-descriptions-item>
          <a-descriptions-item label="訂單總額">{{ formatCurrency(selectedOrder.total_amount) }}</a-descriptions-item>
          <a-descriptions-item label="付款方式">{{ getPaymentMethodText(selectedOrder.payment_method) }}</a-descriptions-item>
          <a-descriptions-item label="付款狀態">
            <a-tag :color="getPaymentStatusColor(selectedOrder.payment_status)">{{ getPaymentStatusText(selectedOrder.payment_status) }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="建立時間">{{ formatDate(selectedOrder.created_at) }}</a-descriptions-item>
          <a-descriptions-item label="備註" :span="2">{{ selectedOrder.notes || '無' }}</a-descriptions-item>
        </a-descriptions>

        <!-- 付款狀態管理 -->
        <a-card title="付款狀態管理" class="mb-4">
          <a-form layout="inline">
            <a-form-item label="付款方式">
              <a-select v-model:value="paymentForm.method" style="width: 150px" @change="updatePaymentMethod">
                <a-select-option value="transfer">轉帳</a-select-option>
                <a-select-option value="linepay">Line Pay</a-select-option>
                <a-select-option value="ecpay">綠界</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="付款狀態">
              <a-select v-model:value="paymentForm.status" style="width: 150px" @change="updatePaymentStatus">
                <a-select-option value="unpaid">未付款</a-select-option>
                <a-select-option value="paid">已付款</a-select-option>
                <a-select-option value="failed">付款失敗</a-select-option>
                <a-select-option value="refunded">已退款</a-select-option>
                <a-select-option value="pending">等待確認</a-select-option>
                <a-select-option value="partial">部分付款</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="savePaymentStatus" :loading="savingPayment">儲存</a-button>
            </a-form-item>
          </a-form>
          <div v-if="selectedOrder.payment_info" class="mt-4">
            <h4 class="font-medium mb-2">金流回傳資訊</h4>
            <pre class="bg-gray-100 p-3 rounded text-sm">{{ JSON.stringify(selectedOrder.payment_info, null, 2) }}</pre>
          </div>
        </a-card>

        <!-- 訂單商品列表 -->
        <h3 class="text-lg font-medium mb-3">訂單商品</h3>
        <a-table
          :columns="itemColumns"
          :data-source="selectedOrder.items || []"
          :pagination="false"
          row-key="id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'product'">
              <div class="flex items-center space-x-3">
                <img :src="record.product?.featured_image || '/static/images/default-product.svg'" class="w-12 h-12 object-cover rounded" />
                <div>
                  <div class="font-medium">{{ record.product_name || record.product?.name }}</div>
                  <div class="text-gray-500 text-sm">SKU: {{ record.product?.sku || 'N/A' }}</div>
                </div>
              </div>
            </template>
            <template v-if="column.key === 'unit_price'">
              {{ formatCurrency(record.unit_price) }}
            </template>
            <template v-if="column.key === 'subtotal'">
              {{ formatCurrency(record.unit_price * record.quantity) }}
            </template>
          </template>
        </a-table>

        <!-- 狀態更新區域 -->
        <div class="mt-4 p-4 bg-gray-50 rounded">
          <h4 class="text-md font-medium mb-2">更新訂單狀態</h4>
          <a-space>
            <a-select v-model:value="updateStatus" style="width: 150px">
              <a-select-option value="pending">待確認</a-select-option>
              <a-select-option value="confirmed">已確認</a-select-option>
              <a-select-option value="shipped">已出貨</a-select-option>
              <a-select-option value="delivered">已送達</a-select-option>
              <a-select-option value="cancelled">已取消</a-select-option>
            </a-select>
            <a-button type="primary" @click="updateOrderStatus" :loading="updateLoading">
              更新狀態
            </a-button>
          </a-space>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { 
  SearchOutlined, 
  ReloadOutlined, 
  EyeOutlined, 
  DownOutlined,
  OrderedListOutlined,
  ClockCircleOutlined,
  CalendarOutlined
} from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'
import dayjs from 'dayjs'
import { formatDate } from '../utils/dateUtils'

const authStore = useAuthStore()
const loading = ref(false)
const detailModalVisible = ref(false)
const updateLoading = ref(false)

// 數據
const orders = ref([])
const stats = ref({
  total_orders: 0,
  processing_orders: 0,
  today_orders: 0,
  total_revenue: 0
})
const selectedOrder = ref(null)
const updateStatus = ref('')

// 付款狀態管理
const paymentForm = reactive({
  method: '',
  status: ''
})
const savingPayment = ref(false)

// 搜尋表單
const searchForm = reactive({
  search: '',
  status: '',
  dateRange: []
})

// 分頁
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 項，共 ${total} 項`
})

const paginationConfig = computed(() => ({
  current: pagination.current,
  pageSize: pagination.pageSize,
  total: pagination.total,
  showSizeChanger: pagination.showSizeChanger,
  showQuickJumper: pagination.showQuickJumper,
  showTotal: pagination.showTotal
}))

// 表格列定義
const columns = [
  {
    title: '訂單編號',
    dataIndex: 'order_number',
    key: 'order_number',
    width: 160
  },
  {
    title: '客戶資訊',
    key: 'customer_info',
    width: 180
  },
  {
    title: '訂單金額',
    key: 'total_amount',
    dataIndex: 'total_amount',
    width: 120,
    sorter: true
  },
  {
    title: '商品數量',
    key: 'items_count',
    width: 100
  },
  {
    title: '訂單狀態',
    key: 'status',
    dataIndex: 'status',
    width: 100
  },
  {
    title: '付款狀態',
    key: 'payment_status',
    dataIndex: 'payment_status',
    width: 100
  },
  {
    title: '付款方式',
    key: 'payment_method',
    dataIndex: 'payment_method',
    width: 100
  },
  {
    title: '建立時間',
    key: 'created_at',
    dataIndex: 'created_at',
    width: 150,
    sorter: true
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
    fixed: 'right'
  }
]

// 訂單商品列表列定義
const itemColumns = [
  {
    title: '商品',
    key: 'product',
    width: 250
  },
  {
    title: '單價',
    key: 'unit_price',
    dataIndex: 'unit_price',
    width: 100
  },
  {
    title: '數量',
    dataIndex: 'quantity',
    width: 80
  },
  {
    title: '小計',
    key: 'subtotal',
    width: 100
  }
]

// 方法
const fetchOrders = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      skip: ((pagination.current - 1) * pagination.pageSize).toString(),
      limit: pagination.pageSize.toString()
    })

    if (searchForm.search) {
      params.append('search', searchForm.search)
    }
    if (searchForm.status) {
      params.append('status', searchForm.status)
    }
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.append('start_date', dayjs(searchForm.dateRange[0]).format('YYYY-MM-DD'))
      params.append('end_date', dayjs(searchForm.dateRange[1]).format('YYYY-MM-DD'))
    }

    const ordersResponse = await fetch(`/api/orders?${params}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!ordersResponse.ok) {
      throw new Error('獲取訂單列表失敗')
    }

    const data = await ordersResponse.json()
    orders.value = data.items || data
    pagination.total = data.total || data.length

  } catch (error) {
    message.error(error.message || '獲取訂單列表失敗')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const statsResponse = await fetch('/api/orders/stats/overview', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!statsResponse.ok) {
      return // 如果沒有統計 API，則跳過
    }

    const data = await statsResponse.json()
    stats.value = data

  } catch (error) {
    // 靜默處理，如果沒有統計 API
    console.log('統計資料 API 尚未實現')
  }
}

const viewOrderDetail = async (order) => {
  try {
    const detailResponse = await fetch(`/api/orders/${order.id}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!detailResponse.ok) {
      throw new Error('獲取訂單詳情失敗')
    }

    selectedOrder.value = await detailResponse.json()
    paymentForm.method = selectedOrder.value.payment_method || ''
    paymentForm.status = selectedOrder.value.payment_status || ''
    updateStatus.value = selectedOrder.value.status || ''
    detailModalVisible.value = true
  } catch (error) {
    message.error(error.message || '獲取訂單詳情失敗')
  }
}

const handleStatusChange = async (e, order) => {
  try {
    const statusResponse = await fetch(`/api/orders/${order.id}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ status: e.key })
    })

    if (!statusResponse.ok) {
      throw new Error('更新訂單狀態失敗')
    }

    message.success('訂單狀態已更新')
    fetchOrders()
  } catch (error) {
    message.error(error.message || '更新訂單狀態失敗')
  }
}

const savePaymentStatus = async () => {
  savingPayment.value = true
  try {
    const paymentStatusResponse = await fetch(`/api/orders/${selectedOrder.value.id}/payment`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        payment_method: paymentForm.method,
        payment_status: paymentForm.status
      })
    })

    if (!paymentStatusResponse.ok) {
      throw new Error('更新付款狀態失敗')
    }

    message.success('付款狀態已儲存')
    fetchOrders()
    viewOrderDetail(selectedOrder.value) // 重新載入詳情以更新顯示
  } catch (error) {
    message.error(error.message || '更新付款狀態失敗')
  } finally {
    savingPayment.value = false
  }
}

const updateOrderStatus = async () => {
  updateLoading.value = true
  try {
    const updateOrderResponse = await fetch(`/api/orders/${selectedOrder.value.id}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ status: updateStatus.value })
    })

    if (!updateOrderResponse.ok) {
      throw new Error('更新訂單狀態失敗')
    }

    message.success('訂單狀態已更新')
    fetchOrders()
    viewOrderDetail(selectedOrder.value) // 重新載入詳情以更新顯示
  } catch (error) {
    message.error(error.message || '更新訂單狀態失敗')
  } finally {
    updateLoading.value = false
  }
}

const updatePaymentMethod = (value) => {
  paymentForm.method = value
}

const updatePaymentStatus = (value) => {
  paymentForm.status = value
}

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchOrders()
}

const refreshOrders = () => {
  fetchOrders()
  fetchStats()
}

const handleSearch = () => {
  pagination.current = 1
  fetchOrders()
}

const resetSearch = () => {
  searchForm.search = ''
  searchForm.status = ''
  searchForm.dateRange = []
  pagination.current = 1
  fetchOrders()
}

// 輔助函數
const getStatusColor = (status) => {
  const colors = {
    pending: 'orange',
    confirmed: 'blue',
    shipped: 'cyan',
    delivered: 'green',
    cancelled: 'red'
  }
  return colors[status] || 'default'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待確認',
    confirmed: '已確認',
    shipped: '已出貨',
    delivered: '已送達',
    cancelled: '已取消'
  }
  return texts[status] || status
}

const getPaymentStatusColor = (status) => {
  const colors = {
    unpaid: 'orange',
    paid: 'green',
    failed: 'red',
    refunded: 'purple',
    pending: 'blue',
    partial: 'yellow'
  }
  return colors[status] || 'default'
}

const getPaymentStatusText = (status) => {
  const texts = {
    unpaid: '未付款',
    paid: '已付款',
    failed: '付款失敗',
    refunded: '已退款',
    pending: '等待確認',
    partial: '部分付款'
  }
  return texts[status] || status
}

const getPaymentMethodText = (method) => {
  const texts = {
    transfer: '轉帳',
    linepay: 'Line Pay',
    ecpay: '綠界'
  }
  return texts[method] || method
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD'
  }).format(amount || 0)
}

// formatDate 已移至 utils/dateUtils.js

// 初始化
onMounted(() => {
  fetchOrders()
  fetchStats()
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

.ant-statistic-content {
  font-size: 16px;
}
</style> 