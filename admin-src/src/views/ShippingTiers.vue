<template>
  <div class="admin-page">
    <!-- 1. 頁面標題區 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">運費級距管理</h1>
          <p class="page-description">管理多段運費級距設定和計算規則</p>
        </div>
        <div class="action-section">
          <a-button type="primary" @click="showCreateModal">
            <template #icon><PlusOutlined /></template>
            新增級距
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
              title="總級距數"
              :value="shippingTiers.length"
              prefix="🚚"
              :value-style="{ color: '#1890ff' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="啟用級距"
              :value="activeCount"
              prefix="✅"
              :value-style="{ color: '#52c41a' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="免運級距"
              :value="freeShippingCount"
              prefix="🎁"
              :value-style="{ color: '#faad14' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="平均運費"
              :value="averageShippingFee"
              prefix="💰"
              :precision="0"
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
              placeholder="搜尋級距名稱"
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
              v-model:value="searchForm.is_active"
              placeholder="選擇狀態"
              allow-clear
              @change="handleSearch"
            >
              <a-select-option :value="true">啟用</a-select-option>
              <a-select-option :value="false">停用</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="4">
            <a-select
              v-model:value="searchForm.free_shipping"
              placeholder="免運設定"
              allow-clear
              @change="handleSearch"
            >
              <a-select-option :value="true">免運</a-select-option>
              <a-select-option :value="false">收費</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="6">
            <a-input-number
              v-model:value="searchForm.min_amount"
              placeholder="最低金額"
              :min="0"
              :precision="0"
              style="width: 100%"
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
          :data-source="shippingTiers"
          :loading="loading"
          :pagination="paginationConfig"
          :row-key="record => record.id"
          @change="handleTableChange"
        >
          <!-- 級距資訊 -->
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'range'">
              <div class="range-info">
                <div class="range-text">
                  <span class="min-amount">{{ formatCurrency(record.min_amount) }}</span>
                  <span class="separator">-</span>
                  <span class="max-amount">
                    {{ record.max_amount ? formatCurrency(record.max_amount) : '無上限' }}
                  </span>
                </div>
                <div class="range-note">
                  {{ getRangeNote(record) }}
                </div>
              </div>
            </template>

            <!-- 運費設定 -->
            <template v-else-if="column.key === 'fee'">
              <div class="fee-info">
                <div v-if="record.free_shipping" class="free-shipping">
                  <a-tag color="green">免運費</a-tag>
                </div>
                <div v-else class="shipping-fee">
                  <span class="fee-amount">{{ formatCurrency(record.shipping_fee) }}</span>
                </div>
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
                <a-tag v-if="record.is_active" color="green">啟用</a-tag>
                <a-tag v-else color="default">停用</a-tag>
              </div>
            </template>

            <!-- 操作 -->
            <template v-else-if="column.key === 'action'">
              <a-space>
                <a-button size="small" @click="editShippingTier(record)">
                  <template #icon><EditOutlined /></template>
                  編輯
                </a-button>
                <a-popconfirm
                  title="確認刪除此級距？"
                  @confirm="deleteShippingTier(record.id)"
                >
                  <a-button size="small" danger>
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

    <!-- 5. 運費計算測試區 -->
    <div class="calculator-section">
      <a-card title="運費計算測試">
        <a-row :gutter="24">
          <a-col :span="8">
            <a-input-number
              v-model:value="testAmount"
              placeholder="請輸入測試金額"
              :min="0"
              :precision="0"
              style="width: 100%"
            />
          </a-col>
          <a-col :span="8">
            <a-button type="primary" @click="calculateShipping">
              <template #icon><CalculatorOutlined /></template>
              計算運費
            </a-button>
          </a-col>
          <a-col :span="8">
            <div v-if="calculationResult" class="calculation-result">
              <span class="result-label">計算結果：</span>
              <span class="result-value">{{ formatCurrency(calculationResult.shipping_fee) }}</span>
            </div>
          </a-col>
        </a-row>
      </a-card>
    </div>

    <!-- 6. 新增/編輯 Modal -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      :confirm-loading="modalLoading"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
      width="600px"
    >
      <a-form
        ref="formRef"
        :model="form"
        :rules="rules"
        layout="vertical"
      >
        <a-form-item label="級距名稱" name="name">
          <a-input v-model:value="form.name" placeholder="請輸入級距名稱" />
        </a-form-item>

        <a-form-item label="級距描述" name="description">
          <a-textarea
            v-model:value="form.description"
            placeholder="請輸入級距描述"
            :rows="3"
          />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="最低金額" name="min_amount">
              <a-input-number
                v-model:value="form.min_amount"
                placeholder="0"
                :min="0"
                :precision="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="最高金額" name="max_amount">
              <a-input-number
                v-model:value="form.max_amount"
                placeholder="留空表示無上限"
                :min="0"
                :precision="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="免運設定" name="free_shipping">
              <a-switch
                v-model:checked="form.free_shipping"
                checked-children="免運"
                un-checked-children="收費"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              label="運費金額"
              name="shipping_fee"
              v-show="!form.free_shipping"
            >
              <a-input-number
                v-model:value="form.shipping_fee"
                placeholder="0"
                :min="0"
                :precision="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="排序權重" name="sort_order">
              <a-input-number
                v-model:value="form.sort_order"
                placeholder="0"
                :min="0"
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

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import axios from '../utils/axios'
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  CalculatorOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'ShippingTiers',
  components: {
    PlusOutlined,
    SearchOutlined,
    EditOutlined,
    DeleteOutlined,
    CalculatorOutlined
  },
  setup() {
    // 響應式資料
    const shippingTiers = ref([])
    const loading = ref(false)
    const modalVisible = ref(false)
    const modalLoading = ref(false)
    const editingId = ref(null)
    const testAmount = ref(1000)
    const calculationResult = ref(null)

    // 搜尋表單
    const searchForm = reactive({
      search: '',
      is_active: null,
      free_shipping: null,
      min_amount: null
    })

    // 編輯表單
    const form = reactive({
      name: '',
      description: '',
      min_amount: 0,
      max_amount: null,
      shipping_fee: 0,
      free_shipping: false,
      is_active: true,
      sort_order: 0
    })

    // 表單驗證規則
    const rules = {
      name: [
        { required: true, message: '請輸入級距名稱' },
        { min: 1, max: 100, message: '級距名稱長度應在1-100個字符之間' }
      ],
      min_amount: [
        { required: true, message: '請輸入最低金額' },
        { type: 'number', min: 0, message: '最低金額不能小於0' }
      ],
      max_amount: [
        { type: 'number', min: 0, message: '最高金額不能小於0' }
      ],
      shipping_fee: [
        { required: true, message: '請輸入運費金額' },
        { type: 'number', min: 0, message: '運費金額不能小於0' }
      ]
    }

    // 表格欄位定義
    const columns = [
      {
        title: '級距名稱',
        dataIndex: 'name',
        key: 'name',
        width: 150
      },
      {
        title: '金額範圍',
        key: 'range',
        width: 200
      },
      {
        title: '運費設定',
        key: 'fee',
        width: 120
      },
      {
        title: '描述',
        dataIndex: 'description',
        key: 'description',
        ellipsis: true
      },
      {
        title: '排序',
        dataIndex: 'sort_order',
        key: 'sort_order',
        width: 80
      },
      {
        title: '狀態',
        key: 'status',
        width: 120
      },
      {
        title: '操作',
        key: 'action',
        width: 160
      }
    ]

    // 分頁配置
    const paginationConfig = {
      current: 1,
      pageSize: 10,
      total: 0,
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: total => `共 ${total} 條記錄`
    }

    // 計算屬性
    const modalTitle = computed(() => {
      return editingId.value ? '編輯級距' : '新增級距'
    })

    const activeCount = computed(() => {
      return shippingTiers.value.filter(tier => tier.is_active).length
    })

    const freeShippingCount = computed(() => {
      return shippingTiers.value.filter(tier => tier.free_shipping).length
    })

    const averageShippingFee = computed(() => {
      const paidTiers = shippingTiers.value.filter(tier => !tier.free_shipping)
      if (paidTiers.length === 0) return 0
      
      const totalFee = paidTiers.reduce((sum, tier) => sum + parseFloat(tier.shipping_fee || 0), 0)
      return totalFee / paidTiers.length
    })

    // 方法定義
    const formatCurrency = (amount) => {
      return `NT$ ${parseFloat(amount || 0).toLocaleString()}`
    }

    const getRangeNote = (record) => {
      if (record.max_amount) {
        return `含 ${formatCurrency(record.min_amount)}，不含 ${formatCurrency(record.max_amount)}`
      }
      return `${formatCurrency(record.min_amount)} 以上`
    }

    const fetchShippingTiers = async () => {
      try {
        loading.value = true
        const response = await axios.get('/api/shipping-tiers')
        shippingTiers.value = response.data
        paginationConfig.total = response.data.length
      } catch (error) {
        message.error('載入運費級距失敗')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    const showCreateModal = () => {
      editingId.value = null
      resetForm()
      modalVisible.value = true
    }

    const editShippingTier = (record) => {
      editingId.value = record.id
      Object.assign(form, {
        name: record.name,
        description: record.description,
        min_amount: record.min_amount,
        max_amount: record.max_amount,
        shipping_fee: record.shipping_fee,
        free_shipping: record.free_shipping,
        is_active: record.is_active,
        sort_order: record.sort_order
      })
      modalVisible.value = true
    }

    const resetForm = () => {
      Object.assign(form, {
        name: '',
        description: '',
        min_amount: 0,
        max_amount: null,
        shipping_fee: 0,
        free_shipping: false,
        is_active: true,
        sort_order: 0
      })
    }

    const handleModalOk = async () => {
      try {
        modalLoading.value = true
        
        const formData = {
          ...form,
          shipping_fee: form.free_shipping ? 0 : form.shipping_fee
        }

        if (editingId.value) {
          await axios.put(`/api/shipping-tiers/${editingId.value}`, formData)
          message.success('運費級距更新成功')
        } else {
          await axios.post('/api/shipping-tiers', formData)
          message.success('運費級距建立成功')
        }

        modalVisible.value = false
        await fetchShippingTiers()
      } catch (error) {
        message.error('操作失敗')
        console.error(error)
      } finally {
        modalLoading.value = false
      }
    }

    const handleModalCancel = () => {
      modalVisible.value = false
      resetForm()
    }

    const toggleStatus = async (record) => {
      try {
        record.updating = true
        await axios.put(`/api/shipping-tiers/${record.id}/toggle-status`)
        message.success('狀態更新成功')
        await fetchShippingTiers()
      } catch (error) {
        message.error('狀態更新失敗')
        record.is_active = !record.is_active // 回復原狀態
        console.error(error)
      } finally {
        record.updating = false
      }
    }

    const deleteShippingTier = async (id) => {
      try {
        await axios.delete(`/api/shipping-tiers/${id}`)
        message.success('運費級距刪除成功')
        await fetchShippingTiers()
      } catch (error) {
        message.error('刪除失敗')
        console.error(error)
      }
    }

    const calculateShipping = async () => {
      if (!testAmount.value || testAmount.value <= 0) {
        message.warning('請輸入有效的測試金額')
        return
      }

      try {
        const response = await axios.post('/api/shipping-tiers/calculate', {
          amount: testAmount.value
        })
        calculationResult.value = response.data
        message.success('運費計算完成')
      } catch (error) {
        message.error('運費計算失敗')
        console.error(error)
      }
    }

    const handleSearch = () => {
      // 實現搜尋邏輯
      console.log('搜尋:', searchForm)
    }

    const resetSearch = () => {
      Object.assign(searchForm, {
        search: '',
        is_active: null,
        free_shipping: null,
        min_amount: null
      })
      handleSearch()
    }

    const handleTableChange = (pagination, filters, sorter) => {
      paginationConfig.current = pagination.current
      paginationConfig.pageSize = pagination.pageSize
    }

    // 生命週期
    onMounted(() => {
      fetchShippingTiers()
    })

    return {
      // 響應式資料
      shippingTiers,
      loading,
      modalVisible,
      modalLoading,
      editingId,
      testAmount,
      calculationResult,
      searchForm,
      form,
      rules,
      columns,
      paginationConfig,
      
      // 計算屬性
      modalTitle,
      activeCount,
      freeShippingCount,
      averageShippingFee,
      
      // 方法
      formatCurrency,
      getRangeNote,
      showCreateModal,
      editShippingTier,
      handleModalOk,
      handleModalCancel,
      toggleStatus,
      deleteShippingTier,
      calculateShipping,
      handleSearch,
      resetSearch,
      handleTableChange
    }
  }
}
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
  align-items: center;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #1f2937;
}

.page-description {
  margin: 4px 0 0 0;
  color: #6b7280;
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

.calculator-section {
  margin-bottom: 24px;
}

.range-info {
  display: flex;
  flex-direction: column;
}

.range-text {
  font-weight: 600;
  margin-bottom: 4px;
}

.separator {
  margin: 0 8px;
  color: #6b7280;
}

.range-note {
  font-size: 12px;
  color: #6b7280;
}

.fee-info {
  display: flex;
  align-items: center;
}

.fee-amount {
  font-weight: 600;
  color: #1f2937;
}

.free-shipping {
  font-weight: 600;
}

.status-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.calculation-result {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-label {
  color: #6b7280;
}

.result-value {
  font-weight: 600;
  color: #1f2937;
  font-size: 16px;
}
</style> 