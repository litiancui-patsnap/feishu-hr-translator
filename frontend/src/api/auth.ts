import { apiClient } from './client'
import { LoginRequest, TokenResponse, User } from '../types'

export const authAPI = {
  // Login with username and password
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/api/auth/login', data)
    return response.data
  },

  // Register new user
  register: async (data: {
    username: string
    password: string
    email?: string
    full_name?: string
  }): Promise<User> => {
    const response = await apiClient.post<User>('/api/auth/register', data)
    return response.data
  },

  // Get current user info
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/auth/me')
    return response.data
  },

  // Logout
  logout: async (): Promise<void> => {
    await apiClient.post('/api/auth/logout')
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  },
}
