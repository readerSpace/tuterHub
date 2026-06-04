import type {
  AIGenerationLogItem,
  AIGenerationSummary,
  HomeworkSuggestionRequest,
  HomeworkSuggestionResponse,
  LessonFeedbackRequest,
  LessonFeedbackResponse,
  StudyPlanRequest,
  StudyPlanResponse,
} from '../types/ai'
import { apiClient } from './client'

export async function generateLessonFeedback(payload: LessonFeedbackRequest) {
  const response = await apiClient.post<LessonFeedbackResponse>('/ai/lesson-feedback', payload)
  return response.data
}

export async function generateHomeworkSuggestion(payload: HomeworkSuggestionRequest) {
  const response = await apiClient.post<HomeworkSuggestionResponse>('/ai/homework-suggestion', payload)
  return response.data
}

export async function generateStudyPlan(payload: StudyPlanRequest) {
  const response = await apiClient.post<StudyPlanResponse>('/ai/study-plan', payload)
  return response.data
}

export async function getAiSummary() {
  const response = await apiClient.get<AIGenerationSummary>('/ai/summary')
  return response.data
}

export async function listAiLogs(params: { studentId?: number; limit?: number } = {}) {
  const response = await apiClient.get<AIGenerationLogItem[]>('/ai/logs', {
    params: {
      student_id: params.studentId,
      limit: params.limit ?? 10,
    },
  })
  return response.data
}
