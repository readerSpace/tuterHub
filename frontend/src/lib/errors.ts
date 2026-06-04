import axios from 'axios'

export function getErrorMessage(error: unknown, fallback = '処理に失敗しました。') {
  if (axios.isAxiosError(error)) {
    const payload = error.response?.data

    if (typeof payload === 'string' && payload.trim()) {
      return payload
    }

    if (payload && typeof payload === 'object') {
      const detail = (payload as Record<string, unknown>).detail
      if (typeof detail === 'string' && detail.trim()) {
        return detail
      }

      const entries = Object.entries(payload as Record<string, unknown>)
      if (entries.length > 0) {
        const firstValue = entries[0][1]
        if (Array.isArray(firstValue) && firstValue.length > 0) {
          return String(firstValue[0])
        }
        if (typeof firstValue === 'string' && firstValue.trim()) {
          return firstValue
        }
      }
    }

    if (typeof error.message === 'string' && error.message.trim()) {
      return error.message
    }
  }

  if (error instanceof Error && error.message.trim()) {
    return error.message
  }

  return fallback
}
