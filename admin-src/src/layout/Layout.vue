<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible>
      <div class="logo">
        <h3 v-if="!collapsed" style="color: white; text-align: center; margin: 16px 0;">
          BlogCommerce
        </h3>
        <h3 v-else style="color: white; text-align: center; margin: 16px 0;">
          BC
        </h3>
      </div>
      
      <a-menu theme="dark" mode="inline" :selected-keys="selectedKeys">
        <a-menu-item key="dashboard" @click="$router.push('/dashboard')">
          <dashboard-outlined />
          <span>儀表板</span>
        </a-menu-item>
        
        <a-menu-item key="posts" @click="$router.push('/posts')">
          <edit-outlined />
          <span>文章管理</span>
        </a-menu-item>
        
        <a-menu-item key="products" @click="$router.push('/products')">
          <shopping-outlined />
          <span>商品管理</span>
        </a-menu-item>
        
        <a-menu-item key="orders" @click="$router.push('/orders')">
          <shopping-cart-outlined />
          <span>訂單管理</span>
        </a-menu-item>
        
        <a-menu-item key="users" @click="$router.push('/users')">
          <user-outlined />
          <span>會員管理</span>
        </a-menu-item>
        
        <a-menu-item key="banners" @click="$router.push('/banners')">
          <picture-outlined />
          <span>廣告管理</span>
        </a-menu-item>
        
        <a-menu-item key="shipping-tiers" @click="$router.push('/shipping-tiers')">
          <car-outlined />
          <span>運費級距</span>
        </a-menu-item>
        
        <a-menu-item key="promo-codes" @click="$router.push('/promo-codes')">
          <gift-outlined />
          <span>推薦碼管理</span>
        </a-menu-item>
        
        <!-- 移除: 數據分析選單項目 -->
        
        <a-menu-item key="settings" @click="$router.push('/settings')">
          <setting-outlined />
          <span>系統設定</span>
        </a-menu-item>

      </a-menu>
    </a-layout-sider>
    
    <a-layout>
      <a-layout-header style="background: #fff; padding: 0 24px; box-shadow: 0 1px 4px rgba(0,21,41,.08);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="font-size: 18px; font-weight: bold;">
            {{ getPageTitle() }}
          </div>
          
          <a-dropdown>
            <template #overlay>
              <a-menu>
                <a-menu-item @click="handleLogout">
                  <logout-outlined />
                  登出
                </a-menu-item>
              </a-menu>
            </template>
            
            <a-button type="text" style="height: auto;">
              <user-outlined />
              {{ authStore.user?.username }}
              <down-outlined />
            </a-button>
          </a-dropdown>
        </div>
      </a-layout-header>
      
      <a-layout-content style="margin: 24px; padding: 24px; background: #fff; min-height: 280px;">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '../stores/auth'
import {
  DashboardOutlined,
  EditOutlined,
  ShoppingOutlined,
  ShoppingCartOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  DownOutlined,
  PictureOutlined,
  CarOutlined,
  GiftOutlined
} from '@ant-design/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const collapsed = ref(false)

const selectedKeys = computed(() => {
  const path = route.path.substring(1) // 移除開頭的 /
  return [path || 'dashboard']
})

const pageTitle = {
  dashboard: '儀表板',
  posts: '文章管理',
  products: '商品管理',
  orders: '訂單管理',
  users: '會員管理',
  banners: '廣告管理',
  'shipping-tiers': '運費級距',
  'promo-codes': '推薦碼管理',
  // 移除: analytics: '數據分析',
  settings: '系統設定'
}

const getPageTitle = () => {
  const path = route.path.substring(1) || 'dashboard'
  return pageTitle[path] || '管理後台'
}

const handleLogout = () => {
  authStore.logout()
  message.success('已登出')
  router.push('/login')
}
</script>

<style scoped>
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #303030;
}
</style> 
