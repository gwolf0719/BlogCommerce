<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">訂單管理</h1>
      <div class="space-x-2">
        <a-button @click="refreshOrders">
          <template #icon><ReloadOutlined /></template>
          刷新
        </a-button>
      </div>
    </div>

    <!-- 搜尋與篩選 -->
    <a-card class="mb-6">
      <a-row :gutter="16">
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

    <!-- 統計卡片 -->
    <a-row :gutter="16" class="mb-6">
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="總訂單數"
            :value="stats.total_orders"
            prefix-icon="OrderedListOutlined"
            value-style="color: #3f8600"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="待處理"
            :value="stats.processing_orders"
            prefix-icon="ClockCircleOutlined"
            value-style="color: #cf1322"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="今日訂單"
            :value="stats.today_orders"
            prefix-icon="CalendarOutlined"
            value-style="color: #1890ff"
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
            value-style="color: #3f8600"
          />
        </a-card>
      </a-col>
    </a-row>

    <!-- 訂單列表 -->
    <a-card>
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

          <template v-if="column.key === 'items_count'">
            <a-tag>{{ record.items?.length || 0 }} 件商品</a-tag>
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
          <a-descriptions-item label="建立時間">{{ formatDate(selectedOrder.created_at) }}</a-descriptions-item>
          <a-descriptions-item label="備註" :span="2">{{ selectedOrder.notes || '無' }}</a-descriptions-item>
        </a-descriptions>

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
                <img :src="record.product?.featured_image || '/static/images/placeholder-product.jpg'" class="w-12 h-12 object-cover rounded" />
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

    const response = await fetch(`/api/admin/orders?${params}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!response.ok) {
      throw new Error('獲取訂單列表失敗')
    }

    const data = await response.json()
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
    const response = await fetch('/api/orders/stats/overview', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!response.ok) {
      throw new Error('獲取統計資料失敗')
    }

    const data = await response.json()
    stats.value = data

  } catch (error) {
    console.error('獲取統計資料失敗:', error)
  }
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

const handleTableChange = (pag, filters, sorter) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchOrders()
}

const refreshOrders = () => {
  fetchOrders()
  fetchStats()
}

const viewOrderDetail = async (order) => {
  try {
    const response = await fetch(`/api/admin/orders/${order.id}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!response.ok) {
      throw new Error('獲取訂單詳情失敗')
    }

    const data = await response.json()
    selectedOrder.value = data
    updateStatus.value = data.status
    detailModalVisible.value = true

  } catch (error) {
    message.error(error.message || '獲取訂單詳情失敗')
  }
}

const updateOrderStatus = async () => {
  if (!updateStatus.value) {
    message.warning('請選擇狀態')
    return
  }

  updateLoading.value = true
  try {
    const response = await fetch(`/api/admin/orders/${selectedOrder.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        status: updateStatus.value
      })
    })

    if (!response.ok) {
      throw new Error('更新訂單狀態失敗')
    }

    message.success('訂單狀態已更新')
    selectedOrder.value.status = updateStatus.value
    detailModalVisible.value = false
    refreshOrders()

  } catch (error) {
    message.error(error.message || '更新訂單狀態失敗')
  } finally {
    updateLoading.value = false
  }
}

const handleStatusChange = async ({ key }, order) => {
  try {
    const response = await fetch(`/api/admin/orders/${order.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        status: key
      })
    })

    if (!response.ok) {
      throw new Error('更新訂單狀態失敗')
    }

    message.success('訂單狀態已更新')
    refreshOrders()

  } catch (error) {
    message.error(error.message || '更新訂單狀態失敗')
  }
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
.ant-statistic-content {
  font-size: 16px;
}
</style> 