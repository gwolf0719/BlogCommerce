import Login from '../views/Login.vue'
import Layout from '../layout/Layout.vue'
import Dashboard from '../views/Dashboard.vue'
import Posts from '../views/Posts.vue'
import Products from '../views/Products.vue'
import Orders from '../views/Orders.vue'
import Users from '../views/Users.vue'
// 移除: import Analytics from '../views/Analytics.vue'
import Settings from '../views/Settings.vue'
import Banners from '../views/Banners.vue'
import ShippingTiers from '../views/ShippingTiers.vue'
import PromoCodes from '../views/PromoCodes.vue'


const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: 'posts',
        name: 'Posts',
        component: Posts
      },
      {
        path: 'products',
        name: 'Products',
        component: Products
      },
      {
        path: 'orders',
        name: 'Orders',
        component: Orders
      },
      {
        path: 'users',
        name: 'Users',
        component: Users
      },
      {
        path: 'banners',
        name: 'Banners',
        component: Banners
      },
      {
        path: 'shipping-tiers',
        name: 'ShippingTiers',
        component: ShippingTiers
      },
      {
        path: 'promo-codes',
        name: 'PromoCodes',
        component: PromoCodes
      },
      // 移除: Analytics 路由設定
      {
        path: 'settings',
        name: 'Settings',
        component: Settings
      }
    ]
  }
]

export default routes
