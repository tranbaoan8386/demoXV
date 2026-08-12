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

export interface VerifyAuthResponse {
  success: boolean
  data: {
    user: UserInfo
  }
}
