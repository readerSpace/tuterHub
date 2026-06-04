import type { CurrentUser, LoginCredentials, TokenPair } from '../types/auth'
import { apiClient } from './client'

export async function requestToken(credentials: LoginCredentials) {
  const response = await apiClient.post<TokenPair>('/api/auth/token/', credentials)
  return response.data
}

export async function fetchCurrentUser() {
  const response = await apiClient.get<CurrentUser>('/api/auth/me/')
  return response.data
}
