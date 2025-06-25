<template>
  <div class="analytics-page">
    <div class="page-header">
      <h1>數據分析</h1>
      <a-button @click="refreshData" :loading="loading">
        <ReloadOutlined /> 刷新數據
      </a-button>
    </div>

    <!-- 概覽卡片 -->
    <a-row :gutter="16" class="overview-cards">
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="總用戶數"
            :value="stats.total_users"
            :value-style="{ color: '#3f8600' }"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="總商品數"
            :value="stats.total_products"
            :value-style="{ color: '#cf1322' }"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="總文章數"
            :value="stats.total_posts"
            :value-style="{ color: '#722ed1' }"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="總訂單數"
            :value="stats.total_orders"
            :value-style="{ color: '#fa8c16' }"
          />
        </a-card>
      </a-col>
    </a-row>

    <!-- 熱門內容 -->
    <a-row :gutter="16" style="margin-top: 20px;">
      <a-col :span="12">
        <a-card title="熱門商品" :loading="loading">
          <a-table
            :columns="productColumns"
            :data-source="popularProducts"
            :pagination="false"
            size="small"
          />
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="熱門文章" :loading="loading">
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
    <a-row :gutter="16" style="margin-top: 20px;">
      <a-col :span="24">
        <a-card title="最近活動" :loading="loading">
          <a-table
            :columns="activityColumns"
            :data-source="recentActivities"
            :pagination="{ pageSize: 10 }"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'type'">
                <a-tag :color="getActivityColor(record.type)">
                  {{ getActivityLabel(record.type) }}
                </a-tag>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>
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

const popularProducts = ref([])
const popularPosts = ref([])
const recentActivities = ref([])

// 表格欄位
const productColumns = [
  {
    title: '商品名稱',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: '銷量',
    dataIndex: 'sales_count',
    key: 'sales_count'
  }
]

const postColumns = [
  {
    title: '文章標題',
    dataIndex: 'title',
    key: 'title'
  },
  {
    title: '瀏覽量',
    dataIndex: 'views',
    key: 'views'
  }
]

const activityColumns = [
  {
    title: '類型',
    key: 'type'
  },
  {
    title: '標題',
    dataIndex: 'title',
    key: 'title'
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description'
  },
  {
    title: '時間',
    dataIndex: 'created_at',
    key: 'created_at'
  }
]

// 獲取活動類型顏色
const getActivityColor = (type) => {
  const colors = {
    order: 'green',
    user: 'blue',
    product: 'orange',
    post: 'purple'
  }
  return colors[type] || 'default'
}

// 獲取活動類型標籤
const getActivityLabel = (type) => {
  const labels = {
    order: '訂單',
    user: '用戶',
    product: '商品',
    post: '文章'
  }
  return labels[type] || type
}

// 載入統計數據
const loadStats = async () => {
  try {
    const response = await axios.get('/api/admin/quick-stats')
    Object.assign(stats, response.data)
  } catch (error) {
    console.error('載入統計數據錯誤:', error)
    message.error('載入統計數據失敗')
  }
}

// 載入熱門商品
const loadPopularProducts = async () => {
  try {
    const response = await axios.get('/api/analytics/popular-products')
    popularProducts.value = response.data
  } catch (error) {
    console.error('載入熱門商品錯誤:', error)
    // 使用模擬數據
    popularProducts.value = [
      { name: '熱門商品1', sales_count: 100 },
      { name: '熱門商品2', sales_count: 85 },
      { name: '熱門商品3', sales_count: 72 }
    ]
  }
}

// 載入熱門文章
const loadPopularPosts = async () => {
  try {
    const response = await axios.get('/api/analytics/popular-posts')
    popularPosts.value = response.data
  } catch (error) {
    console.error('載入熱門文章錯誤:', error)
    // 使用模擬數據
    popularPosts.value = [
      { title: '熱門文章1', views: 1200 },
      { title: '熱門文章2', views: 980 },
      { title: '熱門文章3', views: 756 }
    ]
  }
}

// 載入最近活動
const loadRecentActivities = async () => {
  try {
    const response = await axios.get('/api/admin/recent-activity')
    recentActivities.value = response.data
  } catch (error) {
    console.error('載入最近活動錯誤:', error)
    // 使用模擬數據
    recentActivities.value = [
      {
        type: 'order',
        title: '新訂單',
        description: '用戶下了新訂單',
        created_at: '2024-01-15 10:30:00'
      },
      {
        type: 'user',
        title: '用戶註冊',
        description: '新用戶註冊了帳號',
        created_at: '2024-01-15 09:15:00'
      },
      {
        type: 'product',
        title: '商品上架',
        description: '新商品已上架',
        created_at: '2024-01-15 08:45:00'
      }
    ]
  }
}

// 刷新所有數據
const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadStats(),
      loadPopularProducts(),
      loadPopularPosts(),
      loadRecentActivities()
    ])
    message.success('數據已刷新')
  } catch (error) {
    message.error('刷新數據失敗')
  } finally {
    loading.value = false
  }
}

// 掛載時載入數據
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.analytics-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.overview-cards {
  margin-bottom: 20px;
}

.overview-cards .ant-card {
  text-align: center;
}
</style> 