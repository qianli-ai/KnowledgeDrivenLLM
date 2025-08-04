import axios from 'axios'

// Create axios instance
const request = axios.create({
  baseURL: '/api', // Use proxy path configured in vite.config.js
  timeout: 30000, // Request timeout
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
request.interceptors.request.use(
  config => {
    // Do something before sending request
    console.log('Sending request:', config)

    // Add token here if needed
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  error => {
    // Do something with request error
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
request.interceptors.response.use(
  response => {
    // Status codes in 2xx range will trigger this function
    console.log('Response data:', response)

    // Unified response data processing
    const { data, code, message } = response.data

    // Handle based on backend status code
    if (code === 2000 || code === 0) {
      // Return complete response data including data field
      return response.data
    } else {
      // Business error handling
      console.error('Business error:', message)
      return Promise.reject(new Error(message || 'Request failed'))
    }
  },
  error => {
    // Status codes outside 2xx range will trigger this function
    console.error('Response error:', error)

    let errorMessage = 'Network error'

    if (error.response) {
      // Server returned error status code
      const { status, data } = error.response

      switch (status) {
        case 400:
          errorMessage = 'Invalid request parameters'
          break
        case 401:
          errorMessage = 'Unauthorized, please login again'
          // Handle login expiration here
          localStorage.removeItem('token')
          // window.location.href = '/login'
          break
        case 403:
          errorMessage = 'Access denied'
          break
        case 404:
          errorMessage = 'Request address not found'
          break
        case 500:
          errorMessage = 'Internal server error'
          break
        default:
          errorMessage = data?.message || `Request failed (${status})`
      }
    } else if (error.request) {
      // Request was sent but no response received
      errorMessage = 'Network connection timeout'
    }

    return Promise.reject(new Error(errorMessage))
  }
)

export default request
