<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">分類管理</h1>
      <a-button type="primary" @click="handleCreate">
        <template #icon><PlusOutlined /></template>
        新增分類
      </a-button>
    </div>

    <!-- 分類列表 -->
    <a-card>
      <a-table
        :columns="columns"
        :data-source="categories"
        :loading="loading"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <a-typography-title :level="5">{{ record.name }}</a-typography-title>
            <a-typography-text type="secondary" class="text-sm">/{{ record.slug }}</a-typography-text>
          </template>

          <template v-if="column.key === 'type'">
            <a-tag color="cyan">通用</a-tag>
          </template>

          <template v-if="column.key === 'counts'">
            <div class="space-x-2">
              <a-tag color="blue">文章 {{ record.post_count }}</a-tag>
              <a-tag color="purple">商品 {{ record.product_count }}</a-tag>
            </div>
          </template>

          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleEdit(record)">
                <EditOutlined />
              </a-button>
              <a-popconfirm
                title="確定要刪除此分類？"
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

    <!-- 新增/編輯分類 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '編輯分類' : '新增分類'"
      @ok="handleSubmit"
      :confirm-loading="submitLoading"
      @cancel="handleCancel"
    >
      <a-form :model="form" :rules="rules" ref="formRef" layout="vertical">
        <a-form-item label="分類名稱" name="name">
          <a-input v-model:value="form.name" placeholder="輸入分類名稱" />
        </a-form-item>
        <a-form-item label="分類描述" name="description">
          <a-textarea v-model:value="form.description" rows="3" placeholder="輸入描述(可選)" />
        </a-form-item>

      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const categories = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const modalVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

const form = reactive({
  name: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '請輸入分類名稱', trigger: 'blur' }]
}

const columns = [
  { title: '名稱', key: 'name' },
  { title: '類型', key: 'type', width: 120 },
  { title: '內容數', key: 'counts', width: 200 },
  { title: '操作', key: 'action', width: 100 }
]

onMounted(() => {
  fetchCategories()
})

const fetchCategories = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/admin/categories', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      categories.value = await res.json()
    } else {
      message.error('獲取分類失敗')
    }
  } catch (e) {
    console.error(e)
    message.error('獲取分類失敗')
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  isEdit.value = false
  resetForm()
  modalVisible.value = true
}

const handleEdit = (record) => {
  isEdit.value = true
  Object.assign(form, { ...record })
  modalVisible.value = true
}

const handleDelete = async (id) => {
  try {
    const res = await fetch(`/api/categories/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      message.success('刪除成功')
      fetchCategories()
    } else {
      const err = await res.json()
      message.error(err.detail || '刪除失敗')
    }
  } catch (e) {
    console.error(e)
    message.error('刪除失敗')
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const url = isEdit.value ? `/api/categories/${form.id}` : '/api/categories'
    const method = isEdit.value ? 'PUT' : 'POST'
    const res = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`
      },
      body: JSON.stringify(form)
    })
    if (res.ok) {
      message.success(isEdit.value ? '更新成功' : '新增成功')
      modalVisible.value = false
      fetchCategories()
    } else {
      const err = await res.json()
      message.error(err.detail || '操作失敗')
    }
  } catch (e) {
    console.error(e)
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
  Object.assign(form, { name: '', description: '' })
  formRef.value?.resetFields()
}
</script>

<style scoped>
.text-sm {
  font-size: 12px;
}
</style> 