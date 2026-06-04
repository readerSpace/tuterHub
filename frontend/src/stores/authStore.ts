import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { fetchCurrentUser, requestToken } from '../api/authApi'
import type { CurrentUser, LoginCredentials } from '../types/auth'

const ACCESS_TOKEN_KEY = 'tutorhub.accessToken'
const REFRESH_TOKEN_KEY = 'tutorhub.refreshToken'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem(ACCESS_TOKEN_KEY) || '')
  const refreshToken = ref(localStorage.getItem(REFRESH_TOKEN_KEY) || '')
  const user = ref<CurrentUser | null>(null)
  const busy = ref(false)
  const initialized = ref(false)

  const isAuthenticated = computed(() => Boolean(accessToken.value))
  const displayName = computed(() => {
    if (!user.value) {
      return 'Guest'
    }

    return [user.value.last_name, user.value.first_name].filter(Boolean).join(' ') || user.value.username
  })

  function setTokens(tokens: { access: string; refresh?: string }) {
    accessToken.value = tokens.access
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access)

    if (tokens.refresh) {
      refreshToken.value = tokens.refresh
      localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh)
    }
  }

  function clearSession() {
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  }

  function hydrate() {
    accessToken.value = localStorage.getItem(ACCESS_TOKEN_KEY) || ''
    refreshToken.value = localStorage.getItem(REFRESH_TOKEN_KEY) || ''
  }

  async function loadCurrentUser() {
    const currentUser = await fetchCurrentUser()
    user.value = currentUser
    return currentUser
  }

  async function initialize() {
    if (initialized.value) {
      return
    }

    hydrate()
    if (!accessToken.value) {
      initialized.value = true
      return
    }

    try {
      await loadCurrentUser()
    } catch {
      clearSession()
    } finally {
      initialized.value = true
    }
  }

  async function login(credentials: LoginCredentials) {
    busy.value = true
    try {
      const tokens = await requestToken(credentials)
      setTokens(tokens)
      await loadCurrentUser()
    } finally {
      busy.value = false
    }
  }

  function logout() {
    clearSession()
  }

  return {
    accessToken,
    refreshToken,
    user,
    busy,
    initialized,
    isAuthenticated,
    displayName,
    setTokens,
    clearSession,
    hydrate,
    initialize,
    loadCurrentUser,
    login,
    logout,
  }
})
