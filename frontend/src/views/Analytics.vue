<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">數據分析</h1>
      <div class="space-x-2">
        <a-select v-model:value="timeRange" style="width: 120px" @change="refreshData">
          <a-select-option value="7">最近7天</a-select-option>
          <a-select-option value="30">最近30天</a-select-option>
          <a-select-option value="90">最近90天</a-select-option>
        </a-select>
        <a-button @click="refreshData">
          <template #icon><ReloadOutlined /></template>
          刷新
        </a-button>
      </div>
    </div>

    <!-- 總覽統計卡片 -->
    <a-row :gutter="16" class="mb-6">
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="總瀏覽量"
            :value="overview.total_views"
            value-style="color: #3f8600"
          />
          <div class="mt-2 text-sm text-gray-500">
            今日: {{ overview.today_views || 0 }}
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="獨立訪客"
            :value="overview.unique_visitors"
            value-style="color: #1890ff"
          />
          <div class="mt-2 text-sm text-gray-500">
            當前在線: {{ overview.active_sessions || 0 }}
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="總銷售額"
            :value="overview.total_revenue"
            prefix="$"
            :precision="2"
            value-style="color: #722ed1"
          />
          <div class="mt-2 text-sm text-gray-500">
            今日: ${{ (overview.today_revenue || 0).toFixed(2) }}
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="訂單數量"
            :value="overview.total_orders"
            value-style="color: #fa8c16"
          />
          <div class="mt-2 text-sm text-gray-500">
            今日: {{ overview.today_orders || 0 }}
          </div>
        </a-card>
      </a-col>
    </a-row>
    
    <!-- 即時數據更新提示 -->
    <div v-if="overview.calculated_at" class="mb-4 text-xs text-gray-400 text-right">
      數據更新時間: {{ new Date(overview.calculated_at).toLocaleString('zh-TW') }}
      <a-button size="small" type="link" @click="refreshData">
        <template #icon><ReloadOutlined /></template>
        立即刷新
      </a-button>
    </div>

    <!-- 趨勢圖表 -->
    <a-row :gutter="16" class="mb-6">
      <a-col :span="24">
        <a-card title="流量趨勢" :loading="chartsLoading">
          <div class="mb-4">
            <a-radio-group v-model:value="chartGranularity" @change="loadTrendChart">
              <a-radio-button value="hour">小時</a-radio-button>
              <a-radio-button value="day">日</a-radio-button>
              <a-radio-button value="month">月</a-radio-button>
            </a-radio-group>
          </div>
          <div ref="trendChartRef" style="width: 100%; height: 400px;"></div>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="16" class="mb-6">
      <!-- 熱門內容 -->
      <a-col :span="12">
        <a-card title="熱門文章" :loading="loading">
          <a-list
            :data-source="topPosts"
            size="small"
            item-layout="horizontal"
          >
            <template #renderItem="{ item, index }">
              <a-list-item>
                <a-list-item-meta>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: getRankColor(index) }">{{ index + 1 }}</a-avatar>
                  </template>
                  <template #title>
                    <a href="#">{{ item.title }}</a>
                  </template>
                  <template #description>
                    <a-space>
                      <span><EyeOutlined /> {{ item.views }}</span>
                      <span><UserOutlined /> {{ item.unique_views }}</span>
                    </a-space>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>

      <!-- 熱門商品 -->
      <a-col :span="12">
        <a-card title="熱門商品" :loading="loading">
          <a-list
            :data-source="topProducts"
            size="small"
            item-layout="horizontal"
          >
            <template #renderItem="{ item, index }">
              <a-list-item>
                <a-list-item-meta>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: getRankColor(index) }">{{ index + 1 }}</a-avatar>
                  </template>
                  <template #title>
                    <a href="#">{{ item.title }}</a>
                  </template>
                  <template #description>
                    <a-space>
                      <span><EyeOutlined /> {{ item.views }}</span>
                      <span><UserOutlined /> {{ item.unique_views }}</span>
                    </a-space>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
    </a-row>

    <!-- 詳細分析表格 -->
    <a-row :gutter="16" class="mb-6">
      <a-col :span="24">
        <a-card>
          <template #title>
            <a-space>
              <span>內容統計</span>
              <a-select v-model:value="contentType" style="width: 120px" @change="loadContentStats">
                <a-select-option value="">全部</a-select-option>
                <a-select-option value="blog">文章</a-select-option>
                <a-select-option value="product">商品</a-select-option>
              </a-select>
            </a-space>
          </template>
          
          <a-table
            :columns="contentColumns"
            :data-source="contentStats"
            :pagination="contentPagination"
            :loading="loading"
            row-key="content_id"
            @change="handleContentTableChange"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'title'">
                <div class="flex items-center space-x-2">
                  <a-tag :color="record.content_type === 'blog' ? 'blue' : 'green'">
                    {{ record.content_type === 'blog' ? '文章' : '商品' }}
                  </a-tag>
                  <span>{{ record.title }}</span>
                </div>
              </template>
              <template v-if="column.key === 'category'">
                <a-tag v-if="record.category">{{ record.category }}</a-tag>
                <span v-else class="text-gray-400">無分類</span>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>

    <!-- 瀏覽器與設備統計 -->
    <a-row :gutter="16">
      <a-col :span="12">
        <a-card title="瀏覽器統計" :loading="loading">
          <div ref="browserChartRef" style="width: 100%; height: 300px;"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="設備類型統計" :loading="loading">
          <div ref="deviceChartRef" style="width: 100%; height: 300px;"></div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import { 
  ReloadOutlined, 
  EyeOutlined, 
  UserOutlined, 
  ShoppingCartOutlined 
} from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const chartsLoading = ref(false)
const timeRange = ref('30')
const chartGranularity = ref('day')
const contentType = ref('')

// 圖表引用
const trendChartRef = ref()
const browserChartRef = ref()
const deviceChartRef = ref()

// 數據
const overview = ref({
  total_views: 0,
  unique_visitors: 0,
  total_revenue: 0,
  total_orders: 0
})

const topPosts = ref([])
const topProducts = ref([])
const contentStats = ref([])

// 內容統計分頁
const contentPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 項，共 ${total} 項`
})

// 內容統計表格列
const contentColumns = [
  {
    title: '內容',
    key: 'title',
    dataIndex: 'title',
    width: 300
  },
  {
    title: '分類',
    key: 'category',
    dataIndex: 'category',
    width: 120
  },
  {
    title: '總瀏覽量',
    dataIndex: 'total_views',
    sorter: true,
    width: 120
  },
  {
    title: '獨立瀏覽',
    dataIndex: 'unique_views',
    sorter: true,
    width: 120
  },
  {
    title: '今日瀏覽',
    dataIndex: 'today_views',
    sorter: true,
    width: 120
  },
  {
    title: '發布時間',
    dataIndex: 'published_at',
    width: 150,
    customRender: ({ text }) => formatDate(text)
  }
]

// 方法
const loadOverview = async () => {
  try {
    const response = await fetch(`/api/analytics/overview?days=${timeRange.value}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!response.ok) {
      throw new Error('獲取總覽數據失敗')
    }

    const data = await response.json()
    
    // 更新總覽數據，使用即時計算的數值
    overview.value = {
      total_views: data.total_views || 0,
      unique_visitors: data.unique_visitors || 0,
      total_revenue: data.total_revenue || 0,
      total_orders: data.total_orders || 0,
      today_views: data.today_views || 0,
      today_orders: data.today_orders || 0,
      today_revenue: data.today_revenue || 0,
      active_sessions: data.active_sessions || 0,
      calculated_at: data.calculated_at
    }

  } catch (error) {
    console.error('獲取總覽數據失敗:', error)
    message.error('無法獲取總覽數據，請檢查網路連線或聯繫管理員')
    // 設置空數據而不是模擬數據
    overview.value = {
      total_views: 0,
      unique_visitors: 0,
      total_revenue: 0,
      total_orders: 0,
      today_views: 0,
      today_orders: 0,
      today_revenue: 0,
      active_sessions: 0
    }
  }
}

const loadTrendChart = async () => {
  chartsLoading.value = true
  try {
    const response = await fetch(`/api/analytics/trend/time-series?granularity=${chartGranularity.value}&days=${timeRange.value}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!response.ok) {
      throw new Error('獲取趨勢數據失敗')
    }

    const apiData = await response.json()
    
    // 轉換後端數據格式為前端期望的格式
    const labels = apiData.trend_data.map(item => {
      const date = new Date(item.date)
      if (chartGranularity.value === 'hour') {
        return date.toLocaleString('zh-TW', { month: 'short', day: 'numeric', hour: '2-digit' })
      } else if (chartGranularity.value === 'month') {
        return date.toLocaleString('zh-TW', { year: 'numeric', month: 'short' })
      } else {
        return date.toLocaleDateString('zh-TW', { month: 'short', day: 'numeric' })
      }
    })
    
    const blogData = apiData.trend_data.map(item => item.blog_views || 0)
    const productData = apiData.trend_data.map(item => item.product_views || 0)
    
    const chartData = {
      labels: labels,
      datasets: [
        {
          label: '部落格文章',
          data: blogData,
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)'
        },
        {
          label: '商品頁面',
          data: productData,
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)'
        }
      ]
    }
    
    renderTrendChart(chartData)

  } catch (error) {
    console.error('獲取趨勢數據失敗:', error)
    message.error('無法獲取趨勢數據，請檢查網路連線或聯繫管理員')
    // 顯示空圖表
    renderTrendChart({
      labels: [],
      datasets: [
        {
          label: '部落格文章',
          data: [],
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)'
        },
        {
          label: '商品頁面',
          data: [],
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)'
        }
      ]
    })
  } finally {
    chartsLoading.value = false
  }
}

const loadTopContent = async () => {
  try {
    // 載入熱門文章
    const postsResponse = await fetch(`/api/analytics/top-content?content_type=blog&days=${timeRange.value}&limit=5`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (postsResponse.ok) {
      const postsData = await postsResponse.json()
      topPosts.value = postsData
    } else {
      console.error('獲取熱門文章失敗')
      topPosts.value = []
    }

    // 載入熱門商品
    const productsResponse = await fetch(`/api/analytics/top-content?content_type=product&days=${timeRange.value}&limit=5`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (productsResponse.ok) {
      const productsData = await productsResponse.json()
      topProducts.value = productsData
    } else {
      console.error('獲取熱門商品失敗')
      topProducts.value = []
    }

  } catch (error) {
    console.error('獲取熱門內容失敗:', error)
    message.error('無法獲取熱門內容數據，請檢查網路連線或聯繫管理員')
    topPosts.value = []
    topProducts.value = []
  }
}

const loadContentStats = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      days: timeRange.value,
      limit: contentPagination.pageSize.toString(),
      offset: ((contentPagination.current - 1) * contentPagination.pageSize).toString()
    })

    if (contentType.value) {
      params.append('content_type', contentType.value)
    }

    const response = await fetch(`/api/analytics/content-stats?${params}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!response.ok) {
      throw new Error('獲取內容統計失敗')
    }

    const data = await response.json()
    contentStats.value = data.content_stats || []
    contentPagination.total = data.total_count || 0

  } catch (error) {
    console.error('獲取內容統計失敗:', error)
    message.error('無法獲取內容統計數據，請檢查網路連線或聯繫管理員')
    contentStats.value = []
    contentPagination.total = 0
  } finally {
    loading.value = false
  }
}

const loadDeviceStats = async () => {
  try {
    const response = await fetch(`/api/analytics/device-stats?days=${timeRange.value}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!response.ok) {
      throw new Error('獲取設備統計失敗')
    }

    const data = await response.json()
    renderDeviceCharts(data)

  } catch (error) {
    console.error('獲取設備統計失敗:', error)
    message.error('無法獲取設備統計數據，請檢查網路連線或聯繫管理員')
    // 顯示空設備統計而不是模擬數據
    renderDeviceCharts({
      browsers: [],
      devices: [],
      operating_systems: []
    })
  }
}

// 圖表渲染 - 簡化版本，使用 CSS 圖表
const renderTrendChart = (data) => {
  nextTick(() => {
    if (trendChartRef.value) {
      const blogData = data.datasets[0]?.data || []
      const productData = data.datasets[1]?.data || []
      const labels = data.labels || []
      
      // 處理空數據情況
      if (labels.length === 0 || (blogData.length === 0 && productData.length === 0)) {
        trendChartRef.value.innerHTML = `
          <div class="flex items-center justify-center h-80 text-gray-500">
            <div class="text-center">
              <div class="text-xl mb-2">📊</div>
              <div>暫無數據</div>
              <div class="text-sm">請選擇其他時間範圍或等待數據生成</div>
            </div>
          </div>
        `
        return
      }
      
      // 找出最大值用於縮放，防止 -Infinity
      const allValues = [...blogData, ...productData].filter(v => v != null && isFinite(v))
      const maxValue = allValues.length > 0 ? Math.max(...allValues) : 1
      
      trendChartRef.value.innerHTML = `
        <div class="p-4">
          <div class="flex justify-center space-x-8 mb-4">
            <div class="flex items-center">
              <div class="w-4 h-4 bg-blue-500 mr-2 rounded"></div>
              <span class="text-sm">部落格文章</span>
            </div>
            <div class="flex items-center">
              <div class="w-4 h-4 bg-green-500 mr-2 rounded"></div>
              <span class="text-sm">商品頁面</span>
            </div>
          </div>
          <div class="relative" style="height: 300px;">
            <svg width="100%" height="100%" viewBox="0 0 800 280" class="border rounded">
              <!-- 網格線 -->
              <defs>
                <pattern id="grid" width="80" height="56" patternUnits="userSpaceOnUse">
                  <path d="M 80 0 L 0 0 0 56" fill="none" stroke="#f0f0f0" stroke-width="1"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
              
              <!-- Y軸標籤 -->
              <g fill="#666" font-size="12" text-anchor="end">
                <text x="35" y="35">${maxValue}</text>
                <text x="35" y="95">${Math.round(maxValue * 0.75)}</text>
                <text x="35" y="155">${Math.round(maxValue * 0.5)}</text>
                <text x="35" y="215">${Math.round(maxValue * 0.25)}</text>
                <text x="35" y="275">0</text>
              </g>
              
              <!-- 部落格趨勢線 -->
              <polyline
                fill="none"
                stroke="#3B82F6"
                stroke-width="3"
                points="${blogData.map((value, index) => {
                  const x = 50 + (index * (700 / (blogData.length - 1)))
                  const y = 260 - (value / maxValue) * 240
                  return `${x},${y}`
                }).join(' ')}"
              />
              
              <!-- 商品趨勢線 -->
              <polyline
                fill="none"
                stroke="#10B981"
                stroke-width="3"
                points="${productData.map((value, index) => {
                  const x = 50 + (index * (700 / (productData.length - 1)))
                  const y = 260 - (value / maxValue) * 240
                  return `${x},${y}`
                }).join(' ')}"
              />
              
              <!-- 數據點 -->
              ${blogData.map((value, index) => {
                const x = 50 + (index * (700 / (blogData.length - 1)))
                const y = 260 - (value / maxValue) * 240
                return `<circle cx="${x}" cy="${y}" r="4" fill="#3B82F6" stroke="white" stroke-width="2"/>`
              }).join('')}
              
              ${productData.map((value, index) => {
                const x = 50 + (index * (700 / (productData.length - 1)))
                const y = 260 - (value / maxValue) * 240
                return `<circle cx="${x}" cy="${y}" r="4" fill="#10B981" stroke="white" stroke-width="2"/>`
              }).join('')}
              
              <!-- X軸標籤 -->
              <g fill="#666" font-size="11" text-anchor="middle">
                ${labels.map((label, index) => {
                  if (index % 3 === 0) { // 只顯示每3個標籤
                    const x = 50 + (index * (700 / (labels.length - 1)))
                    return `<text x="${x}" y="295">${label}</text>`
                  }
                  return ''
                }).join('')}
              </g>
            </svg>
          </div>
        </div>
      `
    }
  })
}

const renderDeviceCharts = (data) => {
  nextTick(() => {
    if (browserChartRef.value) {
      const browserData = data.browsers || [
        { value: 35, name: 'Chrome' },
        { value: 25, name: 'Safari' },
        { value: 20, name: 'Firefox' },
        { value: 15, name: 'Edge' },
        { value: 5, name: '其他' }
      ]
      
      const colors = ['#4285F4', '#34A853', '#FF6B35', '#0078D4', '#9CA3AF']
      
      browserChartRef.value.innerHTML = `
        <div class="p-4">
          ${browserData.map((item, index) => `
            <div class="mb-3">
              <div class="flex justify-between items-center mb-1">
                <div class="flex items-center">
                  <div class="w-3 h-3 rounded mr-2" style="background-color: ${colors[index]}"></div>
                  <span>${item.name}</span>
                </div>
                <span class="font-medium">${item.value}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="h-2 rounded-full" style="width: ${item.value}%; background-color: ${colors[index]}"></div>
              </div>
            </div>
          `).join('')}
        </div>
      `
    }

    if (deviceChartRef.value) {
      const deviceData = data.devices || [
        { value: 60, name: '桌面' },
        { value: 35, name: '手機' },
        { value: 5, name: '平板' }
      ]
      
      const colors = ['#3B82F6', '#10B981', '#F59E0B']
      const total = deviceData.reduce((sum, item) => sum + item.value, 0)
      let currentAngle = 0
      
      deviceChartRef.value.innerHTML = `
        <div class="p-4">
          <div class="flex justify-center mb-4">
            <svg width="200" height="200" viewBox="0 0 200 200">
              <!-- 圓餅圖 -->
              ${deviceData.map((item, index) => {
                const angle = (item.value / total) * 360
                const startAngle = currentAngle
                currentAngle += angle
                
                const startAngleRad = (startAngle * Math.PI) / 180
                const endAngleRad = (currentAngle * Math.PI) / 180
                
                const x1 = 100 + 80 * Math.cos(startAngleRad)
                const y1 = 100 + 80 * Math.sin(startAngleRad)
                const x2 = 100 + 80 * Math.cos(endAngleRad)
                const y2 = 100 + 80 * Math.sin(endAngleRad)
                
                const largeArcFlag = angle > 180 ? 1 : 0
                
                return `
                  <path
                    d="M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArcFlag} 1 ${x2} ${y2} Z"
                    fill="${colors[index]}"
                    stroke="white"
                    stroke-width="2"
                  />
                `
              }).join('')}
              
              <!-- 中心圓 -->
              <circle cx="100" cy="100" r="30" fill="white" stroke="#e5e7eb" stroke-width="2"/>
              <text x="100" y="105" text-anchor="middle" font-size="14" font-weight="bold" fill="#374151">總計</text>
            </svg>
          </div>
          
          <!-- 圖例 -->
          <div class="space-y-2">
            ${deviceData.map((item, index) => `
              <div class="flex justify-between items-center">
                <div class="flex items-center">
                  <div class="w-3 h-3 rounded mr-2" style="background-color: ${colors[index]}"></div>
                  <span>${item.name}</span>
                </div>
                <span class="font-medium">${item.value}%</span>
              </div>
            `).join('')}
          </div>
        </div>
      `
    }
  })
}

// 事件處理
const handleContentTableChange = (pagination, filters, sorter) => {
  contentPagination.current = pagination.current
  contentPagination.pageSize = pagination.pageSize
  loadContentStats()
}

const refreshData = () => {
  loadOverview()
  loadTrendChart()
  loadTopContent()
  loadContentStats()
  loadDeviceStats()
}

// 輔助函數
const getRankColor = (index) => {
  const colors = ['#f56565', '#ed8936', '#ecc94b', '#48bb78', '#4299e1']
  return colors[index] || '#9f7aea'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-TW')
}

// 初始化
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.ant-statistic-content {
  font-size: 16px;
}

.ant-card-head-title {
  padding: 12px 0;
}
</style> 