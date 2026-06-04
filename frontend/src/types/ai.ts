export type LessonFeedbackRequest = {
  student_name: string
  subject: string
  lesson_content: string
  understanding_level: number
  teacher_note: string
}

export type LessonFeedbackResponse = {
  feedback: string
}

export type HomeworkSuggestionRequest = {
  student_name: string
  grade: string
  subject: string
  weak_points: string[]
  available_minutes: number
}

export type HomeworkSuggestionResponse = {
  homework: string[]
}

export type ScoreInput = {
  subject: string
  score: number
  max_score: number
}

export type StudyPlanRequest = {
  student_name: string
  grade: string
  target_school: string
  scores: ScoreInput[]
  weeks: number
}

export type StudyPlanItem = {
  week: number
  task: string
}

export type StudyPlanResponse = {
  plan: StudyPlanItem[]
}

export type AIGenerationSummary = {
  total_generations: number
  lesson_feedback_count: number
  homework_suggestion_count: number
  study_plan_count: number
}

export type AIGenerationLogItem = {
  id: number
  student_id: number | null
  feature_type: string
  prompt: string
  response: string
  created_at: string
}
