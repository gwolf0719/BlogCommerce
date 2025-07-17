import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Layout from '../layout/Layout.vue'
import Dashboard from '../views/Dashboard.vue'
import Posts from '../views/Posts.vue'
import Products from '../views/Products.vue'
import Orders from '../views/Orders.vue'
import Users from '../views/Users.vue'
import Settings from '../views/Settings.vue'
import Banners from '../views/Banners.vue'
import ShippingTiers from '../views/ShippingTiers.vue'
import PromoCodes from '../views/PromoCodes.vue'

const routes = [
  {
    // 登入頁面路由，注意它在 /admin/login
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    // 主佈局，對應 /admin/
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: Dashboard },
      { path: 'posts', name: 'Posts', component: Posts },
      { path: 'products', name: 'Products', component: Products },
      { path: 'orders', name: 'Orders', component: Orders },
      { path: 'users', name: 'Users', component: Users },
      { path: 'banners', name: 'Banners', component: Banners },
      { path: 'shipping-tiers', name: 'ShippingTiers', component: ShippingTiers },
      { path: 'promo-codes', name: 'PromoCodes', component: PromoCodes },
      { path: 'settings', name: 'Settings', component: Settings }
    ]
  }
]

// 創建並導出 router 實例
const router = createRouter({
  // 使用 createWebHistory 並設定 base 路徑為 /admin/
  // 這會讓所有路由都在 /admin/ 之後，例如 /admin/dashboard
  history: createWebHistory('/admin/'),
  routes
})

export default router
