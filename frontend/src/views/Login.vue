<template>
  <div class="login-container">
    <a-card title="BlogCommerce 管理員登入" class="login-card">
      <a-form :model="form" @finish="handleLogin" layout="vertical">
        <a-form-item 
          label="使用者名稱" 
          name="username" 
          :rules="[{ required: true, message: '請輸入使用者名稱' }]">
          <a-input v-model:value="form.username" placeholder="請輸入使用者名稱" />
        </a-form-item>
        
        <a-form-item 
          label="密碼" 
          name="password" 
          :rules="[{ required: true, message: '請輸入密碼' }]">
          <a-input-password v-model:value="form.password" placeholder="請輸入密碼" />
        </a-form-item>
        
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading" block>
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
import { message } from 'ant-design-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({
  username: 'admin',
  password: 'admin123456'
})

const handleLogin = async (values) => {
  loading.value = true
  try {
    await authStore.login(values)
    message.success('登入成功')
    router.push('/')
  } catch (error) {
    message.error(error.message || '登入失敗')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
</style> 