<template>
  <div class="admin-page">
    <!-- 1. 頁面標題區 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">文章管理</h1>
          <p class="page-description">管理您的部落格文章內容</p>
        </div>
        <div class="action-section">
          <a-button type="primary" @click="showCreateModal">
            <template #icon><PlusOutlined /></template>
            新增文章
          </a-button>
        </div>
      </div>
    </div>

    <!-- 2. 統計卡片區 -->
    <div class="stats-section">
      <a-row :gutter="24" class="stats-row">
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="總文章數"
              :value="posts.length"
              prefix="📄"
              :value-style="{ color: '#1890ff' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="已發布"
              :value="publishedCount"
              prefix="✅"
              :value-style="{ color: '#52c41a' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="草稿"
              :value="draftCount"
              prefix="📝"
              :value-style="{ color: '#faad14' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="發布率"
              :value="publishRate"
              suffix="%"
              prefix="📊"
              :precision="1"
              :value-style="{ color: '#722ed1' }"
            />
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 3. 搜尋篩選區 -->
    <div class="filter-section">
      <a-card class="filter-card">
        <a-row :gutter="24">
          <a-col :span="8">
            <a-input-search
              v-model:value="searchForm.search"
              placeholder="搜尋文章標題或內容"
              allow-clear
              @search="handleSearch"
            />
          </a-col>
          <a-col :span="4">
            <a-select
              v-model:value="searchForm.status"
              placeholder="發布狀態"
              allow-clear
              @change="handleSearch"
            >
              <a-select-option value="published">已發布</a-select-option>
              <a-select-option value="draft">草稿</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="4">
            <a-button @click="resetFilters">重置篩選</a-button>
          </a-col>
        </a-row>
      </a-card>
    </div>

    <!-- 4. 主要內容區 -->
    <div class="content-section">
      <a-card class="content-card">
        <a-table
          :columns="columns"
          :data-source="posts"
          :loading="loading"
          :pagination="paginationConfig"
          @change="handleTableChange"
          row-key="id"
          :scroll="{ x: 800 }"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'view_count'">
              <div class="view-count-cell">
                <a-statistic 
                  :value="record.view_count || 0" 
                  :value-style="{ fontSize: '14px' }"
                >
                  <template #suffix>
                    <span style="font-size: 12px; color: #999;">次</span>
                  </template>
                </a-statistic>
              </div>
            </template>

            <template v-if="column.key === 'status'">
              <a-tag :color="record.is_published ? 'green' : 'orange'" size="default">
                <template #icon>
                  <span>{{ record.is_published ? '✅' : '📝' }}</span>
                </template>
                {{ record.is_published ? '已發布' : '草稿' }}
              </a-tag>
            </template>

            <template v-if="column.key === 'title'">
              <div class="title-cell">
                <div class="post-title">{{ record.title }}</div>
                <div class="post-excerpt" v-if="record.excerpt">
                  {{ record.excerpt.substring(0, 50) }}{{ record.excerpt.length > 50 ? '...' : '' }}
                </div>
              </div>
            </template>

            <template v-if="column.key === 'created_at'">
              <div class="date-cell">
                <div>{{ formatDate(record.created_at) }}</div>
                <small class="text-gray-500">{{ formatTime(record.created_at) }}</small>
              </div>
            </template>

            <template v-if="column.key === 'actions'">
              <a-space>
                <a-button size="small" type="primary" @click="editPost(record)">
                  <EditOutlined /> 編輯
                </a-button>
                <a-popconfirm
                  title="確定要刪除這篇文章嗎？"
                  description="此操作不可恢復，請謹慎操作"
                  @confirm="deletePost(record.id)"
                  ok-text="確定"
                  cancel-text="取消"
                >
                  <a-button size="small" danger>
                    <DeleteOutlined /> 刪除
                  </a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>

    <!-- 新增/編輯文章對話框 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEditing ? '編輯文章' : '新增文章'"
      width="1000px"
      :footer="null"
      @cancel="handleCancel"
      class="post-modal"
    >
      <a-form
        :model="form"
        :rules="rules"
        :label-col="{ span: 4 }"
        :wrapper-col="{ span: 20 }"
        ref="formRef"
        layout="horizontal"
      >
        <!-- 基本信息 -->
        <a-card title="基本信息" size="small" class="form-card">
          <a-form-item label="文章標題" name="title">
            <a-input 
              v-model:value="form.title" 
              placeholder="請輸入文章標題"
              show-count
              :maxlength="100"
            />
          </a-form-item>

          <a-form-item label="文章內容" name="content">
            <MarkdownEditor 
              v-model="form.content" 
              :rows="15" 
              placeholder="請輸入文章內容（支援 Markdown 語法）..." 
            />
          </a-form-item>

          <a-form-item label="文章摘要" name="excerpt">
            <a-textarea 
              v-model:value="form.excerpt" 
              :rows="3" 
              placeholder="可選，如果不填寫會自動從內容中提取"
              show-count
              :maxlength="200"
            />
          </a-form-item>

          <a-form-item label="特色圖片" name="featured_image">
            <UploadImage v-model="form.featured_image" />
          </a-form-item>
        </a-card>

        <!-- 發布設定 -->
        <a-card title="發布設定" size="small" class="form-card">
          <a-form-item label="發布狀態" name="is_published">
            <a-radio-group v-model:value="form.is_published" size="large">
              <a-radio-button :value="false">
                <FileTextOutlined /> 保存為草稿
              </a-radio-button>
              <a-radio-button :value="true">
                <CheckCircleOutlined /> 立即發布
              </a-radio-button>
            </a-radio-group>
            <div class="form-help-text">
              <a-alert
                :message="form.is_published ? '文章將立即對外可見' : '草稿不會顯示在前台'"
                :type="form.is_published ? 'info' : 'warning'"
                show-icon
                banner
              />
            </div>
          </a-form-item>
        </a-card>

        <!-- SEO 設定 -->
        <a-card title="SEO 設定" size="small" class="form-card">
          <a-form-item label="SEO 標題" name="meta_title">
            <a-input 
              v-model:value="form.meta_title" 
              placeholder="用於搜尋引擎優化，建議 50-60 個字符"
              show-count
              :maxlength="60"
            />
          </a-form-item>

          <a-form-item label="SEO 描述" name="meta_description">
            <a-textarea 
              v-model:value="form.meta_description" 
              :rows="3" 
              placeholder="用於搜尋引擎優化，建議 150-160 個字符"
              show-count
              :maxlength="160"
            />
          </a-form-item>
        </a-card>

        <!-- 操作按鈕 -->
        <div class="form-actions">
          <a-space>
            <a-button @click="handleCancel" size="large">取消</a-button>
            <a-button type="primary" @click="handleSubmit" :loading="submitting" size="large">
              <SaveOutlined /> {{ isEditing ? '更新文章' : '新增文章' }}
            </a-button>
          </a-space>
        </div>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  SaveOutlined
} from '@ant-design/icons-vue'
import axios from '../utils/axios'
import MarkdownEditor from '../components/MarkdownEditor.vue'
import UploadImage from '../components/UploadImage.vue'
import { formatDate, formatTimeOnly } from '../utils/dateUtils'

// 為了向後兼容，建立 formatTime 別名
const formatTime = formatTimeOnly

// 響應式數據
const posts = ref([])
const loading = ref(false)
const modalVisible = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const formRef = ref()

// 搜尋表單
const searchForm = reactive({
  search: '',
  status: undefined
})

// 分頁
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true
})

// 計算統計數據
const publishedCount = computed(() => 
  posts.value.filter(post => post.is_published).length
)
const draftCount = computed(() => 
  posts.value.filter(post => !post.is_published).length
)
const publishRate = computed(() => 
  posts.value.length > 0 ? (publishedCount.value / posts.value.length) * 100 : 0
)

// 分頁設定
const paginationConfig = computed(() => ({
  ...pagination,
  showTotal: (total, range) => `顯示 ${range[0]}-${range[1]} 項，共 ${total} 項`,
  pageSizeOptions: ['10', '20', '50', '100'],
  showSizeChanger: true,
  showQuickJumper: true
}))

// 表格欄位
const columns = [
  {
    title: '文章標題',
    key: 'title',
    width: 300
  },
  {
    title: '瀏覽量',
    key: 'view_count',
    width: 100,
    sorter: true
  },
  {
    title: '發布狀態',
    key: 'status',
    width: 120,
    filters: [
      { text: '已發布', value: 'published' },
      { text: '草稿', value: 'draft' }
    ]
  },
  {
    title: '建立時間',
    key: 'created_at',
    width: 150,
    sorter: true
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    fixed: 'right'
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
  meta_description: ''
})

// 表單驗證規則
const rules = {
  title: [
    { required: true, message: '請輸入文章標題' },
    { min: 5, max: 100, message: '標題長度應在5-100字符之間' }
  ],
  content: [
    { required: true, message: '請輸入文章內容' },
    { min: 10, message: '內容至少需要10個字符' }
  ]
}

// 載入文章列表
const loadPosts = async () => {
  try {
    loading.value = true
    const params = new URLSearchParams()
    
    if (searchForm.search) params.append('search', searchForm.search)
    
    // 處理發布狀態篩選
    if (searchForm.status === 'published') {
      params.append('published_only', 'true')
    } else if (searchForm.status === 'draft') {
      params.append('published_only', 'false')
    }
    
    params.append('skip', ((pagination.current - 1) * pagination.pageSize).toString())
    params.append('limit', pagination.pageSize.toString())
    
    const response = await axios.get(`/api/posts?${params}`)
    posts.value = response.data
    // 注意：實際應用中可能需要從響應頭或其他方式獲取總數
    // pagination.total = response.headers['x-total-count'] || posts.value.length
  } catch (error) {
    console.error('載入文章列表錯誤:', error)
    message.error('載入文章列表失敗')
  } finally {
    loading.value = false
  }
}

// 搜尋處理
const handleSearch = () => {
  pagination.current = 1
  loadPosts()
}

// 重置篩選
const resetFilters = () => {
  Object.assign(searchForm, { search: '', status: undefined })
  pagination.current = 1
  loadPosts()
}

// 表格變化處理
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadPosts()
}

// 顯示新增對話框
const showCreateModal = () => {
  isEditing.value = false
  modalVisible.value = true
  resetForm()
}

// 編輯文章
const editPost = (post) => {
  isEditing.value = true
  modalVisible.value = true
  Object.assign(form, post)
}

// 重置表單
const resetForm = () => {
  Object.assign(form, {
    title: '', content: '', excerpt: '', featured_image: '', is_published: false, meta_title: '', meta_description: ''
  })
}

// 提交表單
const handleSubmit = async () => {
  try {
    submitting.value = true
    await formRef.value.validate()
    
    const data = { ...form }
    
    if (isEditing.value) {
      await axios.put(`/api/posts/${form.id}`, data)
      message.success('文章更新成功')
    } else {
      await axios.post('/api/posts', data)
      message.success('文章新增成功')
    }
    
    modalVisible.value = false
    loadPosts()
  } catch (error) {
    console.error('操作失敗:', error)
    message.error('操作失敗')
  } finally {
    submitting.value = false
  }
}

// 取消對話框
const handleCancel = () => {
  modalVisible.value = false
  resetForm()
}

// 刪除文章
const deletePost = async (id) => {
  try {
    await axios.delete(`/api/posts/${id}`)
    message.success('文章刪除成功')
    loadPosts()
  } catch (error) {
    console.error('刪除失敗:', error)
    message.error('刪除失敗')
  }
}

// 掛載時載入數據
onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
.admin-page {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #262626;
}

.page-description {
  color: #8c8c8c;
  margin: 0;
  font-size: 14px;
}

.stats-section {
  margin-bottom: 24px;
}

.stats-row {
  margin-bottom: 24px;
}

.filter-section {
  margin-bottom: 24px;
}

.content-section {
  margin-bottom: 24px;
}

.view-count-cell {
  text-align: right;
}

.title-cell {
  display: flex;
  flex-direction: column;
}

.post-title {
  font-weight: bold;
}

.post-excerpt {
  color: #666;
  margin-top: 5px;
}

.date-cell {
  text-align: right;
}

.form-card {
  margin-bottom: 20px;
}

.form-actions {
  text-align: right;
}

.post-modal {
  width: 1000px;
}
</style> 