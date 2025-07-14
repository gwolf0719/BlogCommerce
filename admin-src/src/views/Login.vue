<template>
  <div class="login-container">
    <a-card class="login-card" :bordered="false">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-gray-800">
          管理後台登入
        </h2>
        <p class="text-gray-500 mt-2">歡迎回來！</p>
      </div>
      <a-form
        :model="formState"
        name="login"
        class="login-form"
        @finish="handleLogin"
      >
        <a-form-item
          name="username"
          :rules="[{ required: true, message: '請輸入用戶名!' }]"
        >
          <a-input v-model:value="formState.username" placeholder="用戶名" size="large">
            <template #prefix>
              <UserOutlined class="site-form-item-icon" />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item
          name="password"
          :rules="[{ required: true, message: '請輸入密碼!' }]"
        >
          <a-input-password v-model:value="formState.password" placeholder="密碼" size="large">
            <template #prefix>
              <LockOutlined class="site-form-item-icon" />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item>
          <a-button type="primary" html-type="submit" class="w-full" size="large" :loading="loading">
            登入
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { handleApiError } from '@/utils/errorHandler'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const formState = reactive({
  username: '',
  password: '',
})

const handleLogin = async (values) => {
  loading.value = true
  try {
    await authStore.login(values)
    message.success('登入成功，正在跳轉...')
    // 直接跳轉到根路徑，讓路由守衛處理後續
    // 路由守衛會根據登入後的狀態決定要跳轉到 dashboard 還是其他頁面
    router.push('/')
  } catch (error) {
    // 登入失敗的錯誤已在 authStore 中處理，這裡只處理非預期的錯誤
    if (!error.response) {
      message.error(error.message || '登入時發生未知錯誤')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 400px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border-radius: 12px;
  padding: 2rem;
}

@media (max-width: 420px) {
  .login-card {
    width: 100%;
    margin: 20px;
    padding: 1.5rem;
    box-shadow: none;
    border: none;
  }
}

.login-form .ant-form-item {
  margin-bottom: 24px;
}

.login-form .ant-btn-primary {
  background: #1890ff;
  border-color: #1890ff;
}

.login-form .ant-btn-primary:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

.site-form-item-icon {
  color: rgba(0,0,0,.25);
}
</style>