import request from './request'

/**
 * System Prompt API
 */
export const systemPromptAPI = {
  /**
   * Save system prompt
   * @param {string} prompt - System prompt content
   * @returns {Promise}
   */
  savePrompt: (prompt) => {
    return request.post('/system-prompt/', {
      prompt
    })
  },

  /**
   * Get current system prompt
   * @returns {Promise}
   */
  getPrompt: () => {
    return request.get('/system-prompt/')
  }
}

export default systemPromptAPI
