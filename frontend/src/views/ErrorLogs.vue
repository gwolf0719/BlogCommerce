<template>
  <div class="error-logs-page">
    <!-- 頁面標題 -->
    <a-page-header 
      title="錯誤日誌管理" 
      sub-title="監控系統錯誤並追蹤解決進度"
      class="page-header"
    >
      <template #extra>
        <a-space>
          <a-button @click="refreshData" :loading="loading" type="primary" icon="reload">
            重新整理
          </a-button>
          <a-button @click="cleanResolvedErrors" type="default" icon="check">
            清理已解決
          </a-button>
          <a-button @click="cleanOldErrors" danger icon="delete">
            清理舊錯誤
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <div class="page-content">
      <!-- 統計卡片 -->
      <a-row :gutter="[16, 16]" class="stats-cards">
        <a-col :span="6">
          <a-card>
            <a-statistic 
              title="總錯誤數" 
              :value="stats?.total_errors || 0" 
              :value-style="{ color: '#cf1322' }"
            >
              <template #prefix>
                <ExclamationCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        
        <a-col :span="6">
          <a-card>
            <a-statistic 
              title="已解決" 
              :value="stats?.resolved_errors || 0"
              :value-style="{ color: '#52c41a' }"
            >
              <template #prefix>
                <CheckCircleOutlined />
              </template>
              <template #suffix>
                <span class="suffix-text">/ {{ stats?.total_errors || 0 }}</span>
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        
        <a-col :span="6">
          <a-card>
            <a-statistic 
              title="未解決" 
              :value="stats?.unresolved_errors || 0"
              :value-style="{ color: '#fa8c16' }"
            >
              <template #prefix>
                <WarningOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        
        <a-col :span="6">
          <a-card>
            <a-statistic 
              title="解決率" 
              :value="getResolvedRate()" 
              suffix="%"
              :value-style="{ color: '#1890ff' }"
            >
              <template #prefix>
                <PieChartOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
      </a-row>

      <!-- 篩選器 -->
      <a-card title="篩選條件" class="filter-card">
        <a-row :gutter="16">
          <a-col :span="8">
            <a-input-search
              v-model:value="searchTerm"
              placeholder="搜尋錯誤訊息、類型..."
              @change="filterErrors"
              allow-clear
            />
          </a-col>
          <a-col :span="4">
            <a-select 
              v-model:value="filterStatus" 
              @change="filterErrors" 
              placeholder="選擇狀態"
              allow-clear
              style="width: 100%"
            >
              <a-select-option value="">全部狀態</a-select-option>
              <a-select-option value="false">未解決</a-select-option>
              <a-select-option value="true">已解決</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="4">
            <a-select 
              v-model:value="filterSource" 
              @change="filterErrors" 
              placeholder="選擇來源"
              allow-clear
              style="width: 100%"
            >
              <a-select-option value="">全部來源</a-select-option>
              <a-select-option value="frontend">前端</a-select-option>
              <a-select-option value="backend">後端</a-select-option>
              <a-select-option value="api">API</a-select-option>
              <a-select-option value="database">資料庫</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="4">
            <a-select 
              v-model:value="filterSeverity" 
              @change="filterErrors" 
              placeholder="選擇嚴重程度"
              allow-clear
              style="width: 100%"
            >
              <a-select-option value="">全部程度</a-select-option>
              <a-select-option value="low">低</a-select-option>
              <a-select-option value="medium">中</a-select-option>
              <a-select-option value="high">高</a-select-option>
              <a-select-option value="critical">緊急</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="4">
            <a-button @click="resetFilters" block>重置篩選</a-button>
          </a-col>
        </a-row>
      </a-card>

      <!-- 錯誤列表 -->
      <a-card title="錯誤列表" class="error-list-card">
        <a-table
          :columns="columns"
          :data-source="paginatedErrors"
          :pagination="paginationConfig"
          :loading="loading"
          :scroll="{ x: 1200 }"
          size="middle"
          @change="handleTableChange"
        >
          <!-- 時間欄位 -->
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'created_at'">
              <a-space direction="vertical" size="small">
                <span>{{ formatDate(record.created_at) }}</span>
                <a-tag size="small" color="blue">{{ formatTimeAgo(record.created_at) }}</a-tag>
              </a-space>
            </template>
            
            <!-- 來源欄位 -->
            <template v-else-if="column.key === 'source'">
              <a-tag :color="getSourceColor(record.source)">
                {{ getSourceLabel(record.source) }}
              </a-tag>
            </template>
            
            <!-- 嚴重程度欄位 -->
            <template v-else-if="column.key === 'severity'">
              <a-tag :color="getSeverityColor(record.severity)">
                {{ getSeverityLabel(record.severity) }}
              </a-tag>
            </template>
            
            <!-- 狀態欄位 -->
            <template v-else-if="column.key === 'is_resolved'">
              <a-tag :color="record.is_resolved ? 'success' : 'error'">
                {{ record.is_resolved ? '已解決' : '未解決' }}
              </a-tag>
            </template>
            
            <!-- 錯誤訊息欄位 -->
            <template v-else-if="column.key === 'error_message'">
              <div class="error-message">
                <div class="error-title">{{ record.error_type || '未知錯誤' }}</div>
                <div class="error-text">{{ record.error_message }}</div>
              </div>
            </template>
            
            <!-- 操作欄位 -->
            <template v-else-if="column.key === 'actions'">
              <a-space>
                <a-button @click="viewError(record)" size="small" type="link">
                  詳情
                </a-button>
                <a-button 
                  v-if="!record.is_resolved"
                  @click="markAsResolved(record)" 
                  size="small" 
                  type="link"
                >
                  標記已解決
                </a-button>
                <a-popconfirm
                  title="確定要刪除這個錯誤記錄嗎？"
                  @confirm="deleteError(record)"
                  ok-text="確定"
                  cancel-text="取消"
                >
                  <a-button size="small" type="link" danger>
                    刪除
                  </a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>

    <!-- 錯誤詳情 Modal -->
    <a-modal
      v-model:open="showDetailModal"
      title="錯誤詳情"
      width="800px"
      :footer="null"
    >
      <div v-if="selectedError" class="error-detail">
        <a-descriptions :column="2" bordered size="small">
          <a-descriptions-item label="錯誤類型">
            {{ selectedError.error_type || '未知' }}
          </a-descriptions-item>
          <a-descriptions-item label="發生時間">
            {{ formatDate(selectedError.created_at) }}
          </a-descriptions-item>
          <a-descriptions-item label="來源">
            <a-tag :color="getSourceColor(selectedError.source)">
              {{ getSourceLabel(selectedError.source) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="嚴重程度">
            <a-tag :color="getSeverityColor(selectedError.severity)">
              {{ getSeverityLabel(selectedError.severity) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="狀態">
            <a-tag :color="selectedError.is_resolved ? 'success' : 'error'">
              {{ selectedError.is_resolved ? '已解決' : '未解決' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="URL" v-if="selectedError.url">
            {{ selectedError.url }}
          </a-descriptions-item>
        </a-descriptions>
        
        <a-divider>錯誤訊息</a-divider>
        <pre class="error-message-detail">{{ selectedError.error_message }}</pre>
        
        <a-divider v-if="selectedError.stack_trace">堆疊追蹤</a-divider>
        <pre v-if="selectedError.stack_trace" class="stack-trace">{{ selectedError.stack_trace }}</pre>
      </div>
    </a-modal>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { 
  ExclamationCircleOutlined,
  CheckCircleOutlined, 
  WarningOutlined,
  PieChartOutlined
} from '@ant-design/icons-vue'
import axios from '../utils/axios'
import { formatDate, formatTimeAgo } from '../utils/dateUtils'

export default {
  name: 'ErrorLogs',
  components: {
    ExclamationCircleOutlined,
    CheckCircleOutlined,
    WarningOutlined,
    PieChartOutlined
  },
  setup() {
    const errorLogs = ref([])
    const filteredErrors = ref([])
    const stats = ref(null)
    const selectedError = ref(null)
    const showDetailModal = ref(false)
    const loading = ref(false)
    
    // 篩選條件
    const searchTerm = ref('')
    const filterStatus = ref('')
    const filterSource = ref('')
    const filterSeverity = ref('')
    
    // 分頁
    const currentPage = ref(1)
    const pageSize = ref(10)
    
    // 表格欄位定義
    const columns = [
      {
        title: '時間',
        dataIndex: 'created_at',
        key: 'created_at',
        width: 180,
        sorter: (a, b) => new Date(a.created_at) - new Date(b.created_at)
      },
      {
        title: '來源',
        dataIndex: 'source',
        key: 'source',
        width: 100,
        filters: [
          { text: '前端', value: 'frontend' },
          { text: '後端', value: 'backend' },
          { text: 'API', value: 'api' },
          { text: '資料庫', value: 'database' }
        ]
      },
      {
        title: '錯誤訊息',
        dataIndex: 'error_message',
        key: 'error_message',
        ellipsis: true
      },
      {
        title: '嚴重程度',
        dataIndex: 'severity',
        key: 'severity',
        width: 100,
        filters: [
          { text: '低', value: 'low' },
          { text: '中', value: 'medium' },
          { text: '高', value: 'high' },
          { text: '緊急', value: 'critical' }
        ]
      },
      {
        title: '狀態',
        dataIndex: 'is_resolved',
        key: 'is_resolved',
        width: 100,
        filters: [
          { text: '已解決', value: true },
          { text: '未解決', value: false }
        ]
      },
      {
        title: '操作',
        key: 'actions',
        width: 180,
        fixed: 'right'
      }
    ]
    
    // 分頁配置
    const paginationConfig = computed(() => ({
      current: currentPage.value,
      pageSize: pageSize.value,
      total: filteredErrors.value.length,
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: (total, range) => `第 ${range[0]}-${range[1]} 項，共 ${total} 項`
    }))
    
    // 分頁後的錯誤列表
    const paginatedErrors = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredErrors.value.slice(start, end)
    })
    
    // 載入資料
    const loadData = async () => {
      loading.value = true
      try {
        const [logsResponse, statsResponse] = await Promise.all([
          axios.get('/api/error-logs/'),
          axios.get('/api/error-logs/stats')
        ])
        
        errorLogs.value = logsResponse.data || []
        filteredErrors.value = [...errorLogs.value]
        stats.value = statsResponse.data || { total_errors: 0, resolved_errors: 0, unresolved_errors: 0 }
        
      } catch (error) {
        console.error('載入錯誤日誌失敗:', error)
        message.error('載入錯誤日誌失敗')
        errorLogs.value = []
        filteredErrors.value = []
        stats.value = { total_errors: 0, resolved_errors: 0, unresolved_errors: 0 }
      } finally {
        loading.value = false
      }
    }
    
    // 篩選錯誤
    const filterErrors = () => {
      let filtered = [...errorLogs.value]
      
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        filtered = filtered.filter(error => 
          error.error_message?.toLowerCase().includes(term) ||
          error.error_type?.toLowerCase().includes(term) ||
          error.url?.toLowerCase().includes(term)
        )
      }
      
      if (filterStatus.value !== '') {
        const isResolved = filterStatus.value === 'true'
        filtered = filtered.filter(error => error.is_resolved === isResolved)
      }
      
      if (filterSource.value) {
        filtered = filtered.filter(error => error.source === filterSource.value)
      }
      
      if (filterSeverity.value) {
        filtered = filtered.filter(error => error.severity === filterSeverity.value)
      }
      
      filteredErrors.value = filtered
      currentPage.value = 1 // 重置到第一頁
    }
    
    // 重置篩選
    const resetFilters = () => {
      searchTerm.value = ''
      filterStatus.value = ''
      filterSource.value = ''
      filterSeverity.value = ''
      filteredErrors.value = [...errorLogs.value]
      currentPage.value = 1
    }
    
    // 刷新資料
    const refreshData = () => {
      loadData()
    }
    
    // 清理已解決錯誤
    const cleanResolvedErrors = async () => {
      try {
        const response = await axios.post('/api/error-logs/clean-resolved')
        message.success(response.data.message || '清理完成')
        await loadData()
      } catch (error) {
        console.error('清理錯誤失敗:', error)
        message.error('清理錯誤失敗')
      }
    }
    
    // 清理舊錯誤
    const cleanOldErrors = async () => {
      try {
        const response = await axios.post('/api/error-logs/clean')
        message.success(response.data.message || '清理完成')
        await loadData()
      } catch (error) {
        console.error('清理錯誤失敗:', error)
        message.error('清理錯誤失敗')
      }
    }
    
    // 查看錯誤詳情
    const viewError = (error) => {
      selectedError.value = error
      showDetailModal.value = true
    }
    
    // 標記為已解決
    const markAsResolved = async (error) => {
      try {
        await axios.put(`/api/error-logs/${error.id}/resolve`)
        message.success('已標記為解決')
        await loadData()
      } catch (err) {
        console.error('標記解決失敗:', err)
        message.error('標記解決失敗')
      }
    }
    
    // 刪除錯誤
    const deleteError = async (error) => {
      try {
        await axios.delete(`/api/error-logs/${error.id}`)
        message.success('刪除成功')
        await loadData()
      } catch (err) {
        console.error('刪除錯誤失敗:', err)
        message.error('刪除錯誤失敗')
      }
    }
    
    // 表格變更處理
    const handleTableChange = (pagination) => {
      currentPage.value = pagination.current
      pageSize.value = pagination.pageSize
    }
    
    // 工具函數（已移至 utils/dateUtils.js）
    
    const getSourceLabel = (source) => {
      const labels = {
        frontend: '前端',
        backend: '後端',
        api: 'API',
        database: '資料庫'
      }
      return labels[source] || source
    }
    
    const getSourceColor = (source) => {
      const colors = {
        frontend: 'blue',
        backend: 'green',
        api: 'orange',
        database: 'purple'
      }
      return colors[source] || 'default'
    }
    
    const getSeverityLabel = (severity) => {
      const labels = {
        low: '低',
        medium: '中',
        high: '高',
        critical: '緊急'
      }
      return labels[severity] || severity
    }
    
    const getSeverityColor = (severity) => {
      const colors = {
        low: 'success',
        medium: 'warning',
        high: 'error',
        critical: 'red'
      }
      return colors[severity] || 'default'
    }
    
    const getResolvedRate = () => {
      if (!stats.value || stats.value.total_errors === 0) return 0
      return Math.round((stats.value.resolved_errors / stats.value.total_errors) * 100)
    }
    
    // 載入初始資料
    onMounted(() => {
      loadData()
    })
    
    return {
      errorLogs,
      filteredErrors,
      stats,
      selectedError,
      showDetailModal,
      loading,
      searchTerm,
      filterStatus,
      filterSource,
      filterSeverity,
      currentPage,
      pageSize,
      columns,
      paginationConfig,
      paginatedErrors,
      loadData,
      filterErrors,
      resetFilters,
      refreshData,
      cleanResolvedErrors,
      cleanOldErrors,
      viewError,
      markAsResolved,
      deleteError,
      handleTableChange,
      getSourceLabel,
      getSourceColor,
      getSeverityLabel,
      getSeverityColor,
      getResolvedRate
    }
  }
}
</script>

<style scoped>
.error-logs-page {
  background: #f0f2f5;
  min-height: 100vh;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e8e8e8;
}

.page-content {
  padding: 24px;
}

.stats-cards {
  margin-bottom: 24px;
}

.filter-card {
  margin-bottom: 24px;
}

.error-list-card {
  margin-bottom: 24px;
}

.error-message {
  max-width: 300px;
}

.error-title {
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 4px;
}

.error-text {
  color: #666;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.error-message-detail {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
}

.stack-trace {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 300px;
  overflow-y: auto;
  font-size: 12px;
}

.suffix-text {
  font-size: 14px;
  color: #666;
}
</style> 