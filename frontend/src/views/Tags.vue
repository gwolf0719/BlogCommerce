<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">標籤管理</h1>
      <a-button type="primary" @click="handleCreate">
        <template #icon><PlusOutlined /></template>
        新增標籤
      </a-button>
    </div>

    <a-card>
      <a-table
        :columns="columns"
        :data-source="tags"
        :loading="loading"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <a-typography-title :level="5">{{ record.name }}</a-typography-title>
            <a-typography-text type="secondary" class="text-sm">/{{ record.slug }}</a-typography-text>
          </template>

          <template v-if="column.key === 'type'">
            <a-tag :color="record.type === 'BLOG' ? 'blue' : (record.type === 'PRODUCT' ? 'purple' : 'cyan')">
              {{ record.type }}
            </a-tag>
          </template>

          <template v-if="column.key === 'count'">
            <a-tag color="blue">{{ record.count || 0 }}</a-tag>
          </template>

          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleEdit(record)">
                <EditOutlined />
              </a-button>
              <a-popconfirm
                title="確定要刪除此標籤？"
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

    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '編輯標籤' : '新增標籤'"
      @ok="handleSubmit"
      :confirm-loading="submitLoading"
      @cancel="handleCancel"
    >
      <a-form :model="form" :rules="rules" layout="vertical" ref="formRef">
        <a-form-item label="標籤名稱" name="name">
          <a-input v-model:value="form.name" placeholder="輸入標籤名稱" />
        </a-form-item>
        <a-form-item label="標籤描述" name="description">
          <a-textarea v-model:value="form.description" rows="3" placeholder="輸入描述(可選)" />
        </a-form-item>
        <a-form-item label="類型" name="type">
          <a-select v-model:value="form.type" placeholder="選擇標籤類型">
            <a-select-option value="BLOG">BLOG</a-select-option>
            <a-select-option value="PRODUCT">PRODUCT</a-select-option>
          </a-select>
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

const tags = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const modalVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

const form = reactive({
  name: '',
  description: '',
  type: 'BLOG'
})

const rules = {
  name: [{ required: true, message: '請輸入標籤名稱', trigger: 'blur' }],
  type: [{ required: true, message: '請選擇標籤類型', trigger: 'change' }]
}

const columns = [
  { title: '名稱', key: 'name' },
  { title: '類型', key: 'type', width: 120 },
  { title: '使用次數', key: 'count', width: 120 },
  { title: '操作', key: 'action', width: 100 }
]

onMounted(() => fetchTags())

const fetchTags = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/admin/tags', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      tags.value = await res.json()
    } else {
      message.error('獲取標籤失敗')
    }
  } catch (e) {
    console.error(e)
    message.error('獲取標籤失敗')
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
    const res = await fetch(`/api/admin/tags/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      message.success('刪除成功')
      fetchTags()
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
    const url = isEdit.value ? `/api/admin/tags/${form.id}` : '/api/admin/tags'
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
      fetchTags()
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
  Object.assign(form, { name: '', description: '', type: 'BLOG' })
  formRef.value?.resetFields()
}
</script>

<style scoped>
.text-sm { font-size: 12px; }
</style> 