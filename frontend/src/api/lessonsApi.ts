import type { PaginatedResponse } from '../types/common'
import type { Lesson, LessonCreatePayload } from '../types/lesson'
import { apiClient } from './client'

export async function listLessons(params: Record<string, string | number | undefined> = {}) {
  const response = await apiClient.get<PaginatedResponse<Lesson>>('/api/lessons/', { params })
  return response.data
}

export async function createLesson(payload: LessonCreatePayload) {
  const response = await apiClient.post<Lesson>('/api/lessons/', payload)
  return response.data
}
