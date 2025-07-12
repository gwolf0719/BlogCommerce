<template>
  <div class="promo-codes-container">
    <div class="header-section">
      <h1 class="page-title">推薦碼管理</h1>
      <div class="header-actions">
        <a-button type="primary" @click="showCreateModal">
          <template #icon>
            <PlusOutlined />
          </template>
          新增推薦碼
        </a-button>
      </div>
    </div>

    <!-- 統計卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.total_codes }}</div>
          <div class="stat-label">總推薦碼數</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.active_codes }}</div>
          <div class="stat-label">啟用推薦碼</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.total_usage }}</div>
          <div class="stat-label">總使用次數</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-content">
          <div class="stat-number">NT${{ Math.round(stats.total_promo_amount).toLocaleString() }}</div>
          <div class="stat-label">推薦碼節省金額</div>
        </div>
      </div>
    </div>

    <!-- 篩選器 -->
    <div class="filter-section">
      <div class="filter-row">
        <a-input-search
          v-model:value="searchText"
          placeholder="搜尋推薦碼或名稱"
          @search="loadPromoCodes"
          style="width: 300px"
        />
        <a-select
          v-model:value="statusFilter"
          placeholder="狀態篩選"
          style="width: 120px"
          allowClear
          @change="loadPromoCodes"
        >
          <a-select-option value="true">啟用</a-select-option>
          <a-select-option value="false">停用</a-select-option>
        </a-select>
        <a-select
          v-model:value="typeFilter"
          placeholder="類型篩選"
          style="width: 120px"
          allowClear
          @change="loadPromoCodes"
        >
          <a-select-option value="PERCENTAGE">百分比</a-select-option>
          <a-select-option value="AMOUNT">固定金額</a-select-option>
          <a-select-option value="FREE_SHIPPING">免運費</a-select-option>
        </a-select>
      </div>
    </div>

    <!-- 推薦碼列表 -->
    <div class="table-container">
      <a-table
        :columns="columns"
        :data-source="promoCodes || []"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        rowKey="id"
        size="middle"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'code'">
            <a-tag color="blue" style="font-family: monospace; font-weight: bold;">
              {{ record.code }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'promo_type'">
            <a-tag :color="getTypeColor(record.promo_type)">
              {{ getTypeText(record.promo_type) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'promo_value'">
            <span v-if="record.promo_type === 'PERCENTAGE'">
              {{ record.promo_value }}%
            </span>
            <span v-else-if="record.promo_type === 'AMOUNT'">
              NT${{ record.promo_value.toLocaleString() }}
            </span>
            <span v-else>
              免運費
            </span>
          </template>
          <template v-else-if="column.key === 'usage'">
            <div class="usage-info">
              <span>{{ record.used_count }}</span>
              <span v-if="record.usage_limit"> / {{ record.usage_limit }}</span>
              <span v-else> / 無限制</span>
            </div>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag :color="record.is_active ? 'green' : 'red'">
              {{ record.is_active ? '啟用' : '停用' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'period'">
            <div class="period-info">
              <div>{{ formatDate(record.start_date) }}</div>
              <div>{{ formatDate(record.end_date) }}</div>
            </div>
          </template>
          <template v-else-if="column.key === 'actions'">
            <div class="action-buttons">
              <a-button type="link" size="small" @click="showEditModal(record)">
                編輯
              </a-button>
              <a-button type="link" size="small" @click="showUsageModal(record)">
                使用記錄
              </a-button>
              <a-popconfirm
                title="確定要刪除這個推薦碼嗎？"
                @confirm="deletePromoCode(record.id)"
              >
                <a-button type="link" size="small" danger>
                  刪除
                </a-button>
              </a-popconfirm>
            </div>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 新增/編輯推薦碼對話框 -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      :confirmLoading="modalLoading"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
      width="800px"
    >
      <a-form
        ref="formRef"
        :model="form"
        :rules="rules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 18 }"
      >
        <a-form-item label="推薦碼" name="code">
          <a-input v-model:value="form.code" placeholder="請輸入推薦碼" />
        </a-form-item>
        <a-form-item label="專案名稱" name="name">
          <a-input v-model:value="form.name" placeholder="請輸入專案名稱" />
        </a-form-item>
        <a-form-item label="行銷來源" name="source">
          <a-input v-model:value="form.source" placeholder="請輸入行銷來源" />
        </a-form-item>
        <a-form-item label="推薦類型" name="promo_type">
          <a-select v-model:value="form.promo_type" placeholder="請選擇推薦類型">
            <a-select-option value="PERCENTAGE">百分比推薦</a-select-option>
            <a-select-option value="AMOUNT">固定金額推薦</a-select-option>
            <a-select-option value="FREE_SHIPPING">免運費</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="推薦值" name="promo_value">
          <a-input-number
            v-model:value="form.promo_value"
            :min="0"
            :max="form.promo_type === 'PERCENTAGE' ? 100 : 999999"
            :step="form.promo_type === 'PERCENTAGE' ? 1 : 10"
            :precision="form.promo_type === 'PERCENTAGE' ? 0 : 0"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="有效期間" name="period">
          <a-range-picker
            v-model:value="form.period"
            show-time
            format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="使用限制" name="usage_limit">
          <a-input-number
            v-model:value="form.usage_limit"
            :min="0"
            placeholder="留空表示無限制"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="最小訂單金額" name="min_order_amount">
          <a-input-number
            v-model:value="form.min_order_amount"
            :min="0"
            placeholder="留空表示無限制"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="啟用狀態" name="is_active">
          <a-switch v-model:checked="form.is_active" />
        </a-form-item>
        <a-form-item label="描述" name="description">
          <a-textarea v-model:value="form.description" placeholder="請輸入描述" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 使用記錄對話框 -->
    <a-modal
      v-model:open="usageModalVisible"
      title="使用記錄"
      :footer="null"
      width="1000px"
    >
      <a-table
        :columns="usageColumns"
        :data-source="usageRecords"
        :loading="usageLoading"
        :pagination="usagePagination"
        @change="handleUsageTableChange"
        rowKey="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'amounts'">
            <div class="amount-info">
              <div>原價: NT${{ record.original_amount.toLocaleString() }}</div>
              <div>推薦: -NT${{ record.promo_amount.toLocaleString() }}</div>
              <div>實付: NT${{ record.final_amount.toLocaleString() }}</div>
            </div>
          </template>
          <template v-else-if="column.key === 'used_at'">
            {{ formatDateTime(record.used_at) }}
          </template>
        </template>
      </a-table>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'
import dayjs from 'dayjs'

const authStore = useAuthStore()

// 資料狀態
const promoCodes = ref([])
const loading = ref(false)
const stats = ref({
  total_codes: 0,
  active_codes: 0,
  total_usage: 0,
  total_promo_amount: 0
})
const statsLoading = ref(false)

// 篩選器
const searchText = ref('')
const statusFilter = ref(null)
const typeFilter = ref(null)

// 分頁
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 筆資料`
})

// 表單狀態
const modalVisible = ref(false)
const modalTitle = ref('')
const modalLoading = ref(false)
const editingId = ref(null)
const formRef = ref()

// 表單資料
const form = reactive({
  code: '',
  name: '',
  source: '',
  promo_type: '',
  promo_value: null,
  period: null,
  usage_limit: null,
  min_order_amount: null,
  is_active: true,
  description: ''
})

// 使用記錄相關
const usageModalVisible = ref(false)
const usageLoading = ref(false)
const usageRecords = ref([])
const usagePagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

// 表格列定義
const columns = [
  { title: '推薦碼', dataIndex: 'code', key: 'code', width: 120 },
  { title: '專案名稱', dataIndex: 'name', key: 'name', width: 150 },
  { title: '來源', dataIndex: 'source', key: 'source', width: 100 },
  { title: '類型', dataIndex: 'promo_type', key: 'promo_type', width: 100 },
  { title: '推薦值', dataIndex: 'promo_value', key: 'promo_value', width: 100 },
  { title: '使用情況', dataIndex: 'usage', key: 'usage', width: 120 },
  { title: '狀態', dataIndex: 'is_active', key: 'status', width: 80 },
  { title: '有效期間', dataIndex: 'period', key: 'period', width: 180 },
  { title: '操作', key: 'actions', width: 180, fixed: 'right' }
]

const usageColumns = [
  { title: '訂單ID', dataIndex: 'order_id', key: 'order_id', width: 80 },
  { title: '用戶', dataIndex: 'user', key: 'user', width: 100 },
  { title: '金額明細', dataIndex: 'amounts', key: 'amounts', width: 180 },
  { title: '使用時間', dataIndex: 'used_at', key: 'used_at', width: 150 }
]

// 表單驗證規則
const rules = {
  code: [{ required: true, message: '請輸入推薦碼' }],
  name: [{ required: true, message: '請輸入專案名稱' }],
  promo_type: [{ required: true, message: '請選擇推薦類型' }],
  promo_value: [{ required: true, message: '請輸入推薦值' }],
  period: [{ required: true, message: '請選擇有效期間' }]
}

// 方法
const loadPromoCodes = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: pagination.current,
      size: pagination.pageSize
    })
    
    if (searchText.value) params.append('search', searchText.value)
    if (statusFilter.value) params.append('status', statusFilter.value)
    if (typeFilter.value) params.append('type', typeFilter.value)

    const response = await fetch(`/api/promo-codes?${params}`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })

    if (response.ok) {
      const data = await response.json()
      promoCodes.value = data.items || data || []
      pagination.total = data.total || promoCodes.value.length
    }
  } catch (error) {
    message.error('載入推薦碼失敗')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  statsLoading.value = true
  try {
    const response = await fetch('/api/promo-codes/stats', {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })

    if (response.ok) {
      const data = await response.json()
      stats.value = data
    }
  } catch (error) {
    message.error('載入統計資料失敗')
  } finally {
    statsLoading.value = false
  }
}

const showCreateModal = () => {
  editingId.value = null
  modalTitle.value = '新增推薦碼'
  resetForm()
  modalVisible.value = true
}

const showEditModal = (record) => {
  editingId.value = record.id
  modalTitle.value = '編輯推薦碼'
  
  // 填充表單資料
  Object.assign(form, {
    code: record.code,
    name: record.name,
    source: record.source,
    promo_type: record.promo_type,
    promo_value: record.promo_value,
    period: [dayjs(record.start_date), dayjs(record.end_date)],
    usage_limit: record.usage_limit,
    min_order_amount: record.min_order_amount,
    is_active: record.is_active,
    description: record.description
  })
  
  modalVisible.value = true
}

const handleModalOk = async () => {
  try {
    await formRef.value.validateFields()
    modalLoading.value = true
    
    const payload = {
      code: form.code,
      name: form.name,
      source: form.source,
      promo_type: form.promo_type,
      promo_value: form.promo_value,
      start_date: form.period[0].format('YYYY-MM-DD HH:mm:ss'),
      end_date: form.period[1].format('YYYY-MM-DD HH:mm:ss'),
      usage_limit: form.usage_limit,
      min_order_amount: form.min_order_amount,
      is_active: form.is_active,
      description: form.description
    }
    
    const url = editingId.value 
      ? `/api/promo-codes/${editingId.value}`
      : '/api/promo-codes'
    
    const method = editingId.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    
    if (response.ok) {
      message.success(editingId.value ? '更新成功' : '新增成功')
      modalVisible.value = false
      loadPromoCodes()
      loadStats()
    } else {
      const error = await response.json()
      message.error(error.detail || '操作失敗')
    }
  } catch (error) {
    message.error('表單驗證失敗')
  } finally {
    modalLoading.value = false
  }
}

const handleModalCancel = () => {
  modalVisible.value = false
  resetForm()
}

const resetForm = () => {
  Object.assign(form, {
    code: '',
    name: '',
    source: '',
    promo_type: '',
    promo_value: null,
    period: null,
    usage_limit: null,
    min_order_amount: null,
    is_active: true,
    description: ''
  })
}

const deletePromoCode = async (id) => {
  try {
    const response = await fetch(`/api/promo-codes/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    
    if (response.ok) {
      message.success('刪除成功')
      loadPromoCodes()
      loadStats()
    } else {
      const error = await response.json()
      message.error(error.detail || '刪除失敗')
    }
  } catch (error) {
    message.error('刪除失敗')
  }
}

const showUsageModal = async (record) => {
  usageModalVisible.value = true
  usageLoading.value = true
  
  try {
    const response = await fetch(`/api/promo-codes/${record.id}/usage`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      usageRecords.value = data
    }
  } catch (error) {
    message.error('載入使用記錄失敗')
  } finally {
    usageLoading.value = false
  }
}

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadPromoCodes()
}

const handleUsageTableChange = (pag) => {
  usagePagination.current = pag.current
  usagePagination.pageSize = pag.pageSize
  // 重新載入使用記錄
}

const getTypeColor = (type) => {
  switch (type) {
    case 'PERCENTAGE':
      return 'blue'
    case 'AMOUNT':
      return 'green'
    case 'FREE_SHIPPING':
      return 'orange'
    default:
      return 'default'
  }
}

const getTypeText = (type) => {
  switch (type) {
    case 'PERCENTAGE':
      return '百分比'
    case 'AMOUNT':
      return '固定金額'
    case 'FREE_SHIPPING':
      return '免運費'
    default:
      return type
  }
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD')
}

const formatDateTime = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss')
}

// 頁面載入
onMounted(() => {
  loadPromoCodes()
  loadStats()
})
</script>

<style scoped>
.promo-codes-container {
  padding: 24px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 32px;
  width: 48px;
  text-align: center;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #1890ff;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.filter-section {
  background: white;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.filter-row {
  display: flex;
  gap: 16px;
  align-items: center;
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.usage-info {
  font-size: 12px;
}

.period-info {
  font-size: 12px;
  line-height: 1.4;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.amount-info {
  font-size: 12px;
  line-height: 1.4;
}
</style> 