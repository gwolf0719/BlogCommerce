<template>
  <div class="admin-page">
    <!-- 1. 頁面標題區 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">用戶管理</h1>
          <p class="page-description">管理系統中的所有用戶帳號和權限</p>
        </div>
        <div class="action-section">
          <a-button type="primary" @click="handleCreate">
            <template #icon><UserAddOutlined /></template>
            新增用戶
          </a-button>
        </div>
      </div>
    </div>

    <!-- 2. 統計卡片區 -->
    <div class="stats-section">
      <a-row :gutter="24" class="stats-row">
        <a-col :xs="24" :sm="12" :md="6" style="margin-bottom: 16px;">
          <a-card>
            <a-statistic
              title="總用戶數"
              :value="stats.total_users"
              prefix="👥"
              :value-style="{ color: '#1890ff' }"
            />
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="12" :md="6" style="margin-bottom: 16px;">
          <a-card>
            <a-statistic
              title="活躍用戶"
              :value="stats.active_users"
              prefix="🟢"
              :value-style="{ color: '#52c41a' }"
            />
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="12" :md="6" style="margin-bottom: 16px;">
          <a-card>
            <a-statistic
              title="管理員"
              :value="stats.admin_users"
              prefix="👑"
              :value-style="{ color: '#722ed1' }"
            />
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="12" :md="6" style="margin-bottom: 16px;">
          <a-card>
            <a-statistic
              title="今日新註冊"
              :value="stats.today_new_users"
              prefix="📅"
              :value-style="{ color: '#fa541c' }"
            />
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 3. 搜尋篩選區 -->
    <div class="filter-section">
      <a-card class="filter-card">
        <a-row :gutter="24" align="bottom">
          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="搜尋用戶">
              <a-input
                v-model:value="searchForm.search"
                placeholder="搜尋用戶名稱或郵箱"
                allow-clear
                @pressEnter="handleSearch"
              >
                <template #prefix><SearchOutlined /></template>
              </a-input>
            </a-form-item>
          </a-col>
          <a-col :xs="12" :sm="6" :md="4">
            <a-form-item label="角色">
              <a-select
                v-model:value="searchForm.role"
                placeholder="角色篩選"
                allow-clear
                style="width: 100%;"
                @change="handleSearch"
              >
                <a-select-option value="admin">管理員</a-select-option>
                <a-select-option value="user">一般用戶</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :xs="12" :sm="6" :md="4">
             <a-form-item label="狀態">
              <a-select
                v-model:value="searchForm.is_active"
                placeholder="狀態篩選"
                allow-clear
                style="width: 100%;"
                @change="handleSearch"
              >
                <a-select-option :value="true">啟用</a-select-option>
                <a-select-option :value="false">停用</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item>
              <a-space>
                <a-button type="primary" @click="handleSearch">搜尋</a-button>
                <a-button @click="resetSearch">重置篩選</a-button>
              </a-space>
            </a-form-item>
          </a-col>
        </a-row>
      </a-card>
    </div>

    <!-- 4. 主要內容區 -->
    <div class="content-section">
      <a-card class="content-card">
        <a-table
          :columns="columns"
          :data-source="users"
          :loading="loading"
          row-key="id"
          :pagination="paginationConfig"
          @change="handleTableChange"
          :scroll="{ x: 800 }"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'user_info'">
              <div class="flex items-center space-x-3">
                <a-avatar :src="record.avatar" :size="40">
                  {{ record.username?.[0]?.toUpperCase() || record.email?.[0]?.toUpperCase() }}
                </a-avatar>
                <div>
                  <div class="font-medium">{{ record.username || record.email }}</div>
                  <div class="text-gray-500 text-sm">{{ record.email }}</div>
                </div>
              </div>
            </template>

            <template v-if="column.key === 'role'">
              <a-tag :color="record.role === 'admin' ? 'red' : 'blue'">
                {{ record.role === 'admin' ? '管理員' : '一般會員' }}
              </a-tag>
            </template>

            <template v-if="column.key === 'is_active'">
              <a-tag :color="record.is_active ? 'green' : 'red'">
                {{ record.is_active ? '啟用' : '停用' }}
              </a-tag>
            </template>

            <template v-if="column.key === 'created_at'">
              <span>{{ formatDate(record.created_at) }}</span>
            </template>

            <template v-if="column.key === 'last_login'">
              <span>{{ formatDate(record.last_login) || '未曾登入' }}</span>
            </template>

            <template v-if="column.key === 'action'">
              <a-space>
                <a-button type="link" size="small" @click="handleEdit(record)">
                  <EditOutlined />
                </a-button>
                <a-button 
                  type="link" 
                  size="small" 
                  :class="record.is_active ? 'text-red-500' : 'text-green-500'"
                  @click="toggleUserStatus(record)"
                >
                  {{ record.is_active ? '停用' : '啟用' }}
                </a-button>
                <a-popconfirm 
                  title="確定刪除此會員？" 
                  ok-text="確定" 
                  cancel-text="取消" 
                  @confirm="handleDelete(record.id)"
                  v-if="record.id !== authStore.user?.id"
                >
                  <a-button type="link" danger size="small">
                    <DeleteOutlined />
                  </a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>

    <!-- 新增/編輯會員彈窗 -->
    <a-modal 
      v-model:open="modalVisible" 
      :title="isEdit ? '編輯會員' : '新增會員'" 
      width="600px" 
      :confirm-loading="submitLoading" 
      @ok="handleSubmit" 
      @cancel="handleCancel"
    >
      <a-form :model="form" :rules="rules" ref="formRef" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="用戶名" name="username">
              <a-input v-model:value="form.username" placeholder="輸入用戶名" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="信箱" name="email">
              <a-input v-model:value="form.email" placeholder="輸入信箱" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="密碼" name="password">
              <a-input-password 
                v-model:value="form.password" 
                :placeholder="isEdit ? '留空不修改密碼' : '輸入密碼'" 
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="確認密碼" name="confirmPassword">
              <a-input-password 
                v-model:value="form.confirmPassword" 
                :placeholder="isEdit ? '留空不修改密碼' : '再次輸入密碼'" 
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="角色" name="role">
              <a-select v-model:value="form.role">
                <a-select-option value="user">一般會員</a-select-option>
                <a-select-option value="admin">管理員</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="狀態" name="is_active">
              <a-switch v-model:checked="form.is_active" checked-children="啟用" un-checked-children="停用" />
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
  SearchOutlined, 
  EditOutlined, 
  DeleteOutlined,
  UserAddOutlined
} from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'
import { formatDate } from '../utils/dateUtils'
import api from '../utils/axios'

const authStore = useAuthStore()
const loading = ref(false)
const modalVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const formRef = ref()

// 數據
const users = ref([])
const stats = ref({
  total_users: 0,
  active_users: 0,
  today_new_users: 0,
  admin_users: 0
})

// 搜尋表單
const searchForm = reactive({
  search: '',
  role: undefined,
  is_active: undefined,
})

// 表單
const form = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'user',
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
  { title: '會員資訊', key: 'user_info', width: 250 },
  { title: '角色', key: 'role', dataIndex: 'role', width: 100 },
  { title: '狀態', key: 'is_active', dataIndex: 'is_active', width: 100 },
  { title: '註冊時間', key: 'created_at', dataIndex: 'created_at', width: 150, sorter: (a, b) => new Date(a.created_at) - new Date(b.created_at) },
  { title: '最後登入', key: 'last_login', dataIndex: 'last_login', width: 150 },
  { title: '操作', key: 'action', width: 150, fixed: 'right' }
]

// 表單驗證規則
const rules = {
  username: [{ required: true, message: '請輸入用戶名', trigger: 'blur' }],
  email: [{ required: true, message: '請輸入信箱', trigger: 'blur' }, { type: 'email', message: '請輸入正確的信箱格式', trigger: 'blur' }],
  password: [{ validator: (rule, value) => {
    if (!isEdit.value && !value) return Promise.reject('請輸入密碼');
    if (value && value.length < 6) return Promise.reject('密碼長度至少 6 字元');
    return Promise.resolve();
  }, trigger: 'blur' }],
  confirmPassword: [{ validator: (rule, value) => {
    if (form.password && form.password !== value) return Promise.reject('兩次輸入的密碼不一致');
    return Promise.resolve();
  }, trigger: 'blur' }],
  role: [{ required: true, message: '請選擇角色', trigger: 'change' }]
}

// 方法
const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.current - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      search: searchForm.search || undefined,
      role: searchForm.role || undefined,
      is_active: searchForm.is_active,
    };
    
    // 清理 undefined 的參數
    Object.keys(params).forEach(key => params[key] === undefined && delete params[key]);

    const response = await api.get('/api/admin/users', { params });
    users.value = response.data.items || [];
    pagination.total = response.data.total || 0;
  } catch (error) {
    message.error(error.response?.data?.detail || '獲取會員列表失敗');
  } finally {
    loading.value = false;
  }
}

const fetchStats = async () => {
  try {
    const response = await api.get('/api/admin/users/stats');
    stats.value = response.data;
  } catch (error) {
    console.log('統計資料 API 尚未實現或載入失敗');
  }
}

const handleSearch = () => {
  pagination.current = 1;
  fetchUsers();
}

const resetSearch = () => {
  searchForm.search = '';
  searchForm.role = undefined;
  searchForm.is_active = undefined;
  handleSearch();
}

const handleTableChange = (pag) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  fetchUsers();
}

const refreshUsers = () => {
  fetchUsers();
  fetchStats();
}

const handleCreate = () => {
  isEdit.value = false;
  resetForm();
  modalVisible.value = true;
}

const handleEdit = (user) => {
  isEdit.value = true;
  Object.assign(form, { ...user, password: '', confirmPassword: '' });
  modalVisible.value = true;
}

const resetForm = () => {
  Object.assign(form, {
    id: null, username: '', email: '', password: '', confirmPassword: '', role: 'user', is_active: true
  });
}

const handleCancel = () => {
  modalVisible.value = false;
  formRef.value?.resetFields();
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    submitLoading.value = true;
    
    const submitData = {
      username: form.username,
      email: form.email,
      role: form.role,
      is_active: form.is_active
    };
    if (form.password) {
      submitData.password = form.password;
    }

    const request = isEdit.value 
      ? api.put(`/api/admin/users/${form.id}`, submitData)
      : api.post('/api/admin/users', submitData);

    await request;
    message.success(`會員${isEdit.value ? '更新' : '新增'}成功`);
    modalVisible.value = false;
    refreshUsers();
  } catch (error) {
    if (!error.response) { // 表單驗證錯誤
      return;
    }
    message.error(error.response?.data?.detail || `${isEdit.value ? '更新' : '新增'}會員失敗`);
  } finally {
    submitLoading.value = false;
  }
}

const toggleUserStatus = async (user) => {
  try {
    await api.put(`/api/admin/users/${user.id}`, { is_active: !user.is_active });
    message.success(`會員已${user.is_active ? '停用' : '啟用'}`);
    refreshUsers();
  } catch (error) {
    message.error(error.response?.data?.detail || '更新會員狀態失敗');
  }
}

const handleDelete = async (userId) => {
  try {
    await api.delete(`/api/admin/users/${userId}`);
    message.success('會員已刪除');
    refreshUsers();
  } catch (error) {
    message.error(error.response?.data?.detail || '刪除會員失敗');
  }
}

onMounted(() => {
  refreshUsers();
})
</script>

<style scoped>
.admin-page { padding: 24px; }
.page-header { margin-bottom: 24px; }
.header-content { display: flex; justify-content: space-between; align-items: flex-start; }
.page-title { font-size: 24px; font-weight: 600; margin: 0 0 8px 0; color: #262626; }
.page-description { color: #8c8c8c; margin: 0; font-size: 14px; }
.stats-section { margin-bottom: 24px; }
.filter-section { margin-bottom: 24px; }
.content-section { margin-bottom: 24px; }
</style>
