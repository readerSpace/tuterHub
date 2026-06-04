import type { PaginatedResponse } from '../types/common'
import type { Score } from '../types/score'
import { apiClient } from './client'

export async function listScores(params: Record<string, string | number | undefined> = {}) {
  const response = await apiClient.get<PaginatedResponse<Score>>('/api/scores/', { params })
  return response.data
}
