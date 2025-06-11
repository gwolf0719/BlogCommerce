<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">商品管理</h1>
      <a-button type="primary" @click="handleCreate">
        <template #icon><PlusOutlined /></template>
        新增商品
      </a-button>
    </div>

    <!-- 搜尋與篩選 -->
    <a-card class="mb-6">
      <a-row :gutter="16">
        <a-col :span="8">
          <a-input
            v-model:value="searchForm.search"
            placeholder="搜尋商品名稱 / 描述"
            allowClear
            @change="handleSearch"
          >
            <template #prefix><SearchOutlined /></template>
          </a-input>
        </a-col>
        <a-col :span="6">
          <a-select
            v-model:value="searchForm.category_id"
            placeholder="分類篩選"
            allowClear
            @change="handleSearch"
          >
            <a-select-option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </a-select-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-select
            v-model:value="searchForm.status"
            placeholder="狀態篩選"
            allowClear
            @change="handleSearch"
          >
            <a-select-option value="active">上架</a-select-option>
            <a-select-option value="inactive">下架</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="4">
          <a-button @click="resetSearch">重置</a-button>
        </a-col>
      </a-row>
    </a-card>

    <!-- 列表 -->
    <a-card>
      <a-table
        :columns="columns"
        :data-source="products"
        :pagination="paginationConfig"
        :loading="loading"
        row-key="id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <div class="flex items-center space-x-3">
              <img :src="record.featured_image || '/static/images/placeholder-product.jpg'" class="w-8 h-8 object-cover rounded" />
              <div>
                <a-typography-title :level="5" class="mb-0">{{ record.name }}</a-typography-title>
                <a-typography-text type="secondary" class="text-sm">{{ record.sku }}</a-typography-text>
              </div>
            </div>
          </template>

          <template v-if="column.key === 'price'">
            <span>{{ formatCurrency(record.price) }}</span>
            <span v-if="record.sale_price" class="line-through text-gray-400 ml-1">{{ formatCurrency(record.sale_price) }}</span>
          </template>

          <template v-if="column.key === 'stock_quantity'">
            <a-tag :color="record.stock_quantity > 0 ? 'green' : 'red'">{{ record.stock_quantity }}</a-tag>
          </template>

          <template v-if="column.key === 'is_active'">
            <a-tag :color="record.is_active ? 'blue' : 'default'">{{ record.is_active ? '上架' : '下架' }}</a-tag>
          </template>

          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleEdit(record)"><EditOutlined /></a-button>
              <a-popconfirm title="確定刪除？" ok-text="確定" cancel-text="取消" @confirm="handleDelete(record.id)">
                <a-button type="link" danger size="small"><DeleteOutlined /></a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 彈窗表單 -->
    <a-modal v-model:open="modalVisible" :title="isEdit ? '編輯商品' : '新增商品'" width="80%" :confirm-loading="submitLoading" @ok="handleSubmit" @cancel="handleCancel">
      <a-form :model="form" :rules="rules" ref="formRef" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="商品名稱" name="name">
              <a-input v-model:value="form.name" placeholder="輸入商品名稱" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="SKU" name="sku">
              <a-input v-model:value="form.sku" placeholder="SKU (可選)" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="分類" name="category_id">
              <a-select v-model:value="form.category_id" placeholder="選擇分類">
                <a-select-option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="標籤" name="tag_ids">
              <a-select v-model:value="form.tag_ids" mode="multiple" placeholder="選擇標籤">
                <a-select-option v-for="tag in tags" :key="tag.id" :value="tag.id">{{ tag.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="庫存" name="stock_quantity">
              <a-input-number v-model:value="form.stock_quantity" :min="0" style="width: 100%;" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="6">
            <a-form-item label="價格" name="price">
              <a-input-number v-model:value="form.price" :min="0" :precision="2" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="特價" name="sale_price">
              <a-input-number v-model:value="form.sale_price" :min="0" :precision="2" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="上架" name="is_active">
              <a-switch v-model:checked="form.is_active" checked-children="上架" un-checked-children="下架" />
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="精選" name="is_featured">
              <a-switch v-model:checked="form.is_featured" checked-children="是" un-checked-children="否" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="商品簡述" name="short_description">
          <a-textarea v-model:value="form.short_description" :rows="2" placeholder="輸入商品簡述" />
        </a-form-item>

        <a-form-item label="商品描述" name="description">
          <a-textarea v-model:value="form.description" :rows="6" placeholder="輸入商品描述 (支援HTML)" />
        </a-form-item>

        <!-- 主圖上傳 / 預覽 -->
        <a-form-item label="主圖" name="featured_image">
          <upload-image v-model="form.featured_image" />
        </a-form-item>

        <!-- 圖庫上傳 -->
        <a-form-item label="圖庫" name="gallery_images">
          <upload-gallery v-model="form.gallery_images" />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="SEO 標題" name="meta_title">
              <a-input v-model:value="form.meta_title" placeholder="SEO 標題 (可選)" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="SEO 描述" name="meta_description">
              <a-textarea v-model:value="form.meta_description" :rows="2" placeholder="SEO 描述 (可選)" />
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
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'
import UploadImage from '../components/UploadImage.vue'
import UploadGallery from '../components/UploadGallery.vue'

const authStore = useAuthStore()
const products = ref([])
const categories = ref([])
const tags = ref([])
const loading = ref(false)
const modalVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref()

const searchForm = reactive({
  search: '',
  category_id: undefined,
  status: undefined,
  skip: 0,
  limit: 10
})

const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const paginationConfig = computed(() => ({
  ...pagination,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (t) => `共 ${t} 筆`,
  onChange: (p, s) => {
    pagination.current = p
    pagination.pageSize = s
    fetchProducts()
  }
}))

const columns = [
  { title: '商品', key: 'name', width: '30%' },
  { title: '價格', key: 'price', width: '120px' },
  { title: '庫存', key: 'stock_quantity', width: '100px' },
  { title: '狀態', key: 'is_active', width: '100px' },
  { title: '操作', key: 'action', width: '100px' }
]

const form = reactive({
  name: '',
  sku: '',
  description: '',
  short_description: '',
  price: 0,
  sale_price: null,
  stock_quantity: 0,
  is_active: true,
  is_featured: false,
  category_id: null,
  tag_ids: [],
  featured_image: '',
  gallery_images: [],
  meta_title: '',
  meta_description: ''
})

const rules = {
  name: [{ required: true, message: '請輸入商品名稱', trigger: 'blur' }],
  price: [{ required: true, type: 'number', min: 0, message: '請輸入價格' }],
  category_id: [{ required: true, message: '請選擇分類' }]
}

onMounted(() => {
  fetchCategories()
  fetchTags()
  fetchProducts()
})

const buildQuery = () => {
  const params = new URLSearchParams()
  params.append('page', pagination.current)
  params.append('page_size', pagination.pageSize)
  if (searchForm.search) params.append('search', searchForm.search)
  if (searchForm.category_id) params.append('category', searchForm.category_id)
  if (searchForm.status) params.append('status', searchForm.status)
  return params.toString()
}

const fetchProducts = async () => {
  loading.value = true
  try {
    const res = await fetch(`/api/admin/products?${buildQuery()}`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      const data = await res.json()
      products.value = data.items || data  // 後端可能返回 items+total
      pagination.total = data.total || data.length
    } else {
      message.error('取得商品失敗')
    }
  } catch (e) {
    console.error(e)
    message.error('取得商品失敗')
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  const res = await fetch('/api/categories')
  if (res.ok) categories.value = await res.json()
}

const fetchTags = async () => {
  const res = await fetch('/api/tags')
  if (res.ok) tags.value = await res.json()
}

const handleSearch = () => {
  pagination.current = 1
  fetchProducts()
}

const resetSearch = () => {
  Object.assign(searchForm, { search: '', category_id: undefined, status: undefined })
  pagination.current = 1
  fetchProducts()
}

const handleTableChange = (p) => {
  pagination.current = p.current
  pagination.pageSize = p.pageSize
  fetchProducts()
}

const handleCreate = () => {
  isEdit.value = false
  resetForm()
  modalVisible.value = true
}

const handleEdit = (record) => {
  isEdit.value = true
  Object.assign(form, { ...record, tag_ids: record.tags.map(t => t.id) })
  modalVisible.value = true
}

const handleDelete = async (id) => {
  try {
    const res = await fetch(`/api/admin/products/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      message.success('已刪除')
      fetchProducts()
    } else {
      const err = await res.json()
      message.error(err.detail || '刪除失敗')
    }
  } catch (e) {
    message.error('刪除失敗')
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const url = isEdit.value ? `/api/admin/products/${form.id}` : '/api/admin/products'
    const method = isEdit.value ? 'PUT' : 'POST'
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${authStore.token}` },
      body: JSON.stringify(form)
    })
    if (res.ok) {
      message.success(isEdit.value ? '更新成功' : '新增成功')
      modalVisible.value = false
      fetchProducts()
    } else {
      const err = await res.json()
      message.error(err.detail || '操作失敗')
    }
  } catch (e) {
    message.error('操作失敗')
  } finally {
    submitLoading.value = false
  }
}

const handleCancel = () => {
  modalVisible.value = false
  resetForm()
}

const resetForm = () => {
  Object.assign(form, {
    name: '', sku: '', description: '', short_description: '', price: 0, sale_price: null,
    stock_quantity: 0, is_active: true, is_featured: false, category_id: null, tag_ids: [], featured_image: '', gallery_images: [], meta_title: '', meta_description: ''
  })
  formRef.value?.resetFields()
}

const formatCurrency = (val) => {
  return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD' }).format(val)
}
</script>

<style scoped>
.text-sm { font-size: 12px; }
</style> 