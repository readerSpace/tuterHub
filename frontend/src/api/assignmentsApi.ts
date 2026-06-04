import type { PaginatedResponse } from '../types/common'
import type { Assignment } from '../types/assignment'
import { apiClient } from './client'

export async function listAssignments(params: Record<string, string | number | undefined> = {}) {
  const response = await apiClient.get<PaginatedResponse<Assignment>>('/api/assignments/', { params })
  return response.data
}
