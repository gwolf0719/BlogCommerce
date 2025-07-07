<template>
  <div class="admin-page">
    <!-- 1. 頁面標題區 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">系統設定</h1>
          <p class="page-description">管理系統配置和功能選項</p>
        </div>
        <div class="action-section">
          <a-space>
            <a-button type="primary" @click="saveAllSettings" :loading="saving">
              <template #icon><SaveOutlined /></template>
              儲存所有設定
            </a-button>
            <a-button @click="refreshSettings">
              <template #icon><ReloadOutlined /></template>
              重新載入
            </a-button>
          </a-space>
        </div>
      </div>
    </div>

    <!-- 2. 主要內容區 -->
    <div class="content-section">
      <a-row :gutter="24">
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
                <template #icon><CreditCardOutlined /></template>
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
              <a-row :gutter="24">
                <a-col :span="12">
                  <a-form-item label="網站名稱">
                    <a-input v-model:value="settings.site_name" placeholder="輸入網站名稱" />
                    <div class="text-gray-500 text-sm mt-1">此名稱將顯示在首頁標題和導航列</div>
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="網站標語">
                    <a-input v-model:value="settings.site_tagline" placeholder="輸入網站標語" />
                    <div class="text-gray-500 text-sm mt-1">簡短的網站標語</div>
                  </a-form-item>
                </a-col>
              </a-row>
              
              <a-form-item label="網站描述">
                <a-textarea v-model:value="settings.site_description" :rows="3" placeholder="輸入網站描述" />
                <div class="text-gray-500 text-sm mt-1">此描述將用於首頁SEO和Open Graph標籤</div>
              </a-form-item>

              <a-form-item label="網站 Logo">
                <upload-image v-model="settings.site_logo" />
                <div class="text-gray-500 text-sm mt-1">建議尺寸：300x100px，支援PNG/JPG格式</div>
              </a-form-item>

              <a-form-item label="網站圖示 (Favicon)">
                <upload-image v-model="settings.site_favicon" />
                <div class="text-gray-500 text-sm mt-1">建議尺寸：32x32px，支援ICO/PNG格式</div>
              </a-form-item>
            </a-form>
          </a-card>

          <!-- 功能開關 -->
          <a-card v-if="activeTab === 'features'" title="功能開關" :loading="loading">
            <a-form layout="vertical">
              <a-row :gutter="24">
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

              <a-row :gutter="24">
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

              <a-row :gutter="24">
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

              <a-row :gutter="24">
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
                <a-row :gutter="24">
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

                <a-row :gutter="24">
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

              <a-row :gutter="24">
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

              <a-row :gutter="24">
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
              <a-row :gutter="24">
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

              <a-row :gutter="24">
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

              <a-row :gutter="24">
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
          <div v-if="activeTab === 'payment'" class="payment-settings">
            <!-- 運費設定區塊 -->
            <a-card class="shipping-settings-card" title="運費設定">
              <template #extra>
                <a-tag color="orange">
                  <CarOutlined />
                  運費配置
                </a-tag>
              </template>
              
              <a-form layout="vertical">
                <a-row :gutter="24">
                  <a-col :span="8">
                    <a-form-item>
                      <template #label>
                        <span class="form-label">
                          <MoneyCollectOutlined />
                          運費金額 (NT$)
                        </span>
                      </template>
                      <a-input-number 
                        v-model:value="shippingSettings.fee" 
                        :min="0"
                        :precision="0"
                        style="width: 100%"
                        placeholder="運費金額"
                        size="large"
                      />
                    </a-form-item>
                  </a-col>
                  <a-col :span="8">
                    <a-form-item>
                      <template #label>
                        <span class="form-label">
                          <GiftOutlined />
                          免運門檻 (NT$)
                        </span>
                      </template>
                      <a-input-number 
                        v-model:value="shippingSettings.freeThreshold" 
                        :min="0"
                        :precision="0"
                        style="width: 100%"
                        placeholder="免運門檻"
                        size="large"
                      />
                    </a-form-item>
                  </a-col>
                  <a-col :span="8">
                    <a-form-item>
                      <template #label>
                        <span class="form-label">
                          <SettingOutlined />
                          操作
                        </span>
                      </template>
                      <a-button type="primary" @click="saveShippingSettings" :loading="savingShipping" size="large">
                        儲存運費設定
                      </a-button>
                    </a-form-item>
                  </a-col>
                </a-row>
                
                <a-alert
                  message="運費設定說明"
                  description="設定基本運費金額和免運門檻。當消費者購買金額達到免運門檻時，將自動享受免運費優惠。"
                  type="info"
                  show-icon
                  style="margin-top: 16px;"
                />
              </a-form>
            </a-card>

            <!-- 金流方式選擇區塊 -->
            <a-card class="payment-methods-card" title="金流方式設定">
              <template #extra>
                <a-tag color="blue">
                  <CreditCardOutlined />
                  {{ payment.enabledMethods.length }} 種已啟用
                </a-tag>
              </template>
              
              <div class="payment-methods-grid">
                <div 
                  v-for="method in paymentMethods" 
                  :key="method.key"
                  class="payment-method-card"
                  :class="{ 'active': payment.enabledMethods.includes(method.key) }"
                  @click="togglePaymentMethod(method.key)"
                >
                  <div class="method-icon">
                    <component :is="method.icon" :style="{ color: method.color }" />
                  </div>
                  <div class="method-info">
                    <h4>{{ method.name }}</h4>
                    <p>{{ method.description }}</p>
                  </div>
                  <div class="method-toggle">
                    <a-switch 
                      :checked="payment.enabledMethods.includes(method.key)"
                      @change="(checked) => togglePaymentMethod(method.key, checked)"
                      :checked-children="'開'"
                      :un-checked-children="'關'"
                    />
                  </div>
                </div>
              </div>
            </a-card>

            <!-- 金流設定詳細區塊 -->
            <div class="payment-configs">
              <!-- 轉帳設定 -->
              <a-card 
                v-if="payment.enabledMethods.includes('transfer')" 
                class="config-card transfer-config"
                :loading="loading"
              >
                <template #title>
                  <div class="config-title">
                    <BankOutlined style="color: #1890ff; margin-right: 8px;" />
                    轉帳設定
                    <a-tag color="blue" size="small" style="margin-left: 8px;">銀行轉帳</a-tag>
                  </div>
                </template>
                
                <a-form layout="vertical">
                  <a-row :gutter="24">
                    <a-col :span="8">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <BankOutlined />
                            銀行名稱
                          </span>
                        </template>
                        <a-input 
                          v-model:value="payment.transfer.bank" 
                          placeholder="例如：台灣銀行、中國信託"
                          size="large"
                        />
                      </a-form-item>
                    </a-col>
                    <a-col :span="8">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <NumberOutlined />
                            帳號
                          </span>
                        </template>
                        <a-input 
                          v-model:value="payment.transfer.account" 
                          placeholder="請輸入完整帳號"
                          size="large"
                        />
                      </a-form-item>
                    </a-col>
                    <a-col :span="8">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <UserOutlined />
                            戶名
                          </span>
                        </template>
                        <a-input 
                          v-model:value="payment.transfer.name" 
                          placeholder="請輸入戶名"
                          size="large"
                        />
                      </a-form-item>
                    </a-col>
                  </a-row>
                </a-form>
              </a-card>

              <!-- Line Pay 設定 -->
              <a-card 
                v-if="payment.enabledMethods.includes('linepay')" 
                class="config-card linepay-config"
                :loading="loading"
              >
                <template #title>
                  <div class="config-title">
                    <MessageOutlined style="color: #00c300; margin-right: 8px;" />
                    Line Pay 設定
                    <a-tag color="green" size="small" style="margin-left: 8px;">即時付款</a-tag>
                  </div>
                </template>
                
                <a-form layout="vertical">
                  <a-row :gutter="24">
                    <a-col :span="8">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <KeyOutlined />
                            Channel ID
                          </span>
                        </template>
                        <a-input 
                          v-model:value="payment.linepay.channel_id" 
                          placeholder="請輸入 Line Pay Channel ID"
                          size="large"
                        />
                      </a-form-item>
                    </a-col>
                    <a-col :span="8">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <SafetyCertificateOutlined />
                            Channel Secret
                          </span>
                        </template>
                        <a-input-password 
                          v-model:value="payment.linepay.channel_secret" 
                          placeholder="請輸入 Channel Secret"
                          size="large"
                        />
                      </a-form-item>
                    </a-col>
                    <a-col :span="8">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <ShopOutlined />
                            商店名稱
                          </span>
                        </template>
                        <a-input 
                          v-model:value="payment.linepay.store_name" 
                          placeholder="顯示在付款頁面的商店名稱"
                          size="large"
                        />
                      </a-form-item>
                    </a-col>
                  </a-row>
                </a-form>
              </a-card>

              <!-- 綠界設定 -->
              <a-card 
                v-if="payment.enabledMethods.includes('ecpay')" 
                class="config-card ecpay-config"
                :loading="loading"
              >
                <template #title>
                  <div class="config-title">
                    <CreditCardOutlined style="color: #52c41a; margin-right: 8px;" />
                    綠界全方位金流設定
                    <a-tag color="green" size="small" style="margin-left: 8px;">多元付款</a-tag>
                  </div>
                </template>
                
                <a-form layout="vertical">
                  <a-row :gutter="24">
                    <a-col :span="12">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <IdcardOutlined />
                            Merchant ID
                          </span>
                        </template>
                        <a-input 
                          v-model:value="payment.ecpay.merchant_id" 
                          placeholder="請輸入綠界商店代號"
                          size="large"
                        />
                      </a-form-item>
                    </a-col>
                    <a-col :span="12">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <LinkOutlined />
                            API URL
                          </span>
                        </template>
                        <a-input 
                          v-model:value="payment.ecpay.api_url" 
                          placeholder="https://payment.ecpay.com.tw/..."
                          size="large"
                        />
                      </a-form-item>
                    </a-col>
                  </a-row>
                  <a-row :gutter="24">
                    <a-col :span="12">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <SafetyCertificateOutlined />
                            HashKey
                          </span>
                        </template>
                        <a-input-password 
                          v-model:value="payment.ecpay.hash_key" 
                          placeholder="請輸入 HashKey"
                          size="large"
                        />
                      </a-form-item>
                    </a-col>
                    <a-col :span="12">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <SafetyCertificateOutlined />
                            HashIV
                          </span>
                        </template>
                        <a-input-password 
                          v-model:value="payment.ecpay.hash_iv" 
                          placeholder="請輸入 HashIV"
                          size="large"
                        />
                      </a-form-item>
                    </a-col>
                  </a-row>
                </a-form>
              </a-card>

              <!-- PayPal 設定 -->
              <a-card 
                v-if="payment.enabledMethods.includes('paypal')" 
                class="config-card paypal-config"
                :loading="loading"
              >
                <template #title>
                  <div class="config-title">
                    <GlobalOutlined style="color: #0070ba; margin-right: 8px;" />
                    PayPal 設定
                    <a-tag color="blue" size="small" style="margin-left: 8px;">國際付款</a-tag>
                  </div>
                </template>
                
                <a-form layout="vertical">
                  <a-row :gutter="24">
                    <a-col :span="8">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <KeyOutlined />
                            Client ID
                          </span>
                        </template>
                        <a-input 
                          v-model:value="payment.paypal.client_id" 
                          placeholder="請輸入 PayPal Client ID"
                          size="large"
                        />
                      </a-form-item>
                    </a-col>
                    <a-col :span="8">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <SafetyCertificateOutlined />
                            Client Secret
                          </span>
                        </template>
                        <a-input-password 
                          v-model:value="payment.paypal.client_secret" 
                          placeholder="請輸入 PayPal Client Secret"
                          size="large"
                        />
                      </a-form-item>
                    </a-col>
                    <a-col :span="8">
                      <a-form-item>
                        <template #label>
                          <span class="form-label">
                            <EnvironmentOutlined />
                            環境設定
                          </span>
                        </template>
                        <a-select v-model:value="payment.paypal.environment" size="large">
                          <a-select-option value="sandbox">
                            <ExperimentOutlined /> Sandbox (測試環境)
                          </a-select-option>
                          <a-select-option value="live">
                            <RocketOutlined /> Live (正式環境)
                          </a-select-option>
                        </a-select>
                      </a-form-item>
                    </a-col>
                  </a-row>
                </a-form>
              </a-card>
            </div>

            <!-- 操作按鈕區 -->
            <a-card class="action-card">
              <div class="action-buttons">
                <a-button 
                  type="primary" 
                  size="large"
                  @click="savePaymentSettings" 
                  :loading="savingPayment"
                  class="save-btn"
                >
                  <SaveOutlined />
                  儲存金流設定
                </a-button>
                <a-button 
                  size="large"
                  @click="loadPaymentSettings" 
                  class="reload-btn"
                >
                  <ReloadOutlined />
                  重新載入
                </a-button>
                <a-button 
                  size="large"
                  @click="testPaymentConnection"
                  class="test-btn"
                >
                  <ExperimentOutlined />
                  測試連線
                </a-button>
              </div>
            </a-card>
          </div>
        </a-col>
      </a-row>
    </div>
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
  SafetyOutlined,
  CreditCardOutlined,
  BankOutlined,
  MessageOutlined,
  GlobalOutlined,
  KeyOutlined,
  SafetyCertificateOutlined,
  ShopOutlined,
  IdcardOutlined,
  LinkOutlined,
  NumberOutlined,
  UserOutlined,
  EnvironmentOutlined,
  ExperimentOutlined,
  RocketOutlined,
  CarOutlined,
  MoneyCollectOutlined,
  GiftOutlined
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

// 運費設定
const shippingSettings = reactive({
  fee: 60,
  freeThreshold: 1000
})
const savingShipping = ref(false)

// 金流方式配置
const paymentMethods = [
  {
    key: 'transfer',
    name: '銀行轉帳',
    description: '傳統銀行轉帳付款方式',
    icon: BankOutlined,
    color: '#1890ff'
  },
  {
    key: 'linepay',
    name: 'Line Pay',
    description: '便利的即時付款服務',
    icon: MessageOutlined,
    color: '#00c300'
  },
  {
    key: 'ecpay',
    name: '綠界金流',
    description: '支援多種付款方式',
    icon: CreditCardOutlined,
    color: '#52c41a'
  },
  {
    key: 'paypal',
    name: 'PayPal',
    description: '國際通用付款平台',
    icon: GlobalOutlined,
    color: '#0070ba'
  }
]

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

// 金流相關方法
const togglePaymentMethod = (methodKey, checked) => {
  if (checked === undefined) {
    // 點擊卡片切換
    const index = payment.enabledMethods.indexOf(methodKey)
    if (index > -1) {
      payment.enabledMethods.splice(index, 1)
    } else {
      payment.enabledMethods.push(methodKey)
    }
  } else {
    // Switch 切換
    if (checked) {
      if (!payment.enabledMethods.includes(methodKey)) {
        payment.enabledMethods.push(methodKey)
      }
    } else {
      const index = payment.enabledMethods.indexOf(methodKey)
      if (index > -1) {
        payment.enabledMethods.splice(index, 1)
      }
    }
  }
}

const testPaymentConnection = async () => {
  message.info('測試金流連線功能開發中...')
}

const loadPaymentSettings = async () => {
  loading.value = true
  try {
    // 使用統一的金流設定端點
    const response = await fetch('/api/settings/payment/settings', {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    
    if (response.ok) {
      const settings = await response.json()
      payment.enabledMethods = []
      
      // 檢查轉帳設定
      if (settings.transfer && settings.transfer.enabled) {
        payment.enabledMethods.push('transfer')
        payment.transfer = { bank: '台灣銀行', account: '123-456-789', name: 'BlogCommerce' }
      }
      
      // 檢查 LinePay 設定
      if (settings.linepay && settings.linepay.enabled) {
        payment.enabledMethods.push('linepay')
        payment.linepay = { channel_id: '', channel_secret: '', store_name: '' }
      }
      
      // 檢查綠界設定
      if (settings.ecpay && settings.ecpay.enabled) {
        payment.enabledMethods.push('ecpay')
        payment.ecpay = { merchant_id: '', api_url: '', hash_key: '', hash_iv: '' }
      }
      
      // 檢查 PayPal 設定
      if (settings.paypal && settings.paypal.enabled) {
        payment.enabledMethods.push('paypal')
        payment.paypal = { client_id: '', client_secret: '', environment: 'sandbox' }
      }
    }
    
  } catch (error) {
    console.error('載入金流設定失敗:', error)
    message.error('載入金流設定失敗')
  } finally {
    loading.value = false
  }
}

const savePaymentSettings = async () => {
  savingPayment.value = true
  try {
    // 使用正確的API端點更新金流啟用狀態
    const reqs = [
      fetch('/api/settings/payment_transfer_enabled', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` },
        body: JSON.stringify({ 
          value: payment.enabledMethods.includes('transfer') ? 'true' : 'false', 
          category: 'payment', 
          data_type: 'boolean' 
        })
      }),
      fetch('/api/settings/payment_linepay_enabled', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` },
        body: JSON.stringify({ 
          value: payment.enabledMethods.includes('linepay') ? 'true' : 'false', 
          category: 'payment', 
          data_type: 'boolean' 
        })
      }),
      fetch('/api/settings/payment_ecpay_enabled', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` },
        body: JSON.stringify({ 
          value: payment.enabledMethods.includes('ecpay') ? 'true' : 'false', 
          category: 'payment', 
          data_type: 'boolean' 
        })
      }),
      fetch('/api/settings/payment_paypal_enabled', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` },
        body: JSON.stringify({ 
          value: payment.enabledMethods.includes('paypal') ? 'true' : 'false', 
          category: 'payment', 
          data_type: 'boolean' 
        })
      })
    ]
    
    await Promise.all(reqs)
    message.success('金流設定已儲存')
  } catch (error) {
    console.error('儲存金流設定失敗:', error)
    message.error('儲存金流設定失敗')
  } finally {
    savingPayment.value = false
  }
}

// 運費設定相關方法
const loadShippingSettings = async () => {
  try {
    const feeResponse = await fetch('/api/settings/shipping_fee', {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    const thresholdResponse = await fetch('/api/settings/free_shipping_threshold', {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })

    if (feeResponse.ok) {
      const feeData = await feeResponse.json()
      shippingSettings.fee = feeData.value || 60
    }

    if (thresholdResponse.ok) {
      const thresholdData = await thresholdResponse.json()
      shippingSettings.freeThreshold = thresholdData.value || 1000
    }
  } catch (error) {
    message.error('載入運費設定失敗')
  }
}

const saveShippingSettings = async () => {
  savingShipping.value = true
  try {
    // 同時更新運費和免運門檻設定
    const reqs = [
      fetch('/api/settings/shipping_fee', {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json', 
          'Authorization': `Bearer ${authStore.token}` 
        },
        body: JSON.stringify({ 
          value: shippingSettings.fee, 
          category: 'shipping', 
          data_type: 'integer' 
        })
      }),
      fetch('/api/settings/free_shipping_threshold', {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json', 
          'Authorization': `Bearer ${authStore.token}` 
        },
        body: JSON.stringify({ 
          value: shippingSettings.freeThreshold, 
          category: 'shipping', 
          data_type: 'integer' 
        })
      })
    ]

    await Promise.all(reqs)
    message.success('運費設定已儲存')
  } catch (error) {
    message.error('儲存運費設定失敗')
  } finally {
    savingShipping.value = false
  }
}

// 初始化
onMounted(() => {
  loadSettings()
  loadPaymentSettings()
  loadShippingSettings()
})
</script>

<style scoped>
.ant-menu-vertical {
  border-right: none;
}

.ant-card-head-title {
  padding: 12px 0;
}

/* 金流設定樣式 */
.payment-settings {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.payment-methods-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  overflow: hidden;
}

.payment-methods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.payment-method-card {
  border: 2px solid #f0f0f0;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  position: relative;
  overflow: hidden;
}

.payment-method-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
  transform: translateY(-2px);
}

.payment-method-card.active {
  border-color: #1890ff;
  background: linear-gradient(135deg, #e6f7ff 0%, #f0f8ff 100%);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.2);
}

.method-icon {
  font-size: 32px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.method-info h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.method-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
}

.method-toggle {
  position: absolute;
  top: 20px;
  right: 20px;
}

.payment-configs {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.config-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.config-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #262626;
}

.transfer-config {
  border-left: 4px solid #1890ff;
}

.linepay-config {
  border-left: 4px solid #00c300;
}

.ecpay-config {
  border-left: 4px solid #52c41a;
}

.paypal-config {
  border-left: 4px solid #0070ba;
}

.action-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.save-btn {
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
  transition: all 0.3s ease;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(24, 144, 255, 0.4);
}

.reload-btn {
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.3);
  transition: all 0.3s ease;
}

.reload-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(82, 196, 26, 0.4);
}

.test-btn {
  background: linear-gradient(135deg, #fa8c16 0%, #d48806 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(250, 140, 22, 0.3);
  transition: all 0.3s ease;
}

.test-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(250, 140, 22, 0.4);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .payment-methods-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .ant-btn {
    width: 100%;
  }
}

/* 動畫效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.config-card {
  animation: fadeInUp 0.5s ease;
}

.payment-method-card {
  animation: fadeInUp 0.3s ease;
}

/* 表單樣式增強 */
.ant-input-affix-wrapper,
.ant-input,
.ant-select-selector {
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  transition: all 0.3s ease;
}

.ant-input-affix-wrapper:hover,
.ant-input:hover,
.ant-select-selector:hover {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.ant-input-affix-wrapper:focus,
.ant-input:focus,
.ant-select-focused .ant-select-selector {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}
</style> 