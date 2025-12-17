import axios, { AxiosInstance } from 'axios'

// In production (Docker), use empty string to use same origin (Nginx will proxy /api/ to backend)
// In development, use localhost:8080
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.MODE === 'production' ? '' : 'http://localhost:8080')

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor: Add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor: Handle 401 errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  getInstance() {
    return this.client
  }
}

export const apiClient = new APIClient().getInstance()
export default apiClient
