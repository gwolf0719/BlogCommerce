<template>
  <div class="admin-page">
    <!-- 1. 頁面標題區 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">廣告管理</h1>
          <p class="page-description">管理網站輪播廣告和推廣橫幅</p>
        </div>
        <div class="action-section">
          <a-button type="primary" @click="showCreateModal">
            <template #icon><PlusOutlined /></template>
            新增廣告
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
              title="總廣告數"
              :value="banners.length"
              prefix="🎯"
              :value-style="{ color: '#1890ff' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="啟用廣告"
              :value="activeCount"
              prefix="✅"
              :value-style="{ color: '#52c41a' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="總點擊數"
              :value="totalClicks"
              prefix="👆"
              :value-style="{ color: '#faad14' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="點擊率"
              :value="clickRate"
              suffix="%"
              prefix="📊"
              :precision="2"
              :value-style="{ color: '#722ed1' }"
            />
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 3. 搜尋篩選區 -->
    <div class="search-section">
      <a-card>
        <a-row :gutter="24">
          <a-col :span="6">
            <a-input
              v-model:value="searchForm.search"
              placeholder="搜尋廣告標題"
              allow-clear
              @change="handleSearch"
            >
              <template #prefix>
                <search-outlined />
              </template>
            </a-input>
          </a-col>
          <a-col :span="4">
            <a-select
              v-model:value="searchForm.position"
              placeholder="選擇位置"
              allow-clear
              @change="handleSearch"
            >
              <a-select-option value="HOME">首頁</a-select-option>
              <a-select-option value="BLOG_LIST">文章列表</a-select-option>
              <a-select-option value="PRODUCT_LIST">商品列表</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="4">
            <a-select
              v-model:value="searchForm.is_active"
              placeholder="選擇狀態"
              allow-clear
              @change="handleSearch"
            >
              <a-select-option :value="true">啟用</a-select-option>
              <a-select-option :value="false">停用</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="6">
            <a-range-picker
              v-model:value="searchForm.dateRange"
              :placeholder="['開始時間', '結束時間']"
              @change="handleSearch"
            />
          </a-col>
          <a-col :span="4">
            <a-space>
              <a-button @click="handleSearch">
                <template #icon><SearchOutlined /></template>
                搜尋
              </a-button>
              <a-button @click="resetSearch">
                重置
              </a-button>
            </a-space>
          </a-col>
        </a-row>
      </a-card>
    </div>

    <!-- 4. 表格區 -->
    <div class="table-section">
      <a-card>
        <a-table
          :columns="columns"
          :data-source="banners"
          :loading="loading"
          :pagination="paginationConfig"
          :row-key="record => record.id"
          @change="handleTableChange"
        >
          <!-- 廣告圖片 -->
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'image'">
              <div class="banner-image">
                <div v-if="record.desktop_image || record.mobile_image" class="image-preview">
                  <img
                    v-if="record.desktop_image"
                    :src="getImageUrl(record.desktop_image)"
                    :alt="record.title"
                    class="banner-thumbnail desktop-img"
                    title="桌面版"
                  />
                  <img
                    v-if="record.mobile_image"
                    :src="getImageUrl(record.mobile_image)"
                    :alt="record.title"
                    class="banner-thumbnail mobile-img"
                    title="手機版"
                  />
                </div>
                <div v-else class="no-image">
                  <picture-outlined />
                  <div class="no-image-text">未設定圖片</div>
                </div>
              </div>
            </template>

            <!-- 廣告信息 -->
            <template v-else-if="column.key === 'title'">
              <div class="banner-info">
                <div class="banner-title">{{ record.title }}</div>
                <div class="banner-meta">
                  <span class="position-tag">
                    <a-tag :color="getPositionColor(record.position)">
                      {{ getPositionText(record.position) }}
                    </a-tag>
                  </span>
                  <span class="date-range">
                    {{ formatDate(record.start_date) }} - {{ formatDate(record.end_date) }}
                  </span>
                </div>
              </div>
            </template>

            <!-- 點擊數 -->
            <template v-else-if="column.key === 'clicks'">
              <div class="click-stats">
                <div class="click-count">{{ record.click_count || 0 }}</div>
                <div class="view-count">瀏覽: {{ record.view_count || 0 }}</div>
              </div>
            </template>

            <!-- 狀態 -->
            <template v-else-if="column.key === 'status'">
              <div class="status-cell">
                <a-switch
                  v-model:checked="record.is_active"
                  :loading="record.updating"
                  @change="toggleStatus(record)"
                />
                <a-tag v-if="!isValidPeriod(record)" color="orange">
                  已過期
                </a-tag>
              </div>
            </template>

            <!-- 操作 -->
            <template v-else-if="column.key === 'actions'">
              <a-space>
                <a-button
                  type="primary"
                  size="small"
                  @click="editBanner(record)"
                >
                  <template #icon><EditOutlined /></template>
                  編輯
                </a-button>
                <a-popconfirm
                  title="確定要刪除這個廣告嗎？"
                  @confirm="deleteBanner(record.id)"
                >
                  <a-button
                    type="primary"
                    danger
                    size="small"
                  >
                    <template #icon><DeleteOutlined /></template>
                    刪除
                  </a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>

    <!-- 5. 新增/編輯彈窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEditing ? '編輯廣告' : '新增廣告'"
      :width="800"
      :confirm-loading="submitting"
      @ok="handleSubmit"
      @cancel="handleCancel"
    >
      <a-form
        ref="formRef"
        :model="form"
        :rules="rules"
        layout="vertical"
        @finish="handleSubmit"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="廣告標題" name="title">
              <a-input
                v-model:value="form.title"
                placeholder="請輸入廣告標題"
                :maxlength="100"
                show-count
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="顯示位置" name="position">
              <a-select v-model:value="form.position" placeholder="選擇顯示位置">
                <a-select-option value="HOME">首頁</a-select-option>
                <a-select-option value="BLOG_LIST">文章列表</a-select-option>
                <a-select-option value="PRODUCT_LIST">商品列表</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="廣告描述" name="description">
          <a-textarea
            v-model:value="form.description"
            placeholder="請輸入廣告描述"
            :rows="3"
            :maxlength="500"
            show-count
          />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="電腦版圖片" name="desktop_image">
              <upload-image 
                v-model="form.desktop_image" 
              />
              <div style="margin-top: 8px; font-size: 12px; color: #666;">
                建議尺寸：1920×600px
              </div>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="手機版圖片" name="mobile_image">
              <upload-image 
                v-model="form.mobile_image" 
              />
              <div style="margin-top: 8px; font-size: 12px; color: #666;">
                建議尺寸：750×300px
              </div>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="連結網址" name="link_url">
          <a-input
            v-model:value="form.link_url"
            placeholder="請輸入連結網址 (可選)"
            type="url"
          />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="開始時間" name="start_date">
              <a-date-picker
                v-model:value="form.start_date"
                style="width: 100%"
                placeholder="選擇開始時間"
                show-time
                format="YYYY-MM-DD HH:mm:ss"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="結束時間" name="end_date">
              <a-date-picker
                v-model:value="form.end_date"
                style="width: 100%"
                placeholder="選擇結束時間"
                show-time
                format="YYYY-MM-DD HH:mm:ss"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="排序順序" name="sort_order">
              <a-input-number
                v-model:value="form.sort_order"
                :min="0"
                :max="9999"
                placeholder="排序順序"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="狀態" name="is_active">
              <a-switch
                v-model:checked="form.is_active"
                checked-children="啟用"
                un-checked-children="停用"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick, watch } from 'vue'
import { message } from 'ant-design-vue'
import { 
  PlusOutlined, 
  SearchOutlined, 
  EditOutlined, 
  DeleteOutlined,
  PictureOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'
import UploadImage from '../components/UploadImage.vue'
import dayjs from 'dayjs'

const authStore = useAuthStore()
const loading = ref(false)
const modalVisible = ref(false)
const submitting = ref(false)
const isEditing = ref(false)
const formRef = ref()

// 數據
const banners = ref([])
const stats = ref({
  totalClicks: 0,
  totalViews: 0,
  clickRate: 0
})

// 搜尋表單
const searchForm = reactive({
  search: '',
  position: undefined,
  is_active: undefined,
  dateRange: []
})

// 表單
const form = reactive({
  id: null,
  title: '',
  description: '',
  mobile_image: '',
  desktop_image: '',
  link_url: '',
  position: 'HOME',
  start_date: null,
  end_date: null,
  sort_order: 0,
  is_active: true
})

// 分頁
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 項，共 ${total} 項`
})

// 計算屬性
const activeCount = computed(() => 
  banners.value.filter(banner => banner.is_active).length
)

const totalClicks = computed(() => 
  banners.value.reduce((sum, banner) => sum + (banner.click_count || 0), 0)
)

const clickRate = computed(() => {
  const totalViews = banners.value.reduce((sum, banner) => sum + (banner.view_count || 0), 0)
  return totalViews > 0 ? (totalClicks.value / totalViews) * 100 : 0
})

const paginationConfig = computed(() => ({
  current: pagination.current,
  pageSize: pagination.pageSize,
  total: pagination.total,
  showSizeChanger: pagination.showSizeChanger,
  showQuickJumper: pagination.showQuickJumper,
  showTotal: pagination.showTotal
}))

// 表格列定義
const columns = [
  {
    title: '廣告圖片',
    key: 'image',
    width: 80
  },
  {
    title: '廣告信息',
    key: 'title',
    width: 250
  },
  {
    title: '點擊統計',
    key: 'clicks',
    width: 120,
    sorter: true
  },
  {
    title: '狀態',
    key: 'status',
    width: 120,
    filters: [
      { text: '啟用', value: true },
      { text: '停用', value: false }
    ]
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    fixed: 'right'
  }
]

// 表單驗證規則
const rules = {
  title: [
    { required: true, message: '請輸入廣告標題' },
    { min: 2, max: 100, message: '標題長度應在2-100字符之間' }
  ],
  position: [
    { required: true, message: '請選擇顯示位置' }
  ],
  mobile_image: [
    { required: true, message: '請上傳手機版圖片' }
  ],
  desktop_image: [
    { required: true, message: '請上傳電腦版圖片' }
  ],
  start_date: [
    { required: true, message: '請選擇開始時間' }
  ],
  end_date: [
    { required: true, message: '請選擇結束時間' }
  ]
}

// 載入廣告列表
const loadBanners = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    
    if (searchForm.search) {
      params.append('search', searchForm.search)
    }
    if (searchForm.position) {
      params.append('position', searchForm.position)
    }
    if (searchForm.is_active !== undefined) {
      params.append('is_active', searchForm.is_active)
    }
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.append('start_date', searchForm.dateRange[0].format('YYYY-MM-DD'))
      params.append('end_date', searchForm.dateRange[1].format('YYYY-MM-DD'))
    }

    params.append('page', pagination.current)
    params.append('size', pagination.pageSize)

    const response = await fetch(`/api/banners?${params}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!response.ok) {
      // 嘗試解析API錯誤響應
      let errorMessage = '載入廣告失敗'
      
      try {
        const errorData = await response.json()
        
        // 處理 FastAPI 驗證錯誤格式
        if (errorData.detail && Array.isArray(errorData.detail)) {
          const errors = errorData.detail.map(err => err.msg || err.message || '未知錯誤')
          errorMessage = errors.join(', ')
        } else if (errorData.detail && typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        } else if (errorData.message) {
          errorMessage = errorData.message
        } else if (errorData.msg) {
          errorMessage = errorData.msg
        }
      } catch (parseError) {
        console.error('解析錯誤響應失敗:', parseError)
      }
      
      throw new Error(errorMessage)
    }

    const data = await response.json()
    banners.value = data.items || data
    pagination.total = data.total || data.length

  } catch (error) {
    console.error('載入廣告失敗:', error)
    message.error(error.message)
  } finally {
    loading.value = false
  }
}

// 搜尋處理
const handleSearch = () => {
  pagination.current = 1
  loadBanners()
}

// 重置搜尋
const resetSearch = () => {
  searchForm.search = ''
  searchForm.position = undefined
  searchForm.is_active = undefined
  searchForm.dateRange = []
  handleSearch()
}

// 表格變更處理
const handleTableChange = (paginationInfo, filters, sorter) => {
  pagination.current = paginationInfo.current
  pagination.pageSize = paginationInfo.pageSize
  loadBanners()
}

// 顯示新增彈窗
const showCreateModal = () => {
  resetForm()
  isEditing.value = false
  modalVisible.value = true
}

// 編輯廣告
const editBanner = (record) => {
  resetForm()
  isEditing.value = true
  form.id = record.id
  form.title = record.title
  form.description = record.description || ''
  form.mobile_image = record.mobile_image || ''
  form.desktop_image = record.desktop_image || ''
  form.link_url = record.link_url || ''
  form.position = record.position
  form.start_date = record.start_date ? dayjs(record.start_date) : null
  form.end_date = record.end_date ? dayjs(record.end_date) : null
  form.sort_order = record.sort_order || 0
  form.is_active = record.is_active
  modalVisible.value = true
}

// 重置表單
const resetForm = () => {
  form.id = null
  form.title = ''
  form.description = ''
  form.mobile_image = ''
  form.desktop_image = ''
  form.link_url = ''
  form.position = 'HOME'
  form.start_date = null
  form.end_date = null
  form.sort_order = 0
  form.is_active = true
}

// 監聽圖片字段變化，自動處理驗證
watch(() => form.desktop_image, (newValue) => {
  if (newValue) {
    // 有圖片時清除驗證錯誤
    formRef.value?.clearValidate('desktop_image')
  }
})

watch(() => form.mobile_image, (newValue) => {
  if (newValue) {
    // 有圖片時清除驗證錯誤
    formRef.value?.clearValidate('mobile_image')
  }
})

// 提交表單
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    const submitData = {
      title: form.title,
      description: form.description,
      mobile_image: form.mobile_image,
      desktop_image: form.desktop_image,
      link_url: form.link_url,
      position: form.position,
      start_date: form.start_date ? form.start_date.format('YYYY-MM-DD HH:mm:ss') : null,
      end_date: form.end_date ? form.end_date.format('YYYY-MM-DD HH:mm:ss') : null,
      sort_order: form.sort_order,
      is_active: form.is_active
    }

    const url = isEditing.value ? `/api/banners/${form.id}` : '/api/banners'
    const method = isEditing.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(submitData)
    })

    if (!response.ok) {
      // 嘗試解析API錯誤響應
      let errorMessage = isEditing.value ? '更新廣告失敗' : '新增廣告失敗'
      
      try {
        const errorData = await response.json()
        
        // 處理 FastAPI 驗證錯誤格式
        if (errorData.detail && Array.isArray(errorData.detail)) {
          const errors = errorData.detail.map(err => err.msg || err.message || '未知錯誤')
          errorMessage = errors.join(', ')
        } else if (errorData.detail && typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        } else if (errorData.message) {
          errorMessage = errorData.message
        } else if (errorData.msg) {
          errorMessage = errorData.msg
        }
      } catch (parseError) {
        console.error('解析錯誤響應失敗:', parseError)
      }
      
      throw new Error(errorMessage)
    }

    message.success(isEditing.value ? '廣告已更新' : '廣告已新增')
    modalVisible.value = false
    loadBanners()

  } catch (error) {
    console.error('提交失敗:', error)
    message.error(error.message)
  } finally {
    submitting.value = false
  }
}

// 取消編輯
const handleCancel = () => {
  modalVisible.value = false
  resetForm()
}

// 切換狀態
const toggleStatus = async (record) => {
  record.updating = true
  try {
    const response = await fetch(`/api/banners/${record.id}/toggle`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!response.ok) {
      // 嘗試解析API錯誤響應
      let errorMessage = '狀態切換失敗'
      
      try {
        const errorData = await response.json()
        
        // 處理 FastAPI 驗證錯誤格式
        if (errorData.detail && Array.isArray(errorData.detail)) {
          const errors = errorData.detail.map(err => err.msg || err.message || '未知錯誤')
          errorMessage = errors.join(', ')
        } else if (errorData.detail && typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        } else if (errorData.message) {
          errorMessage = errorData.message
        } else if (errorData.msg) {
          errorMessage = errorData.msg
        }
      } catch (parseError) {
        console.error('解析錯誤響應失敗:', parseError)
      }
      
      throw new Error(errorMessage)
    }

    message.success('狀態已更新')
    loadBanners()

  } catch (error) {
    console.error('狀態切換失敗:', error)
    message.error(error.message)
    // 恢復原狀態
    record.is_active = !record.is_active
  } finally {
    record.updating = false
  }
}

// 刪除廣告
const deleteBanner = async (id) => {
  try {
    const response = await fetch(`/api/banners/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!response.ok) {
      // 嘗試解析API錯誤響應
      let errorMessage = '刪除廣告失敗'
      
      try {
        const errorData = await response.json()
        
        // 處理 FastAPI 驗證錯誤格式
        if (errorData.detail && Array.isArray(errorData.detail)) {
          const errors = errorData.detail.map(err => err.msg || err.message || '未知錯誤')
          errorMessage = errors.join(', ')
        } else if (errorData.detail && typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        } else if (errorData.message) {
          errorMessage = errorData.message
        } else if (errorData.msg) {
          errorMessage = errorData.msg
        }
      } catch (parseError) {
        console.error('解析錯誤響應失敗:', parseError)
      }
      
      throw new Error(errorMessage)
    }

    message.success('廣告已刪除')
    loadBanners()

  } catch (error) {
    console.error('刪除廣告失敗:', error)
    message.error(error.message)
  }
}

// 工具函數
const getImageUrl = (imagePath) => {
  if (!imagePath) return ''
  
  // 如果已經是完整的 URL，直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  
  // 如果是相對路徑，加上 baseURL
  const baseURL = 'http://localhost:8002'
  return `${baseURL}${imagePath}`
}

const getPositionColor = (position) => {
  const colors = {
    'HOME': 'blue',
    'BLOG_LIST': 'green',
    'PRODUCT_LIST': 'orange'
  }
  return colors[position] || 'default'
}

const getPositionText = (position) => {
  const texts = {
    'HOME': '首頁',
    'BLOG_LIST': '文章列表',
    'PRODUCT_LIST': '商品列表'
  }
  return texts[position] || position
}

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}

const isValidPeriod = (record) => {
  const now = dayjs()
  const start = dayjs(record.start_date)
  const end = dayjs(record.end_date)
  return now.isAfter(start) && now.isBefore(end)
}

// 生命週期
onMounted(() => {
  loadBanners()
})
</script>

<style scoped>
.admin-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.title-section h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.title-section p {
  margin: 4px 0 0 0;
  color: #666;
}

.stats-section {
  margin-bottom: 24px;
}

.search-section {
  margin-bottom: 24px;
}

.table-section {
  margin-bottom: 24px;
}

.banner-image {
  width: 80px;
  height: 50px;
  border-radius: 4px;
  overflow: hidden;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview {
  display: flex;
  gap: 2px;
  width: 100%;
  height: 100%;
}

.banner-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 2px;
}

.desktop-img {
  border: 1px solid #1890ff;
}

.mobile-img {
  border: 1px solid #52c41a;
}

.no-image {
  color: #ccc;
  font-size: 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.no-image-text {
  font-size: 10px;
  margin-top: 2px;
}

.banner-info {
  padding: 4px 0;
}

.banner-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.banner-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-range {
  color: #666;
  font-size: 12px;
}

.click-stats {
  text-align: center;
}

.click-count {
  font-size: 16px;
  font-weight: 500;
  color: #1890ff;
}

.view-count {
  font-size: 12px;
  color: #666;
}

.status-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style> 