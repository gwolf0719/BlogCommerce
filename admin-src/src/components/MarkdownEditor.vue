<template>
  <div class="markdown-editor-container">
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <a-button size="small" @click="insertText('**', '**')" title="粗體">
          <strong>B</strong>
        </a-button>
        <a-button size="small" @click="insertText('*', '*')" title="斜體">
          <em>I</em>
        </a-button>
        <a-button size="small" @click="insertText('# ', '')" title="標題">
          H1
        </a-button>
        <a-button size="small" @click="insertText('[', '](url)')" title="連結">
          🔗
        </a-button>
        <a-button size="small" @click="insertText('```\n', '\n```')" title="程式碼">
          &lt;/&gt;
        </a-button>
        <a-divider type="vertical" />
        <a-upload
          :show-upload-list="false"
          :before-upload="beforeUpload"
          :custom-request="handleImageUpload"
          accept="image/*"
        >
          <a-button size="small" title="上傳圖片">
            <picture-outlined />
            圖片
          </a-button>
        </a-upload>
      </div>
      <div class="toolbar-right">
        <a-button size="small" @click="togglePreview" :type="showPreview ? 'primary' : 'default'">
          {{ showPreview ? '隱藏預覽' : '顯示預覽' }}
        </a-button>
      </div>
    </div>

    <div class="editor-content" :class="{ 'split-view': showPreview }">
      <div class="editor-pane">
        <a-textarea
          ref="editorRef"
          v-model:value="content"
          :placeholder="placeholder"
          :rows="rows"
          class="markdown-textarea"
          @input="handleInput"
          @keydown="handleKeydown"
        />
      </div>
      
      <div v-if="showPreview" class="preview-pane">
        <div class="preview-content" v-html="compiledMarkdown"></div>
      </div>
    </div>

    <div v-if="imageUploading" class="upload-progress">
      <a-progress :percent="uploadProgress" />
      <span>圖片上傳中...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import { PictureOutlined } from '@ant-design/icons-vue'
import { marked } from 'marked'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '請輸入 Markdown 內容...'
  },
  rows: {
    type: Number,
    default: 15
  }
})

const emit = defineEmits(['update:modelValue'])

const authStore = useAuthStore()
const editorRef = ref()
const content = ref(props.modelValue)
const showPreview = ref(false)
const imageUploading = ref(false)
const uploadProgress = ref(0)

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
  sanitize: false,
  highlight: function(code, lang) {
    // 簡單的程式碼高亮
    return `<pre><code class="language-${lang}">${code}</code></pre>`
  }
})

// 監聽 modelValue 變化
watch(() => props.modelValue, (newValue) => {
  content.value = newValue
})

// 監聽 content 變化，向父組件發射更新事件
watch(content, (newValue) => {
  emit('update:modelValue', newValue)
})

// 編譯 Markdown
const compiledMarkdown = computed(() => {
  try {
    return marked(content.value || '')
  } catch (error) {
    console.error('Markdown 解析錯誤:', error)
    return '<p>Markdown 解析錯誤</p>'
  }
})

// 輸入處理
const handleInput = (e) => {
  content.value = e.target.value
}

// 鍵盤快捷鍵
const handleKeydown = (e) => {
  if (e.ctrlKey || e.metaKey) {
    switch (e.key) {
      case 'b':
        e.preventDefault()
        insertText('**', '**')
        break
      case 'i':
        e.preventDefault()
        insertText('*', '*')
        break
      case 'k':
        e.preventDefault()
        insertText('[', '](url)')
        break
    }
  }
}

// 插入文字
const insertText = (before, after) => {
  const textarea = editorRef.value.resizableTextArea.textArea
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = content.value.substring(start, end)
  
  const newText = before + selectedText + after
  const newContent = content.value.substring(0, start) + newText + content.value.substring(end)
  
  content.value = newContent
  
  // 重新聚焦並設定游標位置
  setTimeout(() => {
    textarea.focus()
    if (selectedText) {
      textarea.setSelectionRange(start + before.length, end + before.length)
    } else {
      const newPosition = start + before.length
      textarea.setSelectionRange(newPosition, newPosition)
    }
  }, 0)
}

// 切換預覽
const togglePreview = () => {
  showPreview.value = !showPreview.value
}

// 上傳前檢查
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('只能上傳圖片文件!')
    return false
  }

  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    message.error('圖片大小不能超過 10MB!')
    return false
  }

  return true
}

// 處理圖片上傳
const handleImageUpload = async ({ file, onProgress, onSuccess, onError }) => {
  imageUploading.value = true
  uploadProgress.value = 0

  try {
    const formData = new FormData()
    formData.append('file', file)

    const xhr = new XMLHttpRequest()
    
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        uploadProgress.value = Math.round((e.loaded / e.total) * 100)
        onProgress && onProgress({ percent: uploadProgress.value })
      }
    }

    xhr.onload = () => {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)
        
        // 插入圖片 Markdown 語法
        const imageMarkdown = `\n![${file.name}](${response.url})\n`
        insertImageAtCursor(imageMarkdown)
        
        message.success('圖片上傳成功')
        onSuccess && onSuccess(response)
      } else {
        throw new Error('上傳失敗')
      }
    }

    xhr.onerror = () => {
      throw new Error('網路錯誤')
    }

    xhr.open('POST', '/api/admin/upload/image')
    xhr.setRequestHeader('Authorization', `Bearer ${authStore.token}`)
    xhr.send(formData)

  } catch (error) {
    message.error(error.message || '圖片上傳失敗')
    onError && onError(error)
  } finally {
    imageUploading.value = false
    uploadProgress.value = 0
  }
}

// 在游標位置插入圖片
const insertImageAtCursor = (imageMarkdown) => {
  const textarea = editorRef.value.resizableTextArea.textArea
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  
  const newContent = content.value.substring(0, start) + imageMarkdown + content.value.substring(end)
  content.value = newContent
  
  // 設定游標位置到插入文字的結尾
  setTimeout(() => {
    textarea.focus()
    const newPosition = start + imageMarkdown.length
    textarea.setSelectionRange(newPosition, newPosition)
  }, 0)
}
</script>

<style scoped>
.markdown-editor-container {
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  overflow: hidden;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #fafafa;
  border-bottom: 1px solid #d9d9d9;
}

.toolbar-left {
  display: flex;
  gap: 4px;
  align-items: center;
}

.toolbar-right {
  display: flex;
  gap: 4px;
}

.editor-content {
  display: flex;
  min-height: 400px;
}

.editor-content.split-view .editor-pane {
  width: 50%;
  border-right: 1px solid #d9d9d9;
}

.editor-content.split-view .preview-pane {
  width: 50%;
}

.editor-pane {
  width: 100%;
}

.markdown-textarea {
  border: none !important;
  box-shadow: none !important;
  resize: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.markdown-textarea:focus {
  border: none !important;
  box-shadow: none !important;
}

.preview-pane {
  padding: 16px;
  background: #fff;
  overflow-y: auto;
}

.preview-content {
  line-height: 1.6;
  color: #333;
}

/* Markdown 預覽樣式 */
.preview-content :deep(h1) {
  font-size: 2em;
  font-weight: bold;
  margin: 0.67em 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3em;
}

.preview-content :deep(h2) {
  font-size: 1.5em;
  font-weight: bold;
  margin: 0.83em 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3em;
}

.preview-content :deep(h3) {
  font-size: 1.17em;
  font-weight: bold;
  margin: 1em 0;
}

.preview-content :deep(h4),
.preview-content :deep(h5),
.preview-content :deep(h6) {
  font-weight: bold;
  margin: 1em 0;
}

.preview-content :deep(p) {
  margin: 1em 0;
}

.preview-content :deep(ul),
.preview-content :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.preview-content :deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 16px;
  margin: 1em 0;
  color: #666;
  background: #f9f9f9;
  padding: 10px 16px;
}

.preview-content :deep(code) {
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
}

.preview-content :deep(pre) {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 1em 0;
}

.preview-content :deep(pre code) {
  background: none;
  padding: 0;
}

.preview-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.preview-content :deep(th),
.preview-content :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.preview-content :deep(th) {
  background: #f5f5f5;
  font-weight: bold;
}

.preview-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin: 8px 0;
}

.upload-progress {
  padding: 8px 12px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #666;
}
</style> 