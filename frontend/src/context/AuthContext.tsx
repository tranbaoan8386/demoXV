import { createContext, useEffect, useMemo, useState, type ReactNode } from 'react'

import { authApi } from '../api/auth.api'
import type { AuthResponse, LoginDTO, RegisterDTO, UserInfo, VerifyAuthResponse } from '../types'
import {
  clearAuthStorage,
  getStoredUser,
  getToken,
  removeToken,
  setStoredUser,
  setToken,
} from '../utils/storage'

export interface AuthContextValue {
  token: string | null
  user: UserInfo | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (payload: LoginDTO) => Promise<AuthResponse>
  register: (payload: RegisterDTO) => Promise<AuthResponse>
  verifyToken: () => Promise<UserInfo | null>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [token, setTokenState] = useState<string | null>(() => getToken())
  const [user, setUser] = useState<UserInfo | null>(() => getStoredUser<UserInfo>())
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    if (!token || user) {
      setIsLoading(false)
      return
    }

    void verifyToken().finally(() => {
      setIsLoading(false)
    })
  }, [])

  const syncAuthState = (nextToken: string, nextUser: UserInfo) => {
    setTokenState(nextToken)
    setUser(nextUser)
    setToken(nextToken)
    setStoredUser(nextUser)
  }

  const login = async (payload: LoginDTO) => {
    const response = await authApi.login(payload)
    const data = response.data.data

    syncAuthState(data.token, data.user)

    return response.data
  }

  const register = async (payload: RegisterDTO) => {
    const response = await authApi.register(payload)
    const data = response.data.data

    syncAuthState(data.token, data.user)

    return response.data
  }

  const verifyToken = async () => {
    const currentToken = getToken()

    if (!currentToken) {
      setTokenState(null)
      setUser(null)
      clearAuthStorage()
      return null
    }

    try {
      const response: VerifyAuthResponse = (await authApi.verify(currentToken)).data
      const nextUser = response.data.user

      setTokenState(currentToken)
      setUser(nextUser)
      setToken(currentToken)
      setStoredUser(nextUser)

      return nextUser
    } catch {
      setTokenState(null)
      setUser(null)
      removeToken()
      clearAuthStorage()
      return null
    }
  }

  const logout = () => {
    setTokenState(null)
    setUser(null)
    clearAuthStorage()
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token && user),
      isLoading,
      login,
      register,
      verifyToken,
      logout,
    }),
    [isLoading, token, user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
