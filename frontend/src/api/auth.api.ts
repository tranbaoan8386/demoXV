import apiClient from './client'

export interface LoginDTO {
  email: string
  password: string
}

export interface RegisterDTO {
  email: string
  username: string
  full_name: string
  password: string
}

export interface UserInfo {
  id?: string
  email: string
  username?: string
  full_name?: string
  role?: string
  status?: string
  is_active?: boolean
  created_at?: string
  updated_at?: string
}

export interface AuthResponse {
  success: boolean
  data: {
    user: UserInfo
    token: string
  }
}

export const authApi = {
  login(payload: LoginDTO) {
    return apiClient.post<AuthResponse>('/api/auth/login', payload)
  },

  register(payload: RegisterDTO) {
    return apiClient.post<AuthResponse>('/api/auth/register', payload)
  },

  verify(token?: string) {
    return apiClient.post<{ success: boolean; data: { user: UserInfo } }>('/api/auth/verify', undefined, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    })
  },
}
