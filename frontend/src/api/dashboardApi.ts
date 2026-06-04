import type { DashboardSummary } from '../types/dashboard'
import { apiClient } from './client'

export async function getDashboardSummary() {
  const response = await apiClient.get<DashboardSummary>('/api/dashboard-summary/')
  return response.data
}
