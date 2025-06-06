<template>
  <div id="app">
    <!-- 導航列 -->
    <nav class="bg-white shadow-lg">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex justify-between h-16">
          <div class="flex">
            <!-- Logo -->
            <div class="flex-shrink-0 flex items-center">
              <router-link to="/" class="text-2xl font-bold text-blue-600">
                {{ appName }}
              </router-link>
            </div>
            
            <!-- 主要導航 -->
            <div class="hidden md:ml-6 md:flex md:space-x-8">
              <router-link
                to="/"
                class="text-gray-900 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                :class="{ 'text-blue-600 border-b-2 border-blue-600': $route.path === '/' }"
              >
                首頁
              </router-link>
              <router-link
                to="/blog"
                class="text-gray-900 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                :class="{ 'text-blue-600 border-b-2 border-blue-600': $route.path.startsWith('/blog') }"
              >
                部落格
              </router-link>
              <router-link
                to="/products"
                class="text-gray-900 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                :class="{ 'text-blue-600 border-b-2 border-blue-600': $route.path.startsWith('/product') }"
              >
                商品
              </router-link>
            </div>
          </div>
          
          <!-- 右側按鈕 -->
          <div class="hidden md:ml-6 md:flex md:items-center md:space-x-4">
            <!-- 購物車 -->
            <router-link
              to="/cart"
              class="text-gray-500 hover:text-gray-700 p-2 relative"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.68 4.19a2 2 0 001.94 2.81h9.48a2 2 0 001.94-2.81L13 13M7 13v4a2 2 0 002 2h4a2 2 0 002-2v-4"></path>
              </svg>
              <span
                v-if="cartItemsCount > 0"
                class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center"
              >
                {{ cartItemsCount }}
              </span>
            </router-link>
            
            <!-- 管理員登入 -->
            <router-link
              v-if="!isLoggedIn"
              to="/admin/login"
              class="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
            >
              登入
            </router-link>
            
            <!-- 管理員區域 -->
            <div v-else class="relative">
              <button
                @click="showUserMenu = !showUserMenu"
                class="flex items-center text-sm rounded-full text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <span class="mr-2">管理員</span>
                <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
              
              <!-- 下拉選單 -->
              <div
                v-if="showUserMenu"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50"
              >
                <router-link
                  to="/admin/dashboard"
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  控制台
                </router-link>
                <button
                  @click="logout"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  登出
                </button>
              </div>
            </div>
          </div>
          
          <!-- 移動端選單按鈕 -->
          <div class="md:hidden flex items-center">
            <button
              @click="showMobileMenu = !showMobileMenu"
              class="text-gray-500 hover:text-gray-700 focus:outline-none focus:text-gray-700"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  :class="{ 'hidden': showMobileMenu, 'inline-flex': !showMobileMenu }"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
                <path
                  :class="{ 'hidden': !showMobileMenu, 'inline-flex': showMobileMenu }"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- 移動端選單 -->
      <div :class="{ 'block': showMobileMenu, 'hidden': !showMobileMenu }" class="md:hidden">
        <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          <router-link
            to="/"
            class="text-gray-900 hover:text-blue-600 block px-3 py-2 text-base font-medium"
          >
            首頁
          </router-link>
          <router-link
            to="/blog"
            class="text-gray-900 hover:text-blue-600 block px-3 py-2 text-base font-medium"
          >
            部落格
          </router-link>
          <router-link
            to="/products"
            class="text-gray-900 hover:text-blue-600 block px-3 py-2 text-base font-medium"
          >
            商品
          </router-link>
          <router-link
            to="/cart"
            class="text-gray-900 hover:text-blue-600 block px-3 py-2 text-base font-medium"
          >
            購物車 ({{ cartItemsCount }})
          </router-link>
        </div>
      </div>
    </nav>
    
    <!-- 主要內容區域 -->
    <main class="min-h-screen bg-gray-50">
      <router-view />
    </main>
    
    <!-- 頁腳 -->
    <footer class="bg-gray-800 text-white">
      <div class="max-w-7xl mx-auto px-4 py-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 class="text-lg font-semibold mb-4">{{ appName }}</h3>
            <p class="text-gray-300 text-sm">
              現代化的部落格與電商系統，使用 Vue 3 + FastAPI 構建。
            </p>
          </div>
          
          <div>
            <h4 class="text-md font-semibold mb-4">快速連結</h4>
            <ul class="space-y-2">
              <li><router-link to="/" class="text-gray-300 hover:text-white text-sm">首頁</router-link></li>
              <li><router-link to="/blog" class="text-gray-300 hover:text-white text-sm">部落格</router-link></li>
              <li><router-link to="/products" class="text-gray-300 hover:text-white text-sm">商品</router-link></li>
            </ul>
          </div>
          
          <div>
            <h4 class="text-md font-semibold mb-4">客戶服務</h4>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-300 hover:text-white text-sm">聯絡我們</a></li>
              <li><a href="#" class="text-gray-300 hover:text-white text-sm">常見問題</a></li>
              <li><a href="#" class="text-gray-300 hover:text-white text-sm">退貨政策</a></li>
            </ul>
          </div>
          
          <div>
            <h4 class="text-md font-semibold mb-4">追蹤我們</h4>
            <div class="flex space-x-4">
              <a href="#" class="text-gray-300 hover:text-white">
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                </svg>
              </a>
              <a href="#" class="text-gray-300 hover:text-white">
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98C8.28 9.09 5.11 7.38 3 4.79c-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.521 8.521 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.44 20.29 5.7 21 8.12 21 16 21 20.33 14.46 20.33 8.79c0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
        
        <div class="mt-8 pt-8 border-t border-gray-700 text-center">
          <p class="text-gray-400 text-sm">
            © {{ currentYear }} {{ appName }}. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { computed, ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useCartStore } from './stores/cart'

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore()
    const cartStore = useCartStore()
    
    const showUserMenu = ref(false)
    const showMobileMenu = ref(false)
    const appName = ref('BlogCommerce')
    const currentYear = ref(new Date().getFullYear())
    
    const isLoggedIn = computed(() => authStore.isLoggedIn)
    const cartItemsCount = computed(() => cartStore.itemsCount)
    
    const logout = async () => {
      await authStore.logout()
      showUserMenu.value = false
    }
    
    onMounted(() => {
      // 檢查本地儲存的認證狀態
      authStore.checkAuth()
      cartStore.loadCart()
    })
    
    return {
      showUserMenu,
      showMobileMenu,
      appName,
      currentYear,
      isLoggedIn,
      cartItemsCount,
      logout
    }
  }
}
</script>

<style scoped>
/* 任何需要的樣式 */
</style> 