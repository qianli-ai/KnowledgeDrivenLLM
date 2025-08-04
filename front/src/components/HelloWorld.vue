<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  SearchOutlined,
  SettingOutlined,
  AppstoreOutlined,
  MessageOutlined,
  RobotOutlined,
  PlusCircleOutlined,
  ToolOutlined,
  AudioOutlined,
  SendOutlined,
  CopyOutlined,
  LikeOutlined,
  DislikeOutlined,
  SoundOutlined,
  ReloadOutlined,
  SaveOutlined,
  MoreOutlined,
  PictureOutlined,
  BulbOutlined,
  CodeOutlined,
  QuestionCircleOutlined,
  DownOutlined,
  ShareAltOutlined
} from '@ant-design/icons-vue'
import { uploadAPI, chatAPI } from '@/api'
import { marked } from 'marked'
import SystemPromptModal from './SystemPromptModal.vue'

// Chat message list
const messages = ref([])
// Current input content
const inputMessage = ref('')
// Whether to show toolbar
const showTools = ref(false)
// Loading state
const loading = ref(false)
// Current conversation ID
const currentConversationId = ref(null)
// File upload related
const uploadProgress = ref(0)
const isUploading = ref(false)
const fileInputRef = ref(null)
// System prompt modal
const showSystemPromptModal = ref(false)

// Configure marked options
marked.setOptions({
  breaks: true, // Convert \n to <br>
  gfm: true, // GitHub Flavored Markdown
  sanitize: false, // Allow HTML (be careful with user input)
  highlight: function(code, lang) {
    // You can add syntax highlighting here if needed
    return code
  }
})

// Render markdown content
const renderMarkdown = (content) => {
  return marked(content)
}

// Handle Enter key press
const handleEnterPress = (e) => {
  // If Shift key is held, allow line break
  if (e.shiftKey) {
    return
  }
  // Otherwise prevent default behavior and send message
  e.preventDefault()

  // Check if there's content to send
  if (!inputMessage.value.trim() || loading.value) {
    return
  }

  // Send message immediately
  sendMessage()
}

// Send message
const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = inputMessage.value.trim()
  // Clear input box immediately
  inputMessage.value = ''
  loading.value = true

  // Add user message
  const userMsg = {
    id: Date.now(),
    type: 'user',
    content: userMessage,
    timestamp: new Date().toLocaleTimeString()
  }
  messages.value.push(userMsg)

  // Add loading AI message
  const loadingMsg = {
    id: Date.now() + 1,
    type: 'ai',
    content: '',
    timestamp: new Date().toLocaleTimeString(),
    isLoading: true
  }
  messages.value.push(loadingMsg)
  console.log('Added loading message:', loadingMsg)

  try {
    // Prepare history messages (last 10 messages)
    const history = messages.value.slice(-10).map(msg => ({
      role: msg.type === 'user' ? 'user' : 'assistant',
      content: msg.content
    }))

    // Call real chat API
    const response = await chatAPI.sendMessage({
      query: userMessage,
      // history: history
    })

    // Update loading message with actual response
    console.log('Updating loading message with response:', response)
    const content = response.data?.answer || response.answer || 'Sorry, I cannot reply right now.'

    // Force reactive update by updating the message in the array
    const messageIndex = messages.value.findIndex(msg => msg.id === loadingMsg.id)
    if (messageIndex !== -1) {
      messages.value[messageIndex].content = content
      messages.value[messageIndex].isLoading = false
      messages.value[messageIndex].messageId = response.messageId || response.id
    }

    inputMessage.value = ''
    console.log('Loading message updated:', messages.value[messageIndex])
    console.log('Backend response data:', response)

  } catch (error) {
    console.error('Failed to send message:', error)
    message.error('Failed to send message: ' + error.message)

    // Update loading message with error
    const messageIndex = messages.value.findIndex(msg => msg.id === loadingMsg.id)
    if (messageIndex !== -1) {
      messages.value[messageIndex].content = 'Sorry, an error occurred while sending the message. Please try again later.'
      messages.value[messageIndex].isLoading = false
      messages.value[messageIndex].isError = true
    }
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// Check if chat is empty
const isEmptyChat = computed(() => messages.value.length === 0)

// Scroll to bottom when messages change
const scrollToBottom = () => {
  setTimeout(() => {
    const chatContent = document.querySelector('.chat-content')
    if (chatContent) {
      chatContent.scrollTop = chatContent.scrollHeight
    }
  }, 100)
}

// Watch message list changes and auto scroll to bottom
watch(() => messages.value.length, () => {
  scrollToBottom()
})

// Create new chat (mock)
const createNewChat = () => {
  messages.value = []
  message.success('New chat created successfully')
}

// Regenerate reply
const regenerateMessage = async (messageIndex) => {
  const msg = messages.value[messageIndex]
  if (!msg || msg.type !== 'ai') return

  // Find corresponding user message (previous message before AI message)
  const userMsgIndex = messageIndex - 1
  const userMsg = messages.value[userMsgIndex]
  if (!userMsg || userMsg.type !== 'user') {
    message.error('Cannot find corresponding user message')
    return
  }

  loading.value = true

  try {
    // Prepare history messages (excluding current AI message to be regenerated)
    const historyMessages = messages.value.slice(0, messageIndex)
    const history = historyMessages.slice(-10).map(m => ({
      role: m.type === 'user' ? 'user' : 'assistant',
      content: m.content
    }))

    // Call chat API to regenerate
    const response = await chatAPI.sendMessage({
      query: userMsg.content,
      // history: history
    })

    // Update AI message content
    msg.content = response.data?.answer || response.answer || response.answer || 'Sorry, regeneration failed.'
    msg.timestamp = new Date().toLocaleTimeString()

    message.success('Regenerated successfully')
    console.log('Regeneration response data:', response)

  } catch (error) {
    console.error('Regeneration failed:', error)
    message.error('Regeneration failed: ' + error.message)
  } finally {
    loading.value = false
  }
}

// Like/dislike message (mock)
const rateMessage = (messageIndex, action) => {
  message.success(action === 'like' ? 'Liked successfully' : 'Disliked successfully')
}

// Save message (mock)
const saveMessage = (messageIndex) => {
  message.success('Saved successfully')
}

// Copy message content (original markdown text)
const copyMessage = async (content) => {
  try {
    await navigator.clipboard.writeText(content)
    message.success('Copied successfully')
  } catch (error) {
    console.error('Copy failed:', error)
    message.error('Copy failed')
  }
}



// Trigger file selection
const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

// Handle file selection
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    uploadKnowledgeFile(file)
  }
  // Clear file input to allow selecting the same file again
  event.target.value = ''
}

// Upload knowledge file
const uploadKnowledgeFile = async (file) => {
  // Check file type
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/markdown',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ]

  if (!allowedTypes.includes(file.type)) {
    message.error('Unsupported file type. Please upload PDF, Word, Excel, TXT or Markdown files')
    return
  }

  // Check file size (limit to 10MB)
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    message.error('File size cannot exceed 10MB')
    return
  }

  isUploading.value = true
  uploadProgress.value = 0

  // Show upload start notification
  message.loading(`Starting to upload file: ${file.name}`, 1)

  try {
    const response = await uploadAPI.uploadKnowledge(file, {
      onProgress: (progress) => {
        uploadProgress.value = progress
      }
    })

    message.success(`Knowledge document "${file.name}" uploaded successfully!`)

    // You can add post-upload logic here
    // Such as refreshing knowledge base list, etc.

  } catch (error) {
    message.error(`Failed to upload file "${file.name}": ${error.message}`)
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}

// Open system prompt modal
const openSystemPromptModal = () => {
  showSystemPromptModal.value = true
}

// Handle system prompt save success
const handleSystemPromptSuccess = (prompt) => {
  message.success('System prompt set successfully')
  // You can add other logic here, such as refreshing chat, etc.
}


</script>

<template>
  <a-layout class="chat-container">
    <!-- Left sidebar -->
    <a-layout-sider class="sidebar" width="260">
      <div class="sidebar-header">
        <a-button type="text" class="icon-btn" @click="openSystemPromptModal" title="Set System Prompt">
          <setting-outlined />
        </a-button>
      </div>
      <div class="sidebar-actions">
        <!-- <a-button type="text" class="action-btn" block @click="createNewChat">
          New Chat
        </a-button> -->
        <a-button
          type="text"
          class="action-btn"
          block
          @click="triggerFileUpload"
          :loading="isUploading"
          :disabled="isUploading"
        >
          {{ isUploading ? `Uploading ${uploadProgress}%` : 'Upload Knowledge' }}
        </a-button>
      </div>

      <!-- Upload progress bar -->
      <div v-if="isUploading" class="upload-progress">
        <div class="upload-info">
          <span class="upload-text">Uploading...</span>
          <span class="upload-percent">{{ uploadProgress }}%</span>
        </div>
        <a-progress
          :percent="uploadProgress"
          :show-info="false"
          size="small"
          :stroke-color="{ '0%': '#108ee9', '100%': '#87d068' }"
        />
      </div>

      <!-- Hidden file input -->
      <input
        ref="fileInputRef"
        type="file"
        accept=".pdf,.doc,.docx,.txt,.md,.xls,.xlsx"
        style="display: none"
        @change="handleFileSelect"
      />
  
      <!-- <div class="sidebar-footer">
        <div class="user-info">
          <a-avatar class="user-avatar">Z</a-avatar>
          <div class="user-name">zhangbanshuo</div>
          <div class="user-plan">Free</div>
        </div>
      </div> -->
    </a-layout-sider>
    
    <!-- Main chat area -->
    <a-layout>
      <a-layout-content class="main-content">
      <!-- Top navigation -->
      <a-layout-header class="top-nav">
        <div class="chat-title">
          <!-- <a-menu-item>2</a-menu-item> -->
          <a-dropdown>
            <template #overlay>
              <a-menu>
                <a-menu-item>Logout</a-menu-item>
                <!-- <a-menu-item>2</a-menu-item> -->
              </a-menu>
            </template>
            <!-- <a-button type="text">
              <down-outlined />
            </a-button> -->
          </a-dropdown>
        </div>
        <div class="nav-actions">
          <a-button type="text" class="action-btn">
            <!-- <template #icon><share-alt-outlined /></template> -->
            <!-- Share -->
          </a-button>
          <!-- <a-button type="text">
            <more-outlined />
          </a-button> -->
        </div>
      </a-layout-header>
      
      <!-- Chat content area -->
      <div class="chat-content">
        <!-- Empty chat state -->
        <div v-if="isEmptyChat" class="empty-chat">
          <a-typography-title class="welcome-text" :level="1">What are you thinking about today?</a-typography-title>
        </div>
        
        <!-- Chat message list -->
        <div v-else class="message-list">
          <a-list :data-source="messages" :split="false" itemLayout="horizontal">
            <template #renderItem="{ item, index }">
              <a-list-item :class="['message', `message-${item.type}`, { 'error-message': item.isError }]">
                <div class="message-wrapper">
                  <!-- Avatar -->
                  <div class="message-avatar">
                    <img
                      :src="item.type === 'user' ? '/imagea/user.png' : '/imagea/aislogo.png'"
                      :alt="item.type === 'user' ? 'User' : 'AI'"
                      class="avatar-image"
                    />
                  </div>

                  <!-- Message content -->
                  <div class="message-content">
                    <!-- User messages display as plain text -->
                    <a-typography-paragraph v-if="item.type === 'user'">{{ item.content }}</a-typography-paragraph>
                    <!-- AI messages -->
                    <div v-else>
                      <!-- Loading state -->
                      <div v-if="item.isLoading" class="loading-content">
                        <div class="loading-dots">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                        <span class="loading-text">AI is thinking...</span>
                      </div>
                      <!-- Normal AI message content -->
                      <div v-else class="markdown-content" v-html="renderMarkdown(item.content)"></div>
                    </div>

                    <!-- AI message actions (only show when not loading) -->
                    <div v-if="item.type === 'ai' && !item.isLoading" class="message-actions">
                      <a-button type="text" size="small" @click="copyMessage(item.content)" title="Copy">
                        <copy-outlined />
                      </a-button>
                      <!-- <a-button type="text" size="small" @click="rateMessage(index, 'like')" title="Like">
                        <like-outlined />
                      </a-button> -->
                      <!-- <a-button type="text" size="small" @click="rateMessage(index, 'dislike')" title="Dislike">
                        <dislike-outlined />
                      </a-button> -->
                      <!-- <a-button type="text" size="small" title="Voice play">
                        <sound-outlined />
                      </a-button> -->
                      <a-button type="text" size="small" @click="regenerateMessage(index)" title="Regenerate">
                        <reload-outlined />
                      </a-button>
                      <!-- <a-button type="text" size="small" @click="saveMessage(index)" title="Save">
                        <save-outlined />
                      </a-button> -->
                      <!-- <a-button type="text" size="small" title="More">
                        <more-outlined />
                      </a-button> -->
                    </div>
                  </div>
                </div>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </div>
      
      <!-- Bottom input area -->
      <a-layout-footer class="input-area">
        <a-card bordered class="input-container" :bodyStyle="{padding: '8px'}">
          <div class="input-wrapper">
            <a-textarea
              v-model:value="inputMessage"
              placeholder="Ask any question"
              :autoSize="{ minRows: 3, maxRows: 5 }"
              @pressEnter="handleEnterPress"
              :bordered="false"
              :disabled="loading"
              class="chat-input"
            />
            <div class="input-actions">
              <!-- <a-button type="text" @click="showTools = !showTools"><plus-circle-outlined /></a-button> -->
              <!-- <a-button type="text" v-if="showTools"><tool-outlined /></a-button> -->
              <!-- <a-button type="text"><audio-outlined /></a-button> -->
              <a-button
                type="primary"
                @click="sendMessage"
                shape="circle"
                :loading="loading"
                :disabled="!inputMessage.trim() || loading"
              >
                <send-outlined v-if="!loading" />
              </a-button>
            </div>
          </div>
        </a-card>
        
        <!-- Bottom toolbar
        <a-space class="tools-bar" wrap>
          <a-button class="tool-btn">
            <template #icon><picture-outlined /></template>
            Create image
          </a-button>
          <a-button class="tool-btn">
            <template #icon><bulb-outlined /></template>
            Brainstorm
          </a-button>
          <a-button class="tool-btn">
            <template #icon><search-outlined /></template>
            Provide suggestions
          </a-button>
          <a-button class="tool-btn">
            <template #icon><code-outlined /></template>
            Code
          </a-button>
          <a-button class="tool-btn">
            <template #icon><question-circle-outlined /></template>
            Help me write
          </a-button>
          <a-button class="tool-btn">
            <template #icon><more-outlined /></template>
            More
          </a-button>
        </a-space> -->
        

      </a-layout-footer>
    </a-layout-content>
    </a-layout>

    <!-- System Prompt Modal -->
    <SystemPromptModal
      v-model:open="showSystemPromptModal"
      @success="handleSystemPromptSuccess"
    />
  </a-layout>
</template>

<style scoped>
/* Global layout */
:deep(.ant-layout) {
  background-color: white;
}

.chat-container {
  display: flex;
  width: 100%;
  height: 100vh;
  background-color: white;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

/* Sidebar style */
.sidebar {
  background-color: #f9f9f9 !important;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  padding: 10px;
  box-sizing: border-box;
}

.sidebar-header {
  padding: 10px 0;
  text-align: right;
}

.sidebar-actions {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 0;
}

.action-btn, .model-btn {
  text-align: left !important;
  justify-content: flex-start;
  margin-bottom: 4px;
}

.search-box {
  margin-bottom: 4px;
  background-color: #f0f0f0;
}

.sidebar-models {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 0;
}

.sidebar-footer {
  margin-top: auto;
  padding: 10px 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 6px;
}

.user-avatar {
  background-color: #0078d4;
  color: white;
}

.user-name {
  font-size: 14px;
}

.user-plan {
  font-size: 12px;
  color: #666;
  margin-left: auto;
}

.upload-progress {
  padding: 10px;
  margin-top: 10px;
  background-color: #f0f0f0;
  border-radius: 6px;
}

.upload-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 12px;
  color: #666;
}

.upload-percent {
  font-size: 12px;
  font-weight: 500;
  color: #1890ff;
}

/* Main content area */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: white !important;
}

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  border-bottom: 1px solid #e6e6e6;
  height: 64px;
  line-height: 64px;
  background-color: white !important;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 600;
  font-size: 16px;
  color: #000;
}

.nav-actions {
  display: flex;
  gap: 10px;
}

/* Chat content area */
.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  background-color: white;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.welcome-text {
  font-size: 28px !important;
  font-weight: normal !important;
  color: #000;
}

.message-list {
  width: 100%;
}

:deep(.ant-list-items) {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

:deep(.ant-list-item) {
  padding: 12px 0;
  border-bottom: none !important;
}

.message {
  max-width: 80%;
}

.message-user {
  align-self: flex-end;
}

.message-ai {
  align-self: flex-start;
}

.message-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
}

.message-user .message-wrapper {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-image {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #f0f0f0;
}

.message-content {
  flex: 1;
  line-height: 1.6;
  word-break: break-word;
  min-width: 0;
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.error-message .message-content {
  color: #ff4d4f;
  background-color: #fff2f0;
  border-left: 3px solid #ff4d4f;
  padding: 10px;
  border-radius: 4px;
}

/* Loading animation styles */
.loading-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  color: #666;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #1890ff;
  animation: loading-bounce 1.4s ease-in-out infinite both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

.loading-text {
  font-size: 14px;
  color: #666;
  font-style: italic;
}

@keyframes loading-bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Markdown content styling */
.markdown-content {
  line-height: 1.6;
  word-break: break-word;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  margin: 16px 0 8px 0;
  font-weight: 600;
  color: #1f2937;
}

.markdown-content h1 { font-size: 1.5em; }
.markdown-content h2 { font-size: 1.3em; }
.markdown-content h3 { font-size: 1.1em; }

.markdown-content p {
  margin: 8px 0;
  color: #374151;
}

.markdown-content code {
  background-color: #f3f4f6;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
  color: #e11d48;
}

.markdown-content pre {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 12px;
  margin: 12px 0;
  overflow-x: auto;
}

.markdown-content pre code {
  background: none;
  padding: 0;
  color: #333;
  font-size: 0.9em;
}

.markdown-content blockquote {
  border-left: 4px solid #d1d5db;
  margin: 12px 0;
  padding: 8px 16px;
  background-color: #f9fafb;
  color: #6b7280;
}

.markdown-content ul,
.markdown-content ol {
  margin: 8px 0;
  padding-left: 24px;
}

.markdown-content li {
  margin: 4px 0;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid #d1d5db;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content th {
  background-color: #f3f4f6;
  font-weight: 600;
}

.markdown-content a {
  color: #2563eb;
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

.markdown-content strong {
  font-weight: 600;
}

.markdown-content em {
  font-style: italic;
}

/* Input area */
.input-area {
  padding: 10px 20px 20px;
  background-color: white !important;
}

.input-container {
  border-radius: 8px !important;
  margin-bottom: 15px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

:deep(.ant-card-body) {
  padding: 8px !important;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
}

:deep(.ant-input) {
  border: none !important;
  box-shadow: none !important;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  padding: 8px 0;
}

.chat-input:focus {
  outline: none;
  border: none !important;
  box-shadow: none !important;
}

.input-actions {
  display: flex;
  gap: 5px;
  align-items: center;
}

.tools-bar {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  overflow-x: auto;
  padding: 5px 0;
  justify-content: center;
  flex-wrap: wrap;
}

.tool-btn {
  border-radius: 20px !important;
  display: flex;
  align-items: center;
  gap: 5px;
  height: auto;
  padding: 6px 12px;
  background-color: #f5f5f5;
  border: none;
  color: #333;
}

.footer-text {
  display: block;
  text-align: center;
  font-size: 12px;
  margin-top: 15px;
}
</style>
