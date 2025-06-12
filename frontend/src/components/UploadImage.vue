<template>
  <div class="upload-image-container">
    <!-- 已上傳的圖片 -->
    <div v-if="imageUrl" class="uploaded-image">
      <div class="image-preview">
        <img :src="imageUrl" alt="預覽圖片" />
        <div class="image-overlay">
          <a-button type="text" size="small" @click="handlePreview">
            <EyeOutlined style="color: white;" />
          </a-button>
          <a-button type="text" size="small" @click="handleDelete">
            <DeleteOutlined style="color: white;" />
          </a-button>
        </div>
      </div>
    </div>

    <!-- 上傳區域 -->
    <div v-else class="upload-area">
      <a-upload
        :show-upload-list="false"
        :before-upload="beforeUpload"
        :custom-request="handleUpload"
        accept="image/*"
        class="uploader"
      >
        <div class="upload-trigger">
          <div v-if="uploading" class="uploading">
            <LoadingOutlined />
            <div class="uploading-text">上傳中...</div>
          </div>
          <div v-else class="upload-content">
            <PlusOutlined />
            <div class="upload-text">點擊或拖拽上傳圖片</div>
          </div>
        </div>
      </a-upload>
    </div>

    <!-- 手動輸入URL -->
    <div class="manual-input">
      <a-input
        v-model:value="manualUrl"
        placeholder="或直接輸入圖片URL"
        @blur="handleManualUrl"
        @pressEnter="handleManualUrl"
      >
        <template #suffix>
          <a-button type="text" size="small" @click="handleManualUrl" :disabled="!manualUrl">
            確定
          </a-button>
        </template>
      </a-input>
    </div>

    <!-- 圖片預覽彈窗 -->
    <a-modal
      v-model:open="previewVisible"
      title="圖片預覽"
      :footer="null"
      width="80%"
      style="max-width: 800px;"
    >
      <img :src="imageUrl" style="width: 100%;" />
    </a-modal>
  </div>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined, EyeOutlined, DeleteOutlined, LoadingOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const authStore = useAuthStore()
const uploading = ref(false)
const previewVisible = ref(false)
const manualUrl = ref('')
const imageUrl = ref(props.modelValue)

// 監聽 modelValue 變化
watch(() => props.modelValue, (newValue) => {
  imageUrl.value = newValue
})

// 監聽 imageUrl 變化，向父組件發射更新
watch(imageUrl, (newValue) => {
  emit('update:modelValue', newValue)
})

// 上傳前檢查
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('只能上傳圖片文件!')
    return false
  }

  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    message.error('圖片大小不能超過 10MB!')
    return false
  }

  return true
}

// 自定義上傳
const handleUpload = async ({ file, onProgress, onSuccess, onError }) => {
  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch('/api/admin/upload/image', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      },
      body: formData
    })

    if (!response.ok) {
      throw new Error('上傳失敗')
    }

    const data = await response.json()
    imageUrl.value = data.url
    message.success('圖片上傳成功')
    onSuccess(data)

  } catch (error) {
    message.error(error.message || '圖片上傳失敗')
    onError(error)
  } finally {
    uploading.value = false
  }
}

// 預覽圖片
const handlePreview = () => {
  previewVisible.value = true
}

// 刪除圖片
const handleDelete = () => {
  imageUrl.value = ''
  manualUrl.value = ''
  message.success('圖片已刪除')
}

// 手動輸入URL
const handleManualUrl = () => {
  if (manualUrl.value && isValidUrl(manualUrl.value)) {
    imageUrl.value = manualUrl.value
    message.success('圖片URL已設定')
  } else if (manualUrl.value) {
    message.error('請輸入有效的圖片URL')
  }
}

// 驗證URL
const isValidUrl = (url) => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}
</script>

<style scoped>
.upload-image-container {
  width: 100%;
  max-width: 300px;
}

.uploaded-image {
  position: relative;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 12px;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 200px;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-preview:hover .image-overlay {
  opacity: 1;
}

.upload-area {
  margin-bottom: 12px;
}

.uploader {
  width: 100%;
}

.upload-trigger {
  width: 100%;
  height: 200px;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.upload-trigger:hover {
  border-color: #1890ff;
}

.upload-content,
.uploading {
  text-align: center;
  color: #666;
}

.upload-content .anticon,
.uploading .anticon {
  font-size: 32px;
  margin-bottom: 8px;
  display: block;
}

.upload-text,
.uploading-text {
  font-size: 14px;
}

.uploading {
  color: #1890ff;
}

.manual-input {
  margin-top: 8px;
}

.manual-input :deep(.ant-input-group-addon) {
  padding: 0;
}
</style> 