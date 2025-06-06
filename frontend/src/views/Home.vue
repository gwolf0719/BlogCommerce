<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
      <div class="max-w-7xl mx-auto px-4 text-center">
        <h1 class="text-5xl font-bold mb-6">
          歡迎來到 {{ appName }}
        </h1>
        <p class="text-xl mb-8 max-w-2xl mx-auto">
          現代化的部落格與電商系統，讓您輕鬆建立線上業務
        </p>
        <div class="space-x-4">
          <router-link
            to="/blog"
            class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            閱讀部落格
          </router-link>
          <router-link
            to="/products"
            class="bg-transparent border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
          >
            瀏覽商品
          </router-link>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">
            功能特色
          </h2>
          <p class="text-gray-600 max-w-2xl mx-auto">
            我們提供完整的部落格和電商解決方案
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- 部落格功能 -->
          <div class="text-center p-6">
            <div class="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">部落格系統</h3>
            <p class="text-gray-600">
              完整的文章管理、分類標籤、SEO 優化功能
            </p>
          </div>

          <!-- 電商功能 -->
          <div class="text-center p-6">
            <div class="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">電商系統</h3>
            <p class="text-gray-600">
              商品管理、購物車、訂單處理一應俱全
            </p>
          </div>

          <!-- 管理後台 -->
          <div class="text-center p-6">
            <div class="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">管理後台</h3>
            <p class="text-gray-600">
              強大的後台管理系統，輕鬆管理內容和訂單
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="py-16 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
          <div>
            <div class="text-3xl font-bold text-blue-600 mb-2">{{ stats.posts }}+</div>
            <div class="text-gray-600">文章發布</div>
          </div>
          <div>
            <div class="text-3xl font-bold text-green-600 mb-2">{{ stats.products }}+</div>
            <div class="text-gray-600">商品上架</div>
          </div>
          <div>
            <div class="text-3xl font-bold text-purple-600 mb-2">{{ stats.orders }}+</div>
            <div class="text-gray-600">成功訂單</div>
          </div>
          <div>
            <div class="text-3xl font-bold text-red-600 mb-2">{{ stats.users }}+</div>
            <div class="text-gray-600">活躍用戶</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 bg-blue-600 text-white">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl font-bold mb-4">
          準備開始您的線上業務了嗎？
        </h2>
        <p class="text-xl mb-8">
          立即體驗我們強大的部落格和電商功能
        </p>
        <router-link
          to="/admin/login"
          class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-block"
        >
          開始使用
        </router-link>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Home',
  setup() {
    const appName = ref('BlogCommerce')
    const stats = ref({
      posts: 0,
      products: 0,
      orders: 0,
      users: 0
    })

    // 模擬統計數據動畫
    const animateStats = () => {
      const targetStats = {
        posts: 150,
        products: 89,
        orders: 324,
        users: 1250
      }

      Object.keys(targetStats).forEach(key => {
        let current = 0
        const target = targetStats[key]
        const increment = Math.ceil(target / 50)
        
        const timer = setInterval(() => {
          current += increment
          if (current >= target) {
            current = target
            clearInterval(timer)
          }
          stats.value[key] = current
        }, 30)
      })
    }

    onMounted(() => {
      // 頁面載入後開始統計動畫
      setTimeout(animateStats, 500)
    })

    return {
      appName,
      stats
    }
  }
}
</script>

<style scoped>
/* 任何需要的樣式 */
</style> 