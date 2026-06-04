import type { LessonReportCreatePayload } from '../types/lesson'
import { apiClient } from './client'

export async function createLessonReport(payload: LessonReportCreatePayload) {
  const response = await apiClient.post('/api/reports/', payload)
  return response.data
}
