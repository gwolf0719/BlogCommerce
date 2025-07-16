<template>
  <div class="upload-gallery-container">
    <!-- 已上傳的圖片 -->
    <div v-if="imageList.length > 0" class="gallery-grid">
      <div
        v-for="(image, index) in imageList"
        :key="index"
        class="gallery-item"
      >
        <div class="image-preview">
          <img :src="image" alt="圖庫圖片" />
          <div class="image-overlay">
            <a-button type="text" size="small" @click="handlePreview(image)">
              <EyeOutlined style="color: white;" />
            </a-button>
            <a-button type="text" size="small" @click="handleDelete(index)">
              <DeleteOutlined style="color: white;" />
            </a-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上傳區域 -->
    <div class="upload-area">
      <a-upload
        :show-upload-list="false"
        :before-upload="beforeUpload"
        :custom-request="handleUpload"
        accept="image/*"
        multiple
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
            <div class="upload-hint">支援多選</div>
          </div>
        </div>
      </a-upload>
    </div>

    <!-- 手動輸入URL（改為純 input，避免 ant-design-vue 表單收集衝突） -->
    <a-form-item-rest>
      <div class="manual-input">
        <input
          v-model="manualUrl"
          placeholder="或直接輸入圖片URL (按Enter添加)"
          @keyup.enter="handleManualUrl"
          style="width: 100%; padding: 4px 8px; border: 1px solid #d9d9d9; border-radius: 4px;"
        />
        <button type="button" @click="handleManualUrl" :disabled="!manualUrl" style="margin-top: 4px;">添加</button>
      </div>
    </a-form-item-rest>

    <!-- 圖片預覽彈窗 -->
    <a-modal
      v-model:open="previewVisible"
      title="圖片預覽"
      :footer="null"
      width="80%"
      style="max-width: 800px;"
    >
      <img :src="previewImage" style="width: 100%;" />
    </a-modal>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined, EyeOutlined, DeleteOutlined, LoadingOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  maxCount: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits(['update:modelValue'])

const authStore = useAuthStore()
const uploading = ref(false)
const previewVisible = ref(false)
const previewImage = ref('')
const manualUrl = ref('')
const imageList = ref([...props.modelValue])

// 監聽 modelValue 變化
watch(() => props.modelValue, (newValue) => {
  // 修正: 只有在新舊值不同時才更新，避免無限循環
  if (JSON.stringify(newValue) !== JSON.stringify(imageList.value)) {
    imageList.value = [...newValue]
  }
})

// 監聽 imageList 變化，向父組件發射更新
watch(imageList, (newValue) => {
  emit('update:modelValue', [...newValue])
}, { deep: true })

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

  if (imageList.value.length >= props.maxCount) {
    message.error(`最多只能上傳 ${props.maxCount} 張圖片!`)
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
    imageList.value.push(data.url)
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
const handlePreview = (imageUrl) => {
  previewImage.value = imageUrl
  previewVisible.value = true
}

// 刪除圖片
const handleDelete = (index) => {
  imageList.value.splice(index, 1)
  message.success('圖片已刪除')
}

// 手動輸入URL
const handleManualUrl = () => {
  if (!manualUrl.value) return

  if (imageList.value.length >= props.maxCount) {
    message.error(`最多只能上傳 ${props.maxCount} 張圖片!`)
    return
  }

  if (isValidUrl(manualUrl.value)) {
    imageList.value.push(manualUrl.value)
    manualUrl.value = ''
    message.success('圖片已添加')
  } else {
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
.upload-gallery-container {
  width: 100%;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.gallery-item {
  position: relative;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  overflow: hidden;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 120px;
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
  height: 120px;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
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
  font-size: 24px;
  margin-bottom: 4px;
  display: block;
}

.upload-text,
.uploading-text {
  font-size: 14px;
  margin-bottom: 2px;
}

.upload-hint {
  font-size: 12px;
  color: #999;
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
