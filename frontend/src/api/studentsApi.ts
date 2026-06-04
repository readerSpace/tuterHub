import type { PaginatedResponse } from '../types/common'
import type { Student, StudentCreatePayload } from '../types/student'
import { apiClient } from './client'

export async function listStudents(params: Record<string, string | number | undefined> = {}) {
  const response = await apiClient.get<PaginatedResponse<Student>>('/api/students/', { params })
  return response.data
}

export async function getStudent(studentId: number) {
  const response = await apiClient.get<Student>(`/api/students/${studentId}/`)
  return response.data
}

export async function createStudent(payload: StudentCreatePayload) {
  const response = await apiClient.post<Student>('/api/students/', payload)
  return response.data
}
