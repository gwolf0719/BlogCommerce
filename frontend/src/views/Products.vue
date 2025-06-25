<template>
  <div class="products-page">
    <!-- 頁面標題 -->
    <a-page-header 
      title="商品管理" 
      sub-title="管理您的電商商品庫存"
      class="page-header"
    >
      <template #extra>
        <a-button type="primary" @click="showCreateModal" size="large">
          <PlusOutlined /> 新增商品
        </a-button>
      </template>
    </a-page-header>

    <!-- 統計卡片 -->
    <a-row :gutter="24" class="stats-row">
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="總商品數"
            :value="products.length"
            prefix="🛍️"
            :value-style="{ color: '#1890ff' }"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="啟用商品"
            :value="activeCount"
            prefix="✅"
            :value-style="{ color: '#52c41a' }"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="推薦商品"
            :value="featuredCount"
            prefix="⭐"
            :value-style="{ color: '#faad14' }"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="總庫存值"
            :value="totalStockValue"
            prefix="💰"
            :precision="2"
            :value-style="{ color: '#722ed1' }"
          />
        </a-card>
      </a-col>
    </a-row>

    <!-- 搜尋和篩選區塊 -->
    <a-card title="搜尋與篩選" class="filter-card">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="搜尋商品">
          <a-input-search
            v-model:value="searchForm.search"
            placeholder="搜尋商品名稱或描述"
            allow-clear
            enter-button
            @search="handleSearch"
            style="width: 280px"
          />
        </a-form-item>
        
        <a-form-item label="商品狀態">
          <a-select
            v-model:value="searchForm.status"
            placeholder="選擇狀態"
            style="width: 140px"
            allow-clear
            @change="handleSearch"
          >
            <a-select-option value="active">
              <a-tag color="green" size="small">啟用</a-tag>
            </a-select-option>
            <a-select-option value="inactive">
              <a-tag color="red" size="small">停用</a-tag>
            </a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="推薦篩選">
          <a-select
            v-model:value="searchForm.featured"
            placeholder="推薦狀態"
            style="width: 120px"
            allow-clear
            @change="handleSearch"
          >
            <a-select-option value="true">推薦</a-select-option>
            <a-select-option value="false">一般</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item>
          <a-button @click="resetFilters" icon="reload">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 商品列表區塊 -->
    <a-card title="商品列表" class="table-card">
      <a-table
        :columns="columns"
        :data-source="products"
        :loading="loading"
        :pagination="paginationConfig"
        @change="handleTableChange"
        row-key="id"
        :scroll="{ x: 1000 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'image'">
            <div class="product-image">
              <a-image
                :src="record.featured_image || '/static/images/default-product.jpg'"
                :alt="record.name"
                width="60"
                height="60"
                :preview="true"
                fallback="/static/images/default-product.jpg"
              />
            </div>
          </template>

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

          <template v-if="column.key === 'name'">
            <div class="product-info">
              <div class="product-name">{{ record.name }}</div>
              <div class="product-sku" v-if="record.sku">
                <a-tag size="small">SKU: {{ record.sku }}</a-tag>
              </div>
              <div class="product-description" v-if="record.short_description">
                {{ record.short_description.substring(0, 50) }}{{ record.short_description.length > 50 ? '...' : '' }}
              </div>
            </div>
          </template>

          <template v-if="column.key === 'featured'">
            <a-tag :color="record.is_featured ? 'gold' : 'default'" size="default">
              <template #icon>
                <span>{{ record.is_featured ? '⭐' : '📦' }}</span>
              </template>
              {{ record.is_featured ? '推薦' : '一般' }}
            </a-tag>
          </template>

          <template v-if="column.key === 'status'">
            <a-tag :color="record.is_active ? 'green' : 'red'" size="default">
              <template #icon>
                <span>{{ record.is_active ? '✅' : '❌' }}</span>
              </template>
              {{ record.is_active ? '啟用' : '停用' }}
            </a-tag>
          </template>

          <template v-if="column.key === 'price'">
            <div class="price-cell">
              <div v-if="record.sale_price" class="sale-price">
                特價: ${{ record.sale_price }}
              </div>
              <div :class="{ 'original-price': record.sale_price, 'regular-price': !record.sale_price }">
                {{ record.sale_price ? '原價:' : '價格:' }} ${{ record.price }}
              </div>
            </div>
          </template>

          <template v-if="column.key === 'stock'">
            <div class="stock-cell">
              <a-tag 
                :color="getStockColor(record.stock_quantity)"
                size="default"
              >
                {{ record.stock_quantity }} 件
              </a-tag>
            </div>
          </template>

          <template v-if="column.key === 'actions'">
            <a-space>
              <a-button size="small" type="primary" @click="editProduct(record)">
                <EditOutlined /> 編輯
              </a-button>
              <a-popconfirm
                title="確定要刪除這個商品嗎？"
                description="此操作不可恢復，請謹慎操作"
                @confirm="deleteProduct(record.id)"
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

    <!-- 新增/編輯商品對話框 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEditing ? '編輯商品' : '新增商品'"
      width="1200px"
      :footer="null"
      @cancel="handleCancel"
      class="product-modal"
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
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="商品名稱" name="name">
                <a-input 
                  v-model:value="form.name" 
                  placeholder="請輸入商品名稱"
                  show-count
                  :maxlength="100"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="商品編號" name="sku">
                <a-input 
                  v-model:value="form.sku" 
                  placeholder="可選，用於庫存管理"
                />
              </a-form-item>
            </a-col>
          </a-row>

          <a-form-item label="商品描述" name="description">
            <a-textarea 
              v-model:value="form.description" 
              :rows="4" 
              placeholder="詳細商品描述"
              show-count
              :maxlength="1000"
            />
          </a-form-item>

          <a-form-item label="簡短描述" name="short_description">
            <a-textarea 
              v-model:value="form.short_description" 
              :rows="2" 
              placeholder="用於商品列表顯示的簡短描述"
              show-count
              :maxlength="200"
            />
          </a-form-item>
        </a-card>

        <!-- 價格庫存 -->
        <a-card title="價格與庫存" size="small" class="form-card">
          <a-row :gutter="24">
            <a-col :span="8">
              <a-form-item label="商品價格" name="price" :label-col="{ span: 8 }" :wrapper-col="{ span: 16 }">
                <a-input-number
                  v-model:value="form.price"
                  :min="0"
                  :precision="2"
                  style="width: 100%"
                  placeholder="0.00"
                  addon-before="$"
                />
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="特價" name="sale_price" :label-col="{ span: 8 }" :wrapper-col="{ span: 16 }">
                <a-input-number
                  v-model:value="form.sale_price"
                  :min="0"
                  :precision="2"
                  style="width: 100%"
                  placeholder="可選"
                  addon-before="$"
                />
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="庫存數量" name="stock_quantity" :label-col="{ span: 8 }" :wrapper-col="{ span: 16 }">
                <a-input-number
                  v-model:value="form.stock_quantity"
                  :min="0"
                  style="width: 100%"
                  placeholder="0"
                />
              </a-form-item>
            </a-col>
          </a-row>
        </a-card>

        <!-- 圖片設定 -->
        <a-card title="圖片設定" size="small" class="form-card">
          <a-form-item label="特色圖片" name="featured_image">
            <UploadImage v-model="form.featured_image" />
          </a-form-item>

          <a-form-item label="相冊圖片" name="gallery_images">
            <a-textarea
              v-model:value="form.gallery_images"
              placeholder='多個圖片URL，JSON格式：["url1", "url2"]'
              :rows="2"
            />
            <div class="form-help-text">
              <small class="text-gray-500">請輸入JSON格式的圖片URL陣列</small>
            </div>
          </a-form-item>
        </a-card>

        <!-- 商品設定 -->
        <a-card title="商品設定" size="small" class="form-card">
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item name="is_active" :wrapper-col="{ offset: 4, span: 20 }">
                <a-checkbox v-model:checked="form.is_active" size="large">
                  <ShopOutlined /> 啟用商品（在前台顯示）
                </a-checkbox>
              </a-form-item>
            </a-col>
            <a-col :span="12">
                             <a-form-item name="is_featured" :wrapper-col="{ offset: 4, span: 20 }">
                 <a-checkbox v-model:checked="form.is_featured" size="large">
                   <StarOutlined /> 推薦商品（首頁展示）
                 </a-checkbox>
               </a-form-item>
             </a-col>
           </a-row>
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
              <SaveOutlined /> {{ isEditing ? '更新商品' : '新增商品' }}
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
  ShopOutlined,
  StarOutlined,
  SaveOutlined
} from '@ant-design/icons-vue'
import axios from '../utils/axios'
import UploadImage from '../components/UploadImage.vue'

// 響應式數據
const products = ref([])
const loading = ref(false)
const modalVisible = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const formRef = ref()

// 搜尋表單
const searchForm = reactive({
  search: '',
  status: undefined,
  featured: undefined
})

// 分頁
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true
})

// 計算統計數據
const activeCount = computed(() => 
  products.value.filter(product => product.is_active).length
)
const featuredCount = computed(() => 
  products.value.filter(product => product.is_featured).length
)
const totalStockValue = computed(() => 
  products.value.reduce((total, product) => {
    const price = product.sale_price || product.price || 0
    return total + (price * (product.stock_quantity || 0))
  }, 0)
)

// 分頁設定
const paginationConfig = computed(() => ({
  ...pagination,
  showTotal: (total, range) => `顯示 ${range[0]}-${range[1]} 項，共 ${total} 項`,
  pageSizeOptions: ['10', '20', '50', '100'],
  showSizeChanger: true,
  showQuickJumper: true
}))

// 庫存顏色判斷
const getStockColor = (quantity) => {
  if (quantity === 0) return 'red'
  if (quantity < 10) return 'orange'
  if (quantity < 50) return 'blue'
  return 'green'
}

// 表格欄位
const columns = [
  {
    title: '商品圖片',
    key: 'image',
    width: 80
  },
  {
    title: '商品信息',
    key: 'name',
    width: 250
  },
  {
    title: '瀏覽量',
    key: 'view_count',
    width: 100,
    sorter: true
  },
  {
    title: '價格',
    key: 'price',
    width: 120,
    sorter: true
  },
  {
    title: '庫存',
    key: 'stock',
    width: 100,
    sorter: true
  },
  {
    title: '推薦',
    key: 'featured',
    width: 100,
    filters: [
      { text: '推薦', value: true },
      { text: '一般', value: false }
    ]
  },
  {
    title: '狀態',
    key: 'status',
    width: 100,
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

// 表單數據
const form = reactive({
  name: '',
  description: '',
  short_description: '',
  price: null,
  sale_price: null,
  stock_quantity: 0,
  sku: '',
  featured_image: '',
  gallery_images: '',
  is_active: true,
  is_featured: false,
  meta_title: '',
  meta_description: ''
})

// 表單驗證規則
const rules = {
  name: [
    { required: true, message: '請輸入商品名稱' },
    { min: 2, max: 100, message: '商品名稱長度應在2-100字符之間' }
  ],
  description: [
    { required: true, message: '請輸入商品描述' },
    { min: 10, message: '商品描述至少需要10個字符' }
  ],
  price: [
    { required: true, message: '請輸入商品價格' },
    { type: 'number', min: 0, message: '價格不能為負數' }
  ],
  stock_quantity: [
    { required: true, message: '請輸入庫存數量' },
    { type: 'number', min: 0, message: '庫存數量不能為負數' }
  ]
}

// 載入商品列表
const loadProducts = async () => {
  try {
    loading.value = true
    const params = new URLSearchParams()
    
    if (searchForm.search) params.append('search', searchForm.search)
    if (searchForm.status === 'active') params.append('active_only', 'true')
    if (searchForm.status === 'inactive') params.append('active_only', 'false')
    if (searchForm.featured !== undefined) params.append('featured', searchForm.featured)
    
    params.append('skip', ((pagination.current - 1) * pagination.pageSize).toString())
    params.append('limit', pagination.pageSize.toString())
    
    const response = await axios.get(`/api/products?${params}`)
    products.value = response.data
    // 注意：實際應用中可能需要從響應頭或其他方式獲取總數
    // pagination.total = response.headers['x-total-count'] || products.value.length
  } catch (error) {
    console.error('載入商品列表錯誤:', error)
    message.error('載入商品列表失敗')
  } finally {
    loading.value = false
  }
}

// 搜尋處理
const handleSearch = () => {
  pagination.current = 1
  loadProducts()
}

// 重置篩選
const resetFilters = () => {
  Object.assign(searchForm, { search: '', status: undefined, featured: undefined })
  pagination.current = 1
  loadProducts()
}

// 表格變化處理
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadProducts()
}

// 顯示新增對話框
const showCreateModal = () => {
  isEditing.value = false
  modalVisible.value = true
  resetForm()
}

// 編輯商品
const editProduct = (product) => {
  isEditing.value = true
  modalVisible.value = true
  Object.assign(form, product)
}

// 重置表單
const resetForm = () => {
  Object.assign(form, {
    name: '', description: '', short_description: '', price: null, sale_price: null,
    stock_quantity: 0, sku: '', featured_image: '', gallery_images: '', is_active: true, is_featured: false, meta_title: '', meta_description: ''
  })
}

// 提交表單
const handleSubmit = async () => {
  try {
    submitting.value = true
    await formRef.value.validate()
    
    const data = { ...form }
    
    if (isEditing.value) {
      await axios.put(`/api/products/${form.id}`, data)
      message.success('商品更新成功')
    } else {
      await axios.post('/api/products', data)
      message.success('商品新增成功')
    }
    
    modalVisible.value = false
    loadProducts()
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

// 刪除商品
const deleteProduct = async (id) => {
  try {
    await axios.delete(`/api/products/${id}`)
    message.success('商品刪除成功')
    loadProducts()
  } catch (error) {
    console.error('刪除失敗:', error)
    message.error('刪除失敗')
  }
}

// 掛載時載入數據
onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.products-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filters {
  margin-bottom: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
}

.sale-price {
  color: #f5222d;
  font-weight: bold;
  margin-right: 8px;
}

.original-price {
  text-decoration: line-through;
  color: #999;
}

.stats-row {
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.product-image {
  width: 60px;
  height: 60px;
  overflow: hidden;
  border-radius: 4px;
  margin-right: 16px;
}

.product-info {
  display: flex;
  flex-direction: column;
}

.product-name {
  font-weight: bold;
}

.product-sku {
  margin-top: 4px;
}

.product-description {
  margin-top: 4px;
  color: #999;
}

.price-cell {
  display: flex;
  flex-direction: column;
}

.stock-cell {
  margin-top: 4px;
}

.form-card {
  margin-bottom: 20px;
}

.form-actions {
  margin-top: 20px;
  text-align: right;
}

.product-modal {
  width: 1200px;
}

.form-help-text {
  margin-top: 8px;
  text-align: right;
}
</style> 