<template>
  <div class="admin-page">
    <!-- 1. 頁面標題區 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">數據分析</h1>
          <p class="page-description">查看系統數據統計和分析報告</p>
        </div>
        <div class="action-section">
          <a-button @click="refreshData" :loading="loading">
            <template #icon><ReloadOutlined /></template>
            刷新數據
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
              title="總用戶數"
              :value="stats.total_users"
              prefix="👥"
              :value-style="{ color: '#3f8600' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="總商品數"
              :value="stats.total_products"
              prefix="📦"
              :value-style="{ color: '#cf1322' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="總文章數"
              :value="stats.total_posts"
              prefix="📄"
              :value-style="{ color: '#722ed1' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="總訂單數"
              :value="stats.total_orders"
              prefix="🛒"
              :value-style="{ color: '#fa8c16' }"
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
            <a-range-picker 
              v-model:value="dateRange"
              :placeholder="['開始日期', '結束日期']"
              @change="handleDateRangeChange"
              style="width: 100%"
            />
          </a-col>
          <a-col :span="4">
            <a-select
              v-model:value="dataType"
              placeholder="數據類型"
              @change="handleDataTypeChange"
              style="width: 100%"
            >
              <a-select-option value="all">全部數據</a-select-option>
              <a-select-option value="users">用戶數據</a-select-option>
              <a-select-option value="content">內容數據</a-select-option>
              <a-select-option value="sales">銷售數據</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="4">
            <a-select
              v-model:value="timePeriod"
              placeholder="時間週期"
              @change="handleTimePeriodChange"
              style="width: 100%"
            >
              <a-select-option value="7">最近7天</a-select-option>
              <a-select-option value="30">最近30天</a-select-option>
              <a-select-option value="90">最近90天</a-select-option>
              <a-select-option value="365">最近一年</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="6">
            <a-space>
              <a-button @click="applyFilters" type="primary">應用篩選</a-button>
              <a-button @click="resetFilters">重置</a-button>
            </a-space>
          </a-col>
        </a-row>
      </a-card>
    </div>

    <!-- 4. 主要內容區 -->
    <div class="content-section">
      <!-- 熱門內容 -->
      <a-row :gutter="24" style="margin-bottom: 24px;">
        <a-col :span="12">
          <a-card title="📈 熱門商品" :loading="loading" class="content-card">
            <a-table
              :columns="productColumns"
              :data-source="popularProducts"
              :pagination="false"
              size="small"
            />
          </a-card>
        </a-col>
        <a-col :span="12">
          <a-card title="📊 熱門文章" :loading="loading" class="content-card">
            <a-table
              :columns="postColumns"
              :data-source="popularPosts"
              :pagination="false"
              size="small"
            />
          </a-card>
        </a-col>
      </a-row>

      <!-- 最近活動 -->
      <a-row :gutter="24">
        <a-col :span="24">
          <a-card title="🕒 最近活動" :loading="loading" class="content-card">
            <a-table
              :columns="activityColumns"
              :data-source="recentActivities"
              :pagination="{ pageSize: 10 }"
              size="small"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'type'">
                  <a-tag :color="getActivityColor(record.type)" size="default">
                    <template #icon>
                      <span>{{ getActivityIcon(record.type) }}</span>
                    </template>
                    {{ getActivityLabel(record.type) }}
                  </a-tag>
                </template>
              </template>
            </a-table>
          </a-card>
        </a-col>
      </a-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import axios from '../utils/axios'

// 響應式數據
const loading = ref(false)
const stats = reactive({
  total_users: 0,
  total_products: 0,
  total_posts: 0,
  total_orders: 0
})

// 篩選相關的響應式數據
const dateRange = ref()
const dataType = ref('all')
const timePeriod = ref('30')

const popularProducts = ref([])
const popularPosts = ref([])
const recentActivities = ref([])

// 篩選處理函數
const handleDateRangeChange = (dates) => {
  if (dates && dates.length === 2) {
    // 自動應用篩選
    refreshData()
  }
}

const handleDataTypeChange = () => {
  refreshData()
}

const handleTimePeriodChange = () => {
  refreshData()
}

const applyFilters = () => {
  refreshData()
}

const resetFilters = () => {
  dateRange.value = undefined
  dataType.value = 'all'
  timePeriod.value = '30'
  refreshData()
}

// 表格欄位定義
const productColumns = [
  { title: '商品名稱', dataIndex: 'name', key: 'name' },
  { title: '查看次數', dataIndex: 'view_count', key: 'view_count', width: 100 },
  { title: '銷售量', dataIndex: 'sales_count', key: 'sales_count', width: 80 }
]

const postColumns = [
  { title: '文章標題', dataIndex: 'title', key: 'title' },
  { title: '查看次數', dataIndex: 'view_count', key: 'view_count', width: 100 },
  { title: '發布日期', dataIndex: 'created_at', key: 'created_at', width: 120 }
]

const activityColumns = [
  { title: '類型', dataIndex: 'type', key: 'type', width: 100 },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '時間', dataIndex: 'timestamp', key: 'timestamp', width: 180 }
]

// 活動類型相關函數
const getActivityColor = (type) => {
  const colors = {
    user: 'blue',
    product: 'green',
    order: 'orange',
    post: 'purple',
    system: 'gray'
  }
  return colors[type] || 'default'
}

const getActivityIcon = (type) => {
  const icons = {
    user: '👤',
    product: '📦',
    order: '🛒',
    post: '📄',
    system: '⚙️'
  }
  return icons[type] || '📋'
}

const getActivityLabel = (type) => {
  const labels = {
    user: '用戶',
    product: '商品',
    order: '訂單',
    post: '文章',
    system: '系統'
  }
  return labels[type] || type
}

// 數據載入函數
const refreshData = async () => {
  loading.value = true
  try {
    // 載入統計數據
    const quickStatsResponse = await axios.get('/api/admin/quick-stats')
    Object.assign(stats, quickStatsResponse.data)

    // 載入熱門商品
    const productsResponse = await axios.get('/api/analytics/popular-products')
    popularProducts.value = productsResponse.data

    // 載入熱門文章
    const postsResponse = await axios.get('/api/analytics/popular-posts')
    popularPosts.value = postsResponse.data

    // 載入最近活動
    const activitiesResponse = await axios.get('/api/admin/recent-activity')
    recentActivities.value = activitiesResponse.data

    message.success('數據載入成功')
  } catch (error) {
    console.error('載入數據失敗:', error)
    message.error('載入數據失敗')
  } finally {
    loading.value = false
  }
}

// 生命週期
onMounted(() => {
  refreshData()
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

/* 統計卡片樣式 */
:deep(.stats-section .ant-card) {
  border-radius: 8px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px 0 rgba(0, 0, 0, 0.02);
}

/* 篩選卡片樣式 */
.filter-card {
  border-radius: 8px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px 0 rgba(0, 0, 0, 0.02);
}

/* 內容卡片樣式 */
.content-card {
  border-radius: 8px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px 0 rgba(0, 0, 0, 0.02);
}

/* 表格樣式優化 */
:deep(.ant-table-thead > tr > th) {
  background: #fafafa;
  font-weight: 600;
}

:deep(.ant-table-tbody > tr > td) {
  padding: 12px 8px;
}
</style> 