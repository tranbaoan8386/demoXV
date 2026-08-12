const TOKEN_KEY = 'demoxv_access_token'
const USER_KEY = 'demoxv_user_info'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export function getStoredUser<T>(): T | null {
  const rawValue = localStorage.getItem(USER_KEY)

  if (!rawValue) {
    return null
  }

  try {
    return JSON.parse(rawValue) as T
  } catch {
    return null
  }
}

export function setStoredUser<T>(user: T): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function removeStoredUser(): void {
  localStorage.removeItem(USER_KEY)
}

export function clearAuthStorage(): void {
  removeToken()
  removeStoredUser()
}
