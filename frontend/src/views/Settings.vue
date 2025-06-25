<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">系統設定</h1>
      <div class="space-x-2">
        <a-button type="primary" @click="saveAllSettings" :loading="saving">
          <template #icon><SaveOutlined /></template>
          儲存所有設定
        </a-button>
        <a-button @click="refreshSettings">
          <template #icon><ReloadOutlined /></template>
          重新載入
        </a-button>
      </div>
    </div>

    <a-row :gutter="16">
      <!-- 左側選單 -->
      <a-col :span="6">
        <a-card>
          <a-menu v-model:selected-keys="selectedKeys" mode="vertical" @click="handleMenuClick">
            <a-menu-item key="general">
              <template #icon><SettingOutlined /></template>
              基本設定
            </a-menu-item>
            <a-menu-item key="features">
              <template #icon><AppstoreOutlined /></template>
              功能開關
            </a-menu-item>
            <a-menu-item key="email">
              <template #icon><MailOutlined /></template>
              郵件設定
            </a-menu-item>
            <a-menu-item key="analytics">
              <template #icon><BarChartOutlined /></template>
              數據分析
            </a-menu-item>
            <a-menu-item key="ai">
              <template #icon><RobotOutlined /></template>
              AI 設定
            </a-menu-item>
            <a-menu-item key="security">
              <template #icon><SafetyOutlined /></template>
              安全設定
            </a-menu-item>
            <a-menu-item key="payment">
              <template #icon><span class="anticon"><i class="fa fa-credit-card"></i></span></template>
              金流設定
            </a-menu-item>
          </a-menu>
        </a-card>
      </a-col>

      <!-- 右側內容 -->
      <a-col :span="18">
        <!-- 基本設定 -->
        <a-card v-if="activeTab === 'general'" title="基本設定" :loading="loading">
          <a-form layout="vertical">
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="網站名稱">
                  <a-input v-model:value="settings.site_name" placeholder="輸入網站名稱" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="網站標語">
                  <a-input v-model:value="settings.site_tagline" placeholder="輸入網站標語" />
                </a-form-item>
              </a-col>
            </a-row>
            
            <a-form-item label="網站描述">
              <a-textarea v-model:value="settings.site_description" :rows="3" placeholder="輸入網站描述" />
            </a-form-item>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="網站網址">
                  <a-input v-model:value="settings.site_url" placeholder="https://example.com" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="管理員信箱">
                  <a-input v-model:value="settings.admin_email" placeholder="admin@example.com" />
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="時區">
                  <a-select v-model:value="settings.timezone" placeholder="選擇時區">
                    <a-select-option value="Asia/Taipei">Asia/Taipei</a-select-option>
                    <a-select-option value="UTC">UTC</a-select-option>
                    <a-select-option value="America/New_York">America/New_York</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="語言">
                  <a-select v-model:value="settings.language" placeholder="選擇語言">
                    <a-select-option value="zh-TW">繁體中文</a-select-option>
                    <a-select-option value="zh-CN">簡體中文</a-select-option>
                    <a-select-option value="en">English</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>

            <a-form-item label="網站 Logo">
              <upload-image v-model="settings.site_logo" />
            </a-form-item>

            <a-form-item label="網站圖示 (Favicon)">
              <upload-image v-model="settings.site_favicon" />
            </a-form-item>
          </a-form>
        </a-card>

        <!-- 功能開關 -->
        <a-card v-if="activeTab === 'features'" title="功能開關" :loading="loading">
          <a-form layout="vertical">
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="部落格功能">
                  <a-switch v-model:checked="settings.blog_enabled" checked-children="開啟" un-checked-children="關閉" />
                  <div class="text-gray-500 text-sm mt-1">啟用/停用部落格功能</div>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="商店功能">
                  <a-switch v-model:checked="settings.shop_enabled" checked-children="開啟" un-checked-children="關閉" />
                  <div class="text-gray-500 text-sm mt-1">啟用/停用電商功能</div>
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="會員註冊">
                  <a-switch v-model:checked="settings.user_registration" checked-children="開啟" un-checked-children="關閉" />
                  <div class="text-gray-500 text-sm mt-1">允許新用戶註冊</div>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="評論功能">
                  <a-switch v-model:checked="settings.comment_enabled" checked-children="開啟" un-checked-children="關閉" />
                  <div class="text-gray-500 text-sm mt-1">啟用/停用評論功能</div>
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="搜尋功能">
                  <a-switch v-model:checked="settings.search_enabled" checked-children="開啟" un-checked-children="關閉" />
                  <div class="text-gray-500 text-sm mt-1">啟用/停用搜尋功能</div>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="數據分析">
                  <a-switch v-model:checked="settings.analytics_enabled" checked-children="開啟" un-checked-children="關閉" />
                  <div class="text-gray-500 text-sm mt-1">啟用/停用訪客統計</div>
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="電子報">
                  <a-switch v-model:checked="settings.newsletter_enabled" checked-children="開啟" un-checked-children="關閉" />
                  <div class="text-gray-500 text-sm mt-1">啟用/停用電子報功能</div>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="維護模式">
                  <a-switch v-model:checked="settings.maintenance_mode" checked-children="開啟" un-checked-children="關閉" />
                  <div class="text-gray-500 text-sm mt-1">網站維護模式</div>
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </a-card>

        <!-- 郵件設定 -->
        <a-card v-if="activeTab === 'email'" title="郵件設定" :loading="loading">
          <a-form layout="vertical">
            <a-form-item label="郵件服務商">
              <a-select v-model:value="settings.email_provider" placeholder="選擇郵件服務商">
                <a-select-option value="smtp">SMTP</a-select-option>
                <a-select-option value="mailgun">Mailgun</a-select-option>
                <a-select-option value="sendgrid">SendGrid</a-select-option>
                <a-select-option value="ses">Amazon SES</a-select-option>
              </a-select>
            </a-form-item>

            <div v-if="settings.email_provider === 'smtp'">
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="SMTP 主機">
                    <a-input v-model:value="settings.smtp_host" placeholder="smtp.gmail.com" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="SMTP 端口">
                    <a-input-number v-model:value="settings.smtp_port" :min="1" :max="65535" style="width: 100%" />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="SMTP 用戶名">
                    <a-input v-model:value="settings.smtp_username" placeholder="your-email@gmail.com" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="SMTP 密碼">
                    <a-input-password v-model:value="settings.smtp_password" placeholder="應用程式密碼" />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-form-item label="加密方式">
                <a-select v-model:value="settings.smtp_encryption">
                  <a-select-option value="tls">TLS</a-select-option>
                  <a-select-option value="ssl">SSL</a-select-option>
                  <a-select-option value="none">無</a-select-option>
                </a-select>
              </a-form-item>
            </div>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="寄件者名稱">
                  <a-input v-model:value="settings.email_from_name" placeholder="網站名稱" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="寄件者信箱">
                  <a-input v-model:value="settings.email_from_address" placeholder="noreply@example.com" />
                </a-form-item>
              </a-col>
            </a-row>

            <a-form-item>
              <a-button @click="testEmail" :loading="testingEmail">測試郵件</a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- 數據分析設定 -->
        <a-card v-if="activeTab === 'analytics'" title="數據分析設定" :loading="loading">
          <a-form layout="vertical">
            <a-form-item label="Google Analytics">
              <a-input v-model:value="settings.google_analytics_id" placeholder="G-XXXXXXXXXX" />
              <div class="text-gray-500 text-sm mt-1">輸入 Google Analytics 追蹤 ID</div>
            </a-form-item>

            <a-form-item label="Google Tag Manager">
              <a-input v-model:value="settings.google_tag_manager_id" placeholder="GTM-XXXXXXX" />
              <div class="text-gray-500 text-sm mt-1">輸入 Google Tag Manager 容器 ID</div>
            </a-form-item>

            <a-form-item label="Facebook Pixel">
              <a-input v-model:value="settings.facebook_pixel_id" placeholder="123456789012345" />
              <div class="text-gray-500 text-sm mt-1">輸入 Facebook Pixel ID</div>
            </a-form-item>

            <a-form-item label="數據保留期限">
              <a-select v-model:value="settings.analytics_retention_days">
                <a-select-option :value="30">30 天</a-select-option>
                <a-select-option :value="90">90 天</a-select-option>
                <a-select-option :value="365">365 天</a-select-option>
                <a-select-option :value="0">永久保留</a-select-option>
              </a-select>
              <div class="text-gray-500 text-sm mt-1">超過期限的數據將自動刪除</div>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- AI 設定 -->
        <a-card v-if="activeTab === 'ai'" title="AI 設定" :loading="loading">
          <a-form layout="vertical">
            <a-form-item label="OpenAI API Key">
              <a-input-password v-model:value="settings.openai_api_key" placeholder="sk-..." />
              <div class="text-gray-500 text-sm mt-1">用於 AI 內容生成功能</div>
            </a-form-item>

            <a-form-item label="AI 模型">
              <a-select v-model:value="settings.ai_model">
                <a-select-option value="gpt-3.5-turbo">GPT-3.5 Turbo</a-select-option>
                <a-select-option value="gpt-4">GPT-4</a-select-option>
                <a-select-option value="gpt-4-turbo">GPT-4 Turbo</a-select-option>
              </a-select>
            </a-form-item>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="AI 內容生成">
                  <a-switch v-model:checked="settings.ai_content_generation" checked-children="開啟" un-checked-children="關閉" />
                  <div class="text-gray-500 text-sm mt-1">啟用 AI 協助寫作</div>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="AI 圖片生成">
                  <a-switch v-model:checked="settings.ai_image_generation" checked-children="開啟" un-checked-children="關閉" />
                  <div class="text-gray-500 text-sm mt-1">啟用 AI 圖片生成</div>
                </a-form-item>
              </a-col>
            </a-row>

            <a-form-item label="AI 提示語溫度">
              <a-slider v-model:value="settings.ai_temperature" :min="0" :max="1" :step="0.1" />
              <div class="text-gray-500 text-sm mt-1">控制 AI 回應的創造性 (0 = 保守, 1 = 創造)</div>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- 安全設定 -->
        <a-card v-if="activeTab === 'security'" title="安全設定" :loading="loading">
          <a-form layout="vertical">
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="登入失敗限制">
                  <a-input-number v-model:value="settings.login_attempts_limit" :min="1" :max="20" style="width: 100%" />
                  <div class="text-gray-500 text-sm mt-1">連續登入失敗次數限制</div>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="鎖定時間 (分鐘)">
                  <a-input-number v-model:value="settings.lockout_duration" :min="1" :max="1440" style="width: 100%" />
                  <div class="text-gray-500 text-sm mt-1">達到限制後的鎖定時間</div>
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="Session 超時 (小時)">
                  <a-input-number v-model:value="settings.session_timeout" :min="1" :max="168" style="width: 100%" />
                  <div class="text-gray-500 text-sm mt-1">用戶 Session 過期時間</div>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="密碼最小長度">
                  <a-input-number v-model:value="settings.password_min_length" :min="6" :max="50" style="width: 100%" />
                  <div class="text-gray-500 text-sm mt-1">用戶密碼最小長度要求</div>
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="強制 HTTPS">
                  <a-switch v-model:checked="settings.force_https" checked-children="開啟" un-checked-children="關閉" />
                  <div class="text-gray-500 text-sm mt-1">強制使用 HTTPS 連線</div>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="二步驟驗證">
                  <a-switch v-model:checked="settings.two_factor_auth" checked-children="開啟" un-checked-children="關閉" />
                  <div class="text-gray-500 text-sm mt-1">啟用二步驟驗證</div>
                </a-form-item>
              </a-col>
            </a-row>

            <a-form-item label="允許的檔案類型">
              <a-select v-model:value="settings.allowed_file_types" mode="multiple" placeholder="選擇允許上傳的檔案類型">
                <a-select-option value="jpg">JPG</a-select-option>
                <a-select-option value="png">PNG</a-select-option>
                <a-select-option value="gif">GIF</a-select-option>
                <a-select-option value="webp">WebP</a-select-option>
                <a-select-option value="pdf">PDF</a-select-option>
                <a-select-option value="doc">DOC</a-select-option>
                <a-select-option value="docx">DOCX</a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="檔案大小限制 (MB)">
              <a-input-number v-model:value="settings.max_file_size" :min="1" :max="100" style="width: 100%" />
              <div class="text-gray-500 text-sm mt-1">單一檔案上傳大小限制</div>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- 金流設定 -->
        <a-card v-if="activeTab === 'payment'" title="金流設定" :loading="loading">
          <a-form layout="vertical">
            <a-form-item label="啟用金流方式">
              <a-checkbox-group v-model:value="payment.enabledMethods">
                <a-checkbox value="transfer">轉帳</a-checkbox>
                <a-checkbox value="linepay">Line Pay</a-checkbox>
                <a-checkbox value="ecpay">綠界全方位金流</a-checkbox>
                <a-checkbox value="paypal">PayPal</a-checkbox>
              </a-checkbox-group>
            </a-form-item>
            <template v-if="payment.enabledMethods.includes('transfer')">
              <a-divider>轉帳設定</a-divider>
              <a-form-item label="銀行名稱">
                <a-input v-model:value="payment.transfer.bank" placeholder="請輸入銀行名稱" />
              </a-form-item>
              <a-form-item label="帳號">
                <a-input v-model:value="payment.transfer.account" placeholder="請輸入帳號" />
              </a-form-item>
              <a-form-item label="戶名">
                <a-input v-model:value="payment.transfer.name" placeholder="請輸入戶名" />
              </a-form-item>
            </template>
            <template v-if="payment.enabledMethods.includes('linepay')">
              <a-divider>Line Pay 設定</a-divider>
              <a-form-item label="Channel ID">
                <a-input v-model:value="payment.linepay.channel_id" placeholder="請輸入 Channel ID" />
              </a-form-item>
              <a-form-item label="Channel Secret">
                <a-input v-model:value="payment.linepay.channel_secret" placeholder="請輸入 Channel Secret" />
              </a-form-item>
              <a-form-item label="商店名稱">
                <a-input v-model:value="payment.linepay.store_name" placeholder="請輸入商店名稱" />
              </a-form-item>
            </template>
            <template v-if="payment.enabledMethods.includes('ecpay')">
              <a-divider>綠界全方位金流設定</a-divider>
              <a-form-item label="Merchant ID">
                <a-input v-model:value="payment.ecpay.merchant_id" placeholder="請輸入 Merchant ID" />
              </a-form-item>
              <a-form-item label="HashKey">
                <a-input v-model:value="payment.ecpay.hash_key" placeholder="請輸入 HashKey" />
              </a-form-item>
              <a-form-item label="HashIV">
                <a-input v-model:value="payment.ecpay.hash_iv" placeholder="請輸入 HashIV" />
              </a-form-item>
              <a-form-item label="API URL">
                <a-input v-model:value="payment.ecpay.api_url" placeholder="請輸入 API URL" />
              </a-form-item>
            </template>
            
            <!-- PayPal 設定 -->
            <template v-if="payment.enabledMethods.includes('paypal')">
              <a-divider>PayPal 設定</a-divider>
              <a-form-item label="Client ID">
                <a-input v-model:value="payment.paypal.client_id" placeholder="請輸入 PayPal Client ID" />
              </a-form-item>
              <a-form-item label="Client Secret">
                <a-input-password v-model:value="payment.paypal.client_secret" placeholder="請輸入 PayPal Client Secret" />
              </a-form-item>
              <a-form-item label="環境">
                <a-select v-model:value="payment.paypal.environment">
                  <a-select-option value="sandbox">Sandbox (測試)</a-select-option>
                  <a-select-option value="live">Live (正式)</a-select-option>
                </a-select>
              </a-form-item>
            </template>
            
            <a-form-item>
              <a-button type="primary" @click="savePaymentSettings" :loading="savingPayment">儲存金流設定</a-button>
              <a-button @click="loadPaymentSettings" style="margin-left: 8px">重新載入</a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { 
  SaveOutlined, 
  ReloadOutlined, 
  SettingOutlined, 
  AppstoreOutlined, 
  MailOutlined, 
  BarChartOutlined, 
  RobotOutlined, 
  SafetyOutlined 
} from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'
import UploadImage from '../components/UploadImage.vue'

const authStore = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const testingEmail = ref(false)

const selectedKeys = ref(['general'])
const activeTab = ref('general')

// 設定數據
const settings = reactive({
  // 基本設定
  site_name: '',
  site_tagline: '',
  site_description: '',
  site_url: '',
  admin_email: '',
  timezone: 'Asia/Taipei',
  language: 'zh-TW',
  site_logo: '',
  site_favicon: '',

  // 功能開關
  blog_enabled: true,
  shop_enabled: true,
  user_registration: true,
  comment_enabled: true,
  search_enabled: true,
  analytics_enabled: true,
  newsletter_enabled: false,
  maintenance_mode: false,

  // 郵件設定
  email_provider: 'smtp',
  smtp_host: '',
  smtp_port: 587,
  smtp_username: '',
  smtp_password: '',
  smtp_encryption: 'tls',
  email_from_name: '',
  email_from_address: '',

  // 數據分析
  google_analytics_id: '',
  google_tag_manager_id: '',
  facebook_pixel_id: '',
  analytics_retention_days: 365,

  // AI 設定
  openai_api_key: '',
  ai_model: 'gpt-3.5-turbo',
  ai_content_generation: false,
  ai_image_generation: false,
  ai_temperature: 0.7,

  // 安全設定
  login_attempts_limit: 5,
  lockout_duration: 15,
  session_timeout: 24,
  password_min_length: 8,
  force_https: false,
  two_factor_auth: false,
  allowed_file_types: ['jpg', 'png', 'gif', 'webp'],
  max_file_size: 10
})

const payment = reactive({
  enabledMethods: [],
  transfer: { bank: '', account: '', name: '' },
  linepay: { channel_id: '', channel_secret: '', store_name: '' },
  ecpay: { merchant_id: '', hash_key: '', hash_iv: '', api_url: '' },
  paypal: { client_id: '', client_secret: '', environment: 'sandbox' }
})
const savingPayment = ref(false)

// 方法
const handleMenuClick = ({ key }) => {
  activeTab.value = key
  selectedKeys.value = [key]
}

const loadSettings = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/admin/settings', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!response.ok) {
      throw new Error('載入設定失敗')
    }

    const data = await response.json()
    
    // 更新設定值
    Object.keys(settings).forEach(key => {
      if (data[key] !== undefined) {
        settings[key] = data[key]
      }
    })

  } catch (error) {
    console.log('設定 API 尚未實現，使用預設值')
    // 使用預設值
  } finally {
    loading.value = false
  }
}

const saveAllSettings = async () => {
  saving.value = true
  try {
    const response = await fetch('/api/admin/settings', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(settings)
    })

    if (!response.ok) {
      throw new Error('儲存設定失敗')
    }

    message.success('設定已儲存')

  } catch (error) {
    message.error(error.message || '儲存設定失敗')
  } finally {
    saving.value = false
  }
}

const refreshSettings = () => {
  loadSettings()
}

const testEmail = async () => {
  testingEmail.value = true
  try {
    const response = await fetch('/api/admin/test-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        to: settings.admin_email,
        subject: '郵件設定測試',
        content: '這是一封測試郵件，如果您收到這封郵件，表示郵件設定正確。'
      })
    })

    if (!response.ok) {
      throw new Error('發送測試郵件失敗')
    }

    message.success('測試郵件已發送，請檢查您的信箱')

  } catch (error) {
    message.error(error.message || '發送測試郵件失敗')
  } finally {
    testingEmail.value = false
  }
}

const loadPaymentSettings = async () => {
  loading.value = true
  try {
    // 取得四種金流設定
    const [transferRes, linepayRes, ecpayRes, paypalRes] = await Promise.all([
      fetch('/api/settings/payment_transfer', { headers: { 'Authorization': `Bearer ${authStore.token}` } }),
      fetch('/api/settings/payment_linepay', { headers: { 'Authorization': `Bearer ${authStore.token}` } }),
      fetch('/api/settings/payment_ecpay', { headers: { 'Authorization': `Bearer ${authStore.token}` } }),
      fetch('/api/settings/payment_paypal', { headers: { 'Authorization': `Bearer ${authStore.token}` } })
    ])
    payment.enabledMethods = []
    if (transferRes.ok) {
      const t = await transferRes.json()
      if (t.value) {
        payment.transfer = t.value
        payment.enabledMethods.push('transfer')
      }
    }
    if (linepayRes.ok) {
      const l = await linepayRes.json()
      if (l.value) {
        payment.linepay = l.value
        payment.enabledMethods.push('linepay')
      }
    }
    if (ecpayRes.ok) {
      const e = await ecpayRes.json()
      if (e.value) {
        payment.ecpay = e.value
        payment.enabledMethods.push('ecpay')
      }
    }
    if (paypalRes.ok) {
      const p = await paypalRes.json()
      if (p.value) {
        payment.paypal = p.value
        payment.enabledMethods.push('paypal')
      }
    }
  } catch (e) {
    message.error('載入金流設定失敗')
  } finally {
    loading.value = false
  }
}

const savePaymentSettings = async () => {
  savingPayment.value = true
  try {
    // 依啟用狀態分別儲存
    const reqs = []
    if (payment.enabledMethods.includes('transfer')) {
      reqs.push(fetch('/api/settings/payment_transfer', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` },
        body: JSON.stringify({ value: payment.transfer, category: 'payment', data_type: 'json' })
      }))
    } else {
      reqs.push(fetch('/api/settings/payment_transfer', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` },
        body: JSON.stringify({ value: null, category: 'payment', data_type: 'json' })
      }))
    }
    if (payment.enabledMethods.includes('linepay')) {
      reqs.push(fetch('/api/settings/payment_linepay', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` },
        body: JSON.stringify({ value: payment.linepay, category: 'payment', data_type: 'json' })
      }))
    } else {
      reqs.push(fetch('/api/settings/payment_linepay', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` },
        body: JSON.stringify({ value: null, category: 'payment', data_type: 'json' })
      }))
    }
    if (payment.enabledMethods.includes('ecpay')) {
      reqs.push(fetch('/api/settings/payment_ecpay', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` },
        body: JSON.stringify({ value: payment.ecpay, category: 'payment', data_type: 'json' })
      }))
    } else {
      reqs.push(fetch('/api/settings/payment_ecpay', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` },
        body: JSON.stringify({ value: null, category: 'payment', data_type: 'json' })
      }))
    }
    if (payment.enabledMethods.includes('paypal')) {
      reqs.push(fetch('/api/settings/payment_paypal', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` },
        body: JSON.stringify(payment.paypal)
      }))
    } else {
      reqs.push(fetch('/api/settings/payment_paypal', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` },
        body: JSON.stringify(null)
      }))
    }
    await Promise.all(reqs)
    message.success('金流設定已儲存')
  } catch (e) {
    message.error('儲存金流設定失敗')
  } finally {
    savingPayment.value = false
  }
}

// 初始化
onMounted(() => {
  loadSettings()
  loadPaymentSettings()
})
</script>

<style scoped>
.ant-menu-vertical {
  border-right: none;
}

.ant-card-head-title {
  padding: 12px 0;
}
</style> 