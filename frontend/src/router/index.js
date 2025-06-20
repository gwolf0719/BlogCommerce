import Login from '../views/Login.vue'
import Layout from '../layout/Layout.vue'
import Dashboard from '../views/Dashboard.vue'
import Posts from '../views/Posts.vue'
import Products from '../views/Products.vue'
import Orders from '../views/Orders.vue'
import Users from '../views/Users.vue'
import Analytics from '../views/Analytics.vue'
import Settings from '../views/Settings.vue'
import ErrorLogs from '../views/ErrorLogs.vue'


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
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: '/posts',
        name: 'Posts',
        component: Posts
      },
      {
        path: '/products',
        name: 'Products',
        component: Products
      },
      {
        path: '/orders',
        name: 'Orders',
        component: Orders
      },
      {
        path: '/users',
        name: 'Users',
        component: Users
      },
      {
        path: '/analytics',
        name: 'Analytics',
        component: Analytics
      },
      {
        path: '/settings',
        name: 'Settings',
        component: Settings
      },
      {
        path: '/error-logs',
        name: 'ErrorLogs',
        component: ErrorLogs
      }
    ]
  }
]

export default routes 