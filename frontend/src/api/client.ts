import axios, { type AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

const baseURL = ''

export const TOKEN_STORAGE_KEY = 'demoxv_access_token'

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY)

    if (token) {
      config.headers = config.headers ?? {}
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error: AxiosError) => Promise.reject(error),
)

export default apiClient
