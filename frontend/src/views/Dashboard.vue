<template>
  <div class="p-6">
    <!-- 主要統計卡片 -->
    <a-row :gutter="16" class="mb-6">
      <a-col :span="6">
        <a-card>
          <a-statistic 
            title="會員總數" 
            :value="stats.users" 
            :loading="loading"
            :value-style="{ color: '#1890ff' }"
          />
          <div class="mt-2 text-sm text-gray-500">
            當前在線: {{ stats.activeUsers || 0 }}
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic 
            title="文章總數" 
            :value="stats.posts" 
            :loading="loading"
            :value-style="{ color: '#52c41a' }"
          />
          <div class="mt-2 text-sm text-gray-500">
            已發布: {{ stats.publishedPosts || 0 }}
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic 
            title="商品總數" 
            :value="stats.products" 
            :loading="loading"
            :value-style="{ color: '#fa8c16' }"
          />
          <div class="mt-2 text-sm text-gray-500">
            上架中: {{ stats.activeProducts || 0 }}
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic 
            title="訂單總數" 
            :value="stats.orders" 
            :loading="loading"
            :value-style="{ color: '#722ed1' }"
          />
          <div class="mt-2 text-sm text-gray-500">
            待處理: {{ stats.pendingOrders || 0 }}
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 銷售統計 -->
    <a-row :gutter="16" class="mb-6">
      <a-col :span="8">
        <a-card>
          <a-statistic 
            title="總銷售額" 
            :value="stats.totalSales" 
            prefix="$"
            :precision="2"
            :loading="loading"
            :value-style="{ color: '#13c2c2' }"
          />
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card>
          <a-statistic 
            title="今日訂單" 
            :value="stats.todayOrders" 
            :loading="loading"
            :value-style="{ color: '#eb2f96' }"
          />
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card>
          <a-statistic 
            title="今日銷售額" 
            :value="stats.todayRevenue" 
            prefix="$"
            :precision="2"
            :loading="loading"
            :value-style="{ color: '#f5222d' }"
          />
        </a-card>
      </a-col>
    </a-row>

    <!-- 即時數據更新提示 -->
    <div v-if="stats.calculatedAt" class="text-xs text-gray-400 text-right">
      數據更新時間: {{ new Date(stats.calculatedAt).toLocaleString('zh-TW') }}
      <a-button size="small" type="link" @click="loadDashboardStats">
        <template #icon><ReloadOutlined /></template>
        立即刷新
      </a-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(true)
const stats = ref({
  users: 0,
  posts: 0,
  products: 0,
  orders: 0,
  activeProducts: 0,
  publishedPosts: 0,
  pendingOrders: 0,
  totalSales: 0,
  todayOrders: 0,
  todayRevenue: 0,
  activeUsers: 0,
  calculatedAt: null
})

const loadDashboardStats = async () => {
  loading.value = true
  try {
    // 使用即時統計 API 獲取準確數據
    const response = await fetch('/api/admin/stats', {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })

    if (response.ok) {
      const statsData = await response.json()
      
      // 更新統計數據，使用即時計算的數值
      stats.value = {
        users: statsData.total_users || 0,
        posts: statsData.total_posts || 0,
        products: statsData.total_products || 0,
        orders: statsData.total_orders || 0,
        activeProducts: statsData.active_products || 0,
        publishedPosts: statsData.published_posts || 0,
        pendingOrders: statsData.pending_orders || 0,
        totalSales: statsData.total_sales || 0,
        todayOrders: statsData.today_orders || 0,
        todayRevenue: statsData.today_revenue || 0,
        activeUsers: statsData.active_sessions || 0,
        calculatedAt: statsData.calculated_at
      }
    } else {
      throw new Error('獲取統計數據失敗')
    }

  } catch (error) {
    console.error('獲取儀表板統計失敗:', error)
    message.error('無法獲取統計數據，請檢查網路連線或聯繫管理員')
    
    // 設置空數據
    stats.value = {
      users: 0,
      posts: 0,
      products: 0,
      orders: 0,
      activeProducts: 0,
      publishedPosts: 0,
      pendingOrders: 0,
      totalSales: 0,
      todayOrders: 0,
      todayRevenue: 0,
      activeUsers: 0
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboardStats()
})
</script> 