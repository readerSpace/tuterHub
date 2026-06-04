import axios, { type InternalAxiosRequestConfig } from 'axios'

const ACCESS_TOKEN_KEY = 'tutorhub.accessToken'
const REFRESH_TOKEN_KEY = 'tutorhub.refreshToken'

export const apiClient = axios.create({
  baseURL: '/',
  timeout: 30000,
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY)

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

let refreshPromise: Promise<string | null> | null = null

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    const requestUrl = String(originalRequest?.url || '')

    if (
      status !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      requestUrl.includes('/api/auth/token/')
    ) {
      throw error
    }

    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!refreshToken) {
      throw error
    }

    originalRequest._retry = true

    refreshPromise ??= apiClient
      .post('/api/auth/token/refresh/', { refresh: refreshToken })
      .then((response) => {
        const nextAccessToken = String(response.data.access || '')
        if (!nextAccessToken) {
          throw new Error('No access token returned from refresh endpoint.')
        }
        localStorage.setItem(ACCESS_TOKEN_KEY, nextAccessToken)
        return nextAccessToken
      })
      .catch(() => {
        localStorage.removeItem(ACCESS_TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        return null
      })
      .finally(() => {
        refreshPromise = null
      })

    const nextAccessToken = await refreshPromise
    if (!nextAccessToken) {
      throw error
    }

    originalRequest.headers.Authorization = `Bearer ${nextAccessToken}`
    return apiClient(originalRequest)
  },
)
