import request from './request'

/**
 * File upload API
 */
export const uploadAPI = {
  /**
   * Upload knowledge document to knowledge base
   * @param {File} file - Document file
   * @param {Object} options - Upload options
   * @param {Function} options.onProgress - Upload progress callback
   * @returns {Promise}
   */
  uploadKnowledge(file, options = {}) {
    const formData = new FormData()
    formData.append('file', file)

    return request.post('/uploadfile/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (options.onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          options.onProgress(progress)
        }
      }
    })
  }
}

export default uploadAPI
