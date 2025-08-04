// Unified API exports
export { default as request } from './request'
export { uploadAPI } from './upload'
export { chatAPI } from './chat'
export { systemPromptAPI } from './systemPrompt'

// Alternative export for convenience
import uploadAPI from './upload'
import chatAPI from './chat'
import systemPromptAPI from './systemPrompt'

export const api = {
  upload: uploadAPI,
  chat: chatAPI,
  systemPrompt: systemPromptAPI
}

export default api
