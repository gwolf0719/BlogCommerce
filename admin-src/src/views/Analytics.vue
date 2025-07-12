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

      <!-- 推薦碼統計 -->
      <a-card title="推薦碼統計" class="mb-4">
        <div class="row">
          <div class="col-md-3">
            <div class="stat-card">
              <h3>{{ promoStats.totalCodes }}</h3>
              <p>推薦碼總數</p>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card">
              <h3>{{ promoStats.activeCodes }}</h3>
              <p>啟用中</p>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card">
              <h3>{{ promoStats.totalUsage }}</h3>
              <p>總使用次數</p>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card">
              <h3>${{ promoStats.totalSavings.toLocaleString() }}</h3>
              <p>總節省金額</p>
            </div>
          </div>
        </div>
      </a-card>
      
      <!-- 推薦碼趨勢分析 -->
      <a-card title="推薦碼趨勢分析" class="mb-4">
        <div class="row">
          <div class="col-md-6">
            <h4>推薦碼使用趨勢</h4>
            <canvas ref="promoUsageChart" width="400" height="200"></canvas>
          </div>
          <div class="col-md-6">
            <h4>推薦碼類型分佈</h4>
            <canvas ref="promoTypeChart" width="400" height="200"></canvas>
          </div>
        </div>
      </a-card>
      
      <!-- 推薦碼效益分析 -->
      <a-card title="推薦碼效益分析" class="mb-4">
        <div class="row">
          <div class="col-md-4">
            <div class="stat-card">
              <h3>${{ promoStats.avgDiscountAmount.toLocaleString() }}</h3>
              <p>平均折扣金額</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="stat-card">
              <h3>{{ promoStats.usageRate }}%</h3>
              <p>使用率</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="stat-card">
              <h3>${{ promoStats.totalSavings.toLocaleString() }}</h3>
              <p>節省總額</p>
            </div>
          </div>
        </div>
      </a-card>
      
      <!-- 熱門推薦碼排行 -->
      <a-card title="熱門推薦碼排行" class="mb-4">
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>排名</th>
                <th>推薦碼</th>
                <th>專案名稱</th>
                <th>使用次數</th>
                <th>節省金額</th>
                <th>使用率</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(code, index) in topPromoCodes" :key="code.id">
                <td>{{ index + 1 }}</td>
                <td>{{ code.code }}</td>
                <td>{{ code.name }}</td>
                <td>{{ code.usageCount }}</td>
                <td>${{ code.savingsAmount.toLocaleString() }}</td>
                <td>{{ code.usageRate }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </a-card>
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
      <!-- 折扣碼報表 -->
      <a-row :gutter="24" style="margin-bottom: 24px;">
        <a-col :span="12">
          <a-card title="🎟️ 熱門折扣碼" :loading="loading" class="content-card">
            <a-table
              :columns="discountCodeColumns"
              :data-source="popularDiscountCodes"
              :pagination="false"
              size="small"
            />
          </a-card>
        </a-col>
        <a-col :span="12">
          <a-card title="📊 折扣碼使用趨勢" :loading="loading" class="content-card">
            <div class="chart-container">
              <canvas ref="discountTrendChart" width="400" height="200"></canvas>
            </div>
          </a-card>
        </a-col>
      </a-row>

      <!-- 折扣碼分析 -->
      <a-row :gutter="24" style="margin-bottom: 24px;">
        <a-col :span="8">
          <a-card title="🎯 折扣碼類型分佈" :loading="loading" class="content-card">
            <div class="chart-container">
              <canvas ref="discountTypeChart" width="250" height="200"></canvas>
            </div>
          </a-card>
        </a-col>
        <a-col :span="8">
          <a-card title="💰 折扣碼效益分析" :loading="loading" class="content-card">
            <div class="benefit-analysis">
              <div class="benefit-item">
                <span class="benefit-label">平均折扣金額</span>
                <span class="benefit-value">${{ averageDiscountAmount.toFixed(2) }}</span>
              </div>
              <div class="benefit-item">
                <span class="benefit-label">使用率</span>
                <span class="benefit-value">{{ discountUsageRate.toFixed(1) }}%</span>
              </div>
              <div class="benefit-item">
                <span class="benefit-label">節省總額</span>
                <span class="benefit-value">${{ stats.total_discount_amount.toFixed(2) }}</span>
              </div>
            </div>
          </a-card>
        </a-col>
        <a-col :span="8">
          <a-card title="📈 折扣碼表現排名" :loading="loading" class="content-card">
            <div class="ranking-list">
              <div 
                v-for="(item, index) in discountCodeRanking" 
                :key="item.code"
                class="ranking-item"
              >
                <div class="ranking-number">{{ index + 1 }}</div>
                <div class="ranking-info">
                  <div class="ranking-code">{{ item.code }}</div>
                  <div class="ranking-stats">{{ item.used_count }} 次使用</div>
                </div>
                <div class="ranking-amount">${{ item.total_amount.toFixed(2) }}</div>
              </div>
            </div>
          </a-card>
        </a-col>
      </a-row>

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
  total_orders: 0,
  total_discount_codes: 0,
  active_discount_codes: 0,
  total_discount_usage: 0,
  today_discount_usage: 0,
  total_discount_amount: 0,
  discount_conversion_rate: 0
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

    // 載入折扣碼統計
    await loadDiscountCodeStats()
    // 載入折扣碼排名
    await loadDiscountCodeRanking()

    message.success('數據載入成功')
  } catch (error) {
    console.error('載入數據失敗:', error)
    message.error('載入數據失敗')
  } finally {
    loading.value = false
  }
}

// 折扣碼轉換率計算
const discountConversionRate = ref(0)

// 折扣碼相關資料
const popularDiscountCodes = ref([])
const discountCodeRanking = ref([])
const averageDiscountAmount = ref(0)
const discountUsageRate = ref(0)
const discountTrendChart = ref(null)
const discountTypeChart = ref(null)

// 表格欄位定義
const discountCodeColumns = [
  { title: '折扣碼', dataIndex: 'code', key: 'code' },
  { title: '使用次數', dataIndex: 'used_count', key: 'used_count' },
  { title: '節省金額', dataIndex: 'total_amount', key: 'total_amount', 
    customRender: ({ text }) => `$${text.toFixed(2)}` }
]

// 生命週期
onMounted(() => {
  refreshData()
})

// 載入折扣碼統計
const loadDiscountCodeStats = async () => {
  try {
    const response = await axios.get('/api/promo-codes/stats/overview')
    const discountStats = response.data
    
    // 更新統計資料
    stats.total_discount_codes = discountStats.total_codes
    stats.active_discount_codes = discountStats.active_codes
    stats.total_discount_usage = discountStats.total_usage
    stats.total_discount_amount = discountStats.total_discount_amount
    
    // 計算轉換率
    if (stats.total_orders > 0) {
      discountConversionRate.value = (stats.total_discount_usage / stats.total_orders) * 100
    }
    
    // 計算平均折扣金額
    if (stats.total_discount_usage > 0) {
      averageDiscountAmount.value = stats.total_discount_amount / stats.total_discount_usage
    }
    
    // 計算使用率
    if (stats.total_discount_codes > 0) {
      discountUsageRate.value = (stats.active_discount_codes / stats.total_discount_codes) * 100
    }
    
  } catch (error) {
    console.error('載入折扣碼統計失敗:', error)
  }
}

// 載入折扣碼排名
const loadDiscountCodeRanking = async () => {
  try {
    const response = await axios.get('/api/promo-codes', { 
      params: { limit: 10, sort: 'usage_desc' }
    })
    const codes = response.data.items || response.data
    
    popularDiscountCodes.value = codes.slice(0, 5)
    discountCodeRanking.value = codes.slice(0, 10).map(code => ({
      code: code.code,
      used_count: code.used_count,
      total_amount: code.used_count * code.discount_value
    }))
    
    // 繪製圖表
    drawDiscountCharts()
    
  } catch (error) {
    console.error('載入折扣碼排名失敗:', error)
  }
}

// 繪製折扣碼圖表
const drawDiscountCharts = () => {
  // 繪製折扣碼類型分佈圖
  if (discountTypeChart.value) {
    const ctx = discountTypeChart.value.getContext('2d')
    
    // 計算各類型數量
    const typeData = popularDiscountCodes.value.reduce((acc, code) => {
      acc[code.discount_type] = (acc[code.discount_type] || 0) + 1
      return acc
    }, {})
    
    // 簡化的圓餅圖繪製
    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
    const labels = Object.keys(typeData)
    const values = Object.values(typeData)
    
    if (labels.length > 0) {
      drawPieChart(ctx, labels, values, colors)
    }
  }
  
  // 繪製使用趨勢圖
  if (discountTrendChart.value) {
    const ctx = discountTrendChart.value.getContext('2d')
    drawTrendChart(ctx)
  }
}

// 簡化的圓餅圖繪製函數
const drawPieChart = (ctx, labels, values, colors) => {
  const centerX = ctx.canvas.width / 2
  const centerY = ctx.canvas.height / 2
  const radius = Math.min(centerX, centerY) - 20
  
  const total = values.reduce((sum, value) => sum + value, 0)
  let currentAngle = 0
  
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height)
  
  values.forEach((value, index) => {
    const sliceAngle = (value / total) * 2 * Math.PI
    
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle)
    ctx.lineTo(centerX, centerY)
    ctx.fillStyle = colors[index % colors.length]
    ctx.fill()
    
    currentAngle += sliceAngle
  })
  
  // 繪製圖例
  labels.forEach((label, index) => {
    const legendY = 20 + index * 25
    ctx.fillStyle = colors[index % colors.length]
    ctx.fillRect(10, legendY, 15, 15)
    ctx.fillStyle = '#333'
    ctx.font = '12px Arial'
    ctx.fillText(label, 30, legendY + 12)
  })
}

// 簡化的趨勢圖繪製函數
const drawTrendChart = (ctx) => {
  const width = ctx.canvas.width
  const height = ctx.canvas.height
  const padding = 40
  
  ctx.clearRect(0, 0, width, height)
  
  // 繪製座標軸
  ctx.strokeStyle = '#ddd'
  ctx.beginPath()
  ctx.moveTo(padding, height - padding)
  ctx.lineTo(width - padding, height - padding)
  ctx.moveTo(padding, height - padding)
  ctx.lineTo(padding, padding)
  ctx.stroke()
  
  // 繪製趨勢線
  ctx.strokeStyle = '#1890ff'
  ctx.lineWidth = 2
  ctx.beginPath()
  
  // 模擬數據點
  const points = [
    { x: padding + 50, y: height - padding - 30 },
    { x: padding + 120, y: height - padding - 50 },
    { x: padding + 200, y: height - padding - 80 },
    { x: padding + 280, y: height - padding - 60 }
  ]
  
  points.forEach((point, index) => {
    if (index === 0) {
      ctx.moveTo(point.x, point.y)
    } else {
      ctx.lineTo(point.x, point.y)
    }
  })
  
  ctx.stroke()
  
  // 繪製數據點
  ctx.fillStyle = '#1890ff'
  points.forEach(point => {
    ctx.beginPath()
    ctx.arc(point.x, point.y, 4, 0, 2 * Math.PI)
    ctx.fill()
  })
}
</script>

<style scoped>
.admin-page {
  padding: 24px;
}

.page-header {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.title-section p {
  margin: 8px 0 0 0;
  color: #666;
}

.action-section {
  display: flex;
  gap: 12px;
}

.stats-section {
  margin-bottom: 24px;
}

.stats-row {
  margin-bottom: 16px;
}

.stats-row:last-child {
  margin-bottom: 0;
}

.sub-stat {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.filter-section {
  margin-bottom: 24px;
}

.filter-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.content-section {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
}

.content-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.chart-container canvas {
  max-width: 100%;
  height: auto;
}

.benefit-analysis {
  padding: 16px 0;
}

.benefit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.benefit-item:last-child {
  border-bottom: none;
}

.benefit-label {
  font-size: 14px;
  color: #666;
}

.benefit-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.ranking-list {
  max-height: 300px;
  overflow-y: auto;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.ranking-item:last-child {
  border-bottom: none;
}

.ranking-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #1890ff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  margin-right: 12px;
}

.ranking-info {
  flex: 1;
}

.ranking-code {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.ranking-stats {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.ranking-amount {
  font-size: 14px;
  font-weight: 600;
  color: #52c41a;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .admin-page {
    padding: 16px;
  }
  
  .page-header {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
  }
  
  .content-section {
    padding: 8px;
  }
  
  .chart-container {
    min-height: 150px;
  }
  
  .benefit-analysis {
    padding: 8px 0;
  }
  
  .ranking-list {
    max-height: 200px;
  }
}
</style> 