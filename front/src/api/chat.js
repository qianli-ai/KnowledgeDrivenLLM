import request from './request'

/**
 * Chat related API
 */
export const chatAPI = {
  /**
   * Send message to chat interface
   * @param {Object} params - Request parameters
   * @param {string} params.prompt - User message content
   * @param {Array} params.history - Message history (optional)
   * @returns {Promise}
   */
  sendMessage(params) {
    return request.post('/chat/', params)
  }
}

export default chatAPI
