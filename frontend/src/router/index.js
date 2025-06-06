import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Blog from '../views/Blog.vue'
import BlogPost from '../views/BlogPost.vue'
import Products from '../views/Products.vue'
import Product from '../views/Product.vue'
import Cart from '../views/Cart.vue'
import Checkout from '../views/Checkout.vue'
import AdminLogin from '../views/admin/AdminLogin.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminPosts from '../views/admin/AdminPosts.vue'
import AdminProducts from '../views/admin/AdminProducts.vue'
import AdminOrders from '../views/admin/AdminOrders.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/blog',
      name: 'blog',
      component: Blog
    },
    {
      path: '/blog/:slug',
      name: 'blog-post',
      component: BlogPost
    },
    {
      path: '/products',
      name: 'products',
      component: Products
    },
    {
      path: '/product/:slug',
      name: 'product',
      component: Product
    },
    {
      path: '/cart',
      name: 'cart',
      component: Cart
    },
    {
      path: '/checkout',
      name: 'checkout',
      component: Checkout
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: AdminLogin
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminDashboard,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/posts',
      name: 'admin-posts',
      component: AdminPosts,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/products',
      name: 'admin-products',
      component: AdminProducts,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/orders',
      name: 'admin-orders',
      component: AdminOrders,
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守衛
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      next('/admin/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router 