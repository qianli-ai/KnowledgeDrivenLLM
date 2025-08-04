# API Interface Documentation

This project has encapsulated API request interfaces, including request interceptors, response interceptors, and error handling.

## File Structure

```
src/api/
├── index.js          # Unified export file
├── request.js        # axios request wrapper
├── chat.js          # Chat related API
├── upload.js        # File upload API
└── README.md        # Documentation
```

## Usage

### 1. Import API

```javascript
// Method 1: Import on demand
import { uploadAPI, chatAPI } from '@/api'

// Method 2: Unified import
import api from '@/api'
// Usage: api.upload.uploadKnowledge(), api.chat.sendMessage()
```

### 2. Usage in Vue Components

```javascript
<script setup>
import { ref } from 'vue'
import { uploadAPI, chatAPI } from '@/api'
import { message } from 'ant-design-vue'

const isUploading = ref(false)
const uploadProgress = ref(0)

// Upload file
const uploadFile = async (file) => {
  isUploading.value = true
  try {
    const response = await uploadAPI.uploadKnowledge(file, {
      onProgress: (progress) => {
        uploadProgress.value = progress
      }
    })
    console.log('Upload successful:', response)
    message.success('File uploaded successfully!')
  } catch (error) {
    message.error('Upload failed: ' + error.message)
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}

// Send chat message
const sendMessage = async (prompt) => {
  try {
    const response = await chatAPI.sendMessage({ prompt })
    console.log('AI reply:', response.data.prompt)
  } catch (error) {
    message.error('Send failed: ' + error.message)
  }
}
</script>
```

## API Interface Description

### File Upload API (uploadAPI)

- `uploadKnowledge(file, options)` - Upload knowledge document to knowledge base
  - `file`: File object to upload
  - `options.onProgress`: Upload progress callback function

### Chat API (chatAPI)

- `sendMessage(params)` - Send message to chat interface
  - `params.query`: User message content
  - `params.history`: Message history (optional)
  - **Response**: AI replies support full Markdown formatting including:
    - Headers, bold, italic text
    - Code blocks with syntax highlighting
    - Lists, tables, blockquotes
    - Links and other Markdown elements

## Configuration

### 1. Proxy Configuration

Proxy is configured in `vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://192.168.0.101:8000',
      changeOrigin: true,
      rewrite: path => path.replace(/^\/api/, '')
    }
  }
}
```

### 2. Request Interceptor

- Automatically add Authorization header (if token exists)
- Request logging
- Unified Content-Type setting

### 3. Response Interceptor

- Unified error handling
- Automatic 401 unauthorized handling (clear token)
- Business error code handling
- Network error handling

## Error Handling

All API calls return Promise, it's recommended to use try-catch for error handling:

```javascript
try {
  const result = await chatAPI.sendMessage({ prompt: 'Hello' })
  // Handle success result
} catch (error) {
  // Handle error
  console.error('API call failed:', error.message)
  message.error(error.message)
}
```

## Important Notes

1. All API calls are asynchronous, use async/await or .then()
2. Error messages are handled in interceptors, use error.message directly
3. Token is automatically read from localStorage and added to request headers
4. File upload supports progress callback for displaying upload progress
5. Request timeout is set to 30 seconds

## Extension

To add new API interfaces:

1. Add new methods in corresponding files
2. Export in `index.js`
3. Update this documentation
