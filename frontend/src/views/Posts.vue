<template>
  <div class="p-6">
    <!-- 頁面標題和新增按鈕 -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">文章管理</h1>
      <a-button type="primary" @click="handleCreate">
        <template #icon><PlusOutlined /></template>
        新增文章
      </a-button>
    </div>

    <!-- 搜尋和篩選 -->
    <a-card class="mb-6">
      <a-row :gutter="16">
        <a-col :span="8">
          <a-input
            v-model:value="searchForm.search"
            placeholder="搜尋文章標題或內容"
            @change="handleSearch"
            allowClear
          >
            <template #prefix><SearchOutlined /></template>
          </a-input>
        </a-col>
        <a-col :span="6">
          <a-select
            v-model:value="searchForm.published"
            placeholder="發布狀態"
            allowClear
            @change="handleSearch"
          >
            <a-select-option :value="true">已發布</a-select-option>
            <a-select-option :value="false">草稿</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-select
            v-model:value="searchForm.category_id"
            placeholder="選擇分類"
            allowClear
            @change="handleSearch"
          >
            <a-select-option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </a-select-option>
          </a-select>
        </a-col>
        <a-col :span="4">
          <a-button @click="resetSearch">重置</a-button>
        </a-col>
      </a-row>
    </a-card>

    <!-- 文章列表 -->
    <a-card>
      <a-table
        :columns="columns"
        :data-source="posts"
        :loading="loading"
        :pagination="paginationConfig"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'title'">
            <div>
              <a-typography-title :level="5" class="mb-1">{{ record.title }}</a-typography-title>
              <a-typography-text type="secondary" class="text-sm">{{ record.excerpt }}</a-typography-text>
            </div>
          </template>
          
          <template v-if="column.key === 'is_published'">
            <a-tag :color="record.is_published ? 'green' : 'orange'">
              {{ record.is_published ? '已發布' : '草稿' }}
            </a-tag>
          </template>
          
          <template v-if="column.key === 'categories'">
            <a-tag v-for="category in record.categories" :key="category.id" color="blue">
              {{ category.name }}
            </a-tag>
          </template>
          
          <template v-if="column.key === 'tags'">
            <a-tag v-for="tag in record.tags" :key="tag.id" color="cyan">
              {{ tag.name }}
            </a-tag>
          </template>
          
          <template v-if="column.key === 'created_at'">
            {{ formatDateTime(record.created_at) }}
          </template>
          
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleEdit(record)">
                <EditOutlined />
              </a-button>
              <a-popconfirm
                title="確定要刪除這篇文章嗎？"
                ok-text="確定"
                cancel-text="取消"
                @confirm="handleDelete(record.id)"
              >
                <a-button type="link" size="small" danger>
                  <DeleteOutlined />
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 新增/編輯文章彈窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '編輯文章' : '新增文章'"
      width="80%"
      @ok="handleSubmit"
      @cancel="handleCancel"
      :confirm-loading="submitLoading"
      :keyboard="false"
      :mask-closable="false"
    >
      <a-form
        ref="formRef"
        :model="form"
        :rules="rules"
        layout="vertical"
      >
        <a-row :gutter="16">
          <a-col :span="16">
            <a-form-item label="文章標題" name="title">
              <a-input v-model:value="form.title" placeholder="請輸入文章標題" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="發布狀態" name="is_published">
              <a-switch
                v-model:checked="form.is_published"
                checked-children="發布"
                un-checked-children="草稿"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="分類" name="category_ids">
              <a-select
                v-model:value="form.category_ids"
                mode="multiple"
                placeholder="選擇分類"
              >
                <a-select-option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="標籤" name="tag_ids">
              <a-select
                v-model:value="form.tag_ids"
                mode="multiple"
                placeholder="選擇標籤"
              >
                <a-select-option v-for="tag in tags" :key="tag.id" :value="tag.id">
                  {{ tag.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="特色圖片" name="featured_image">
          <div class="space-y-3">
            <!-- 圖片預覽 -->
            <div v-if="form.featured_image" class="relative inline-block">
              <img 
                :src="form.featured_image" 
                alt="特色圖片預覽" 
                class="w-32 h-32 object-cover rounded-lg border border-gray-200"
                @error="handleImageError"
              />
              <a-button 
                type="text" 
                danger 
                size="small"
                class="absolute -top-2 -right-2 bg-white rounded-full shadow"
                @click="removeImage"
              >
                <DeleteOutlined />
              </a-button>
            </div>
            
            <!-- 圖片上傳 -->
            <div class="flex gap-2">
              <a-upload
                :show-upload-list="false"
                :before-upload="beforeUpload"
                @change="handleUploadChange"
                accept="image/*"
                action="/api/admin/upload/image"
                :headers="{ 'Authorization': `Bearer ${authStore.token}` }"
                name="file"
              >
                <a-button type="default">
                  <UploadOutlined />
                  選擇圖片
                </a-button>
              </a-upload>
              
              <!-- 手動輸入URL -->
              <a-input
                v-model:value="imageUrlInput"
                placeholder="或輸入圖片URL"
                class="flex-1"
                @blur="handleImageUrlInput"
              />
            </div>
            
            <!-- 上傳進度 -->
            <a-progress
              v-if="uploadProgress > 0 && uploadProgress < 100"
              :percent="uploadProgress"
              size="small"
            />
          </div>
        </a-form-item>

        <a-form-item label="文章摘要" name="excerpt">
          <a-textarea
            v-model:value="form.excerpt"
            placeholder="請輸入文章摘要"
            :rows="3"
          />
        </a-form-item>

        <a-form-item label="文章內容" name="content">
          <a-textarea
            v-model:value="form.content"
            placeholder="請輸入文章內容（支援HTML）"
            :rows="10"
          />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="SEO標題" name="meta_title">
              <a-input v-model:value="form.meta_title" placeholder="請輸入SEO標題" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="SEO描述" name="meta_description">
              <a-textarea
                v-model:value="form.meta_description"
                placeholder="請輸入SEO描述"
                :rows="2"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  UploadOutlined
} from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

// 數據
const posts = ref([])
const categories = ref([])
const tags = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const modalVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const imageUrlInput = ref('')
const uploadProgress = ref(0)

// 搜尋表單
const searchForm = reactive({
  search: '',
  published: undefined,
  category_id: undefined
})

// 分頁配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 項，共 ${total} 項`
})

const paginationConfig = computed(() => ({
  ...pagination,
  onChange: (page, pageSize) => {
    pagination.current = page
    pagination.pageSize = pageSize
    fetchPosts()
  },
  onShowSizeChange: (current, size) => {
    pagination.current = 1
    pagination.pageSize = size
    fetchPosts()
  }
}))

// 表格欄位
const columns = [
  {
    title: '文章標題',
    key: 'title',
    width: '30%'
  },
  {
    title: '狀態',
    key: 'is_published',
    width: '80px'
  },
  {
    title: '分類',
    key: 'categories',
    width: '150px'
  },
  {
    title: '標籤',
    key: 'tags',
    width: '150px'
  },
  {
    title: '創建時間',
    key: 'created_at',
    width: '150px'
  },
  {
    title: '操作',
    key: 'action',
    width: '100px'
  }
]

// 表單數據
const form = reactive({
  title: '',
  content: '',
  excerpt: '',
  featured_image: '',
  is_published: false,
  meta_title: '',
  meta_description: '',
  category_ids: [],
  tag_ids: []
})

// 表單驗證規則
const rules = {
  title: [
    { required: true, message: '請輸入文章標題', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '請輸入文章內容', trigger: 'blur' }
  ]
}

// 初始化
onMounted(() => {
  fetchPosts()
  fetchCategories()
  fetchTags()
})

// 獲取文章列表
const fetchPosts = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      skip: ((pagination.current - 1) * pagination.pageSize).toString(),
      limit: pagination.pageSize.toString()
    })

    if (searchForm.search) {
      params.append('search', searchForm.search)
    }
    if (searchForm.published !== undefined) {
      params.append('published', searchForm.published.toString())
    }
    if (searchForm.category_id) {
      params.append('category_id', searchForm.category_id.toString())
    }

    const response = await fetch(`/api/admin/posts?${params}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      posts.value = data
      // 注意：這裡假設後端沒有返回總數，實際使用時可能需要調整
      pagination.total = data.length >= pagination.pageSize ? 
        (pagination.current * pagination.pageSize) + 1 : 
        (pagination.current - 1) * pagination.pageSize + data.length
    } else {
      message.error('獲取文章列表失敗')
    }
  } catch (error) {
    console.error('獲取文章列表錯誤:', error)
    message.error('獲取文章列表失敗')
  } finally {
    loading.value = false
  }
}

// 獲取分類列表
const fetchCategories = async () => {
  try {
    const response = await fetch('/api/categories')
    if (response.ok) {
      const data = await response.json()
      categories.value = data
    }
  } catch (error) {
    console.error('獲取分類列表錯誤:', error)
  }
}

// 獲取標籤列表
const fetchTags = async () => {
  try {
    const response = await fetch('/api/tags')
    if (response.ok) {
      const data = await response.json()
      tags.value = data
    }
  } catch (error) {
    console.error('獲取標籤列表錯誤:', error)
  }
}

// 搜尋處理
const handleSearch = () => {
  pagination.current = 1
  fetchPosts()
}

// 重置搜尋
const resetSearch = () => {
  searchForm.search = ''
  searchForm.published = undefined
  searchForm.category_id = undefined
  pagination.current = 1
  fetchPosts()
}

// 表格變化處理
const handleTableChange = (pag, filters, sorter) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchPosts()
}

// 新增文章
const handleCreate = () => {
  isEdit.value = false
  resetForm()
  modalVisible.value = true
}

// 編輯文章
const handleEdit = (record) => {
  isEdit.value = true
  Object.assign(form, {
    ...record,
    category_ids: record.categories.map(cat => cat.id),
    tag_ids: record.tags.map(tag => tag.id)
  })
  imageUrlInput.value = record.featured_image || ''
  modalVisible.value = true
}

// 刪除文章
const handleDelete = async (id) => {
  try {
    const response = await fetch(`/api/admin/posts/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (response.ok) {
      message.success('刪除成功')
      fetchPosts()
    } else {
      message.error('刪除失敗')
    }
  } catch (error) {
    console.error('刪除文章錯誤:', error)
    message.error('刪除失敗')
  }
}

// 提交表單
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true

    const url = isEdit.value ? `/api/admin/posts/${form.id}` : '/api/admin/posts'
    const method = isEdit.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(form)
    })

    if (response.ok) {
      message.success(isEdit.value ? '更新成功' : '創建成功')
      modalVisible.value = false
      fetchPosts()
    } else {
      const errorData = await response.json()
      message.error(errorData.detail || (isEdit.value ? '更新失敗' : '創建失敗'))
    }
  } catch (error) {
    console.error('提交表單錯誤:', error)
    message.error(isEdit.value ? '更新失敗' : '創建失敗')
  } finally {
    submitLoading.value = false
  }
}

// 取消操作
const handleCancel = () => {
  modalVisible.value = false
  resetForm()
}

// 重置表單
const resetForm = () => {
  Object.assign(form, {
    title: '',
    content: '',
    excerpt: '',
    featured_image: '',
    is_published: false,
    meta_title: '',
    meta_description: '',
    category_ids: [],
    tag_ids: []
  })
  imageUrlInput.value = ''
  uploadProgress.value = 0
  formRef.value?.resetFields()
}

// 格式化日期時間
const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW') + ' ' + date.toLocaleTimeString('zh-TW', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 處理圖片上傳
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('只能上傳圖片')
    return false
  }
  return true
}

const handleUploadChange = async (info) => {
  if (info.file.status === 'uploading') {
    uploadProgress.value = info.file.percent || 0
  } else if (info.file.status === 'done') {
    uploadProgress.value = 100
    setTimeout(() => {
      uploadProgress.value = 0
    }, 1000)
    
    // 處理上傳結果
    if (info.file.response && info.file.response.success) {
      form.featured_image = info.file.response.url
      imageUrlInput.value = info.file.response.url
      message.success('圖片上傳成功')
    } else {
      message.error('圖片上傳失敗')
    }
  } else if (info.file.status === 'error') {
    uploadProgress.value = 0
    message.error('圖片上傳失敗')
  }
}

const handleImageError = () => {
  message.error('圖片加載失敗')
}

const removeImage = () => {
  form.featured_image = ''
}

const handleImageUrlInput = () => {
  form.featured_image = imageUrlInput.value
}
</script>

<style scoped>
.ant-table-tbody > tr > td {
  padding: 12px 16px;
}

.ant-typography-title {
  margin-bottom: 0 !important;
}

.text-sm {
  font-size: 12px;
}
</style> 