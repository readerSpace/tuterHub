export type LessonStatus = 'scheduled' | 'completed' | 'absent' | 'rescheduled'
export type LessonFormat = 'in_person' | 'online'

export type Lesson = {
  id: number
  student: number
  student_name: string
  teacher: number
  teacher_name: string
  subject: string
  start_time: string
  end_time: string
  lesson_format: LessonFormat
  status: LessonStatus
  created_at: string
  updated_at: string
}

export type LessonCreatePayload = {
  student: number
  subject: string
  start_time: string
  end_time: string
  lesson_format: LessonFormat
  status: LessonStatus
}

export type LessonReportCreatePayload = {
  lesson: number
  content: string
  understanding_level: number
  homework: string
  next_plan: string
  parent_comment: string
}

export type LessonFormState = {
  student: string
  subject: string
  start_time: string
  end_time: string
  lesson_format: LessonFormat
  status: LessonStatus
  content: string
  understanding_level: number
  homework: string
  next_plan: string
  teacher_note: string
  parent_comment: string
}

export function emptyLessonForm(): LessonFormState {
  return {
    student: '',
    subject: '',
    start_time: '',
    end_time: '',
    lesson_format: 'in_person',
    status: 'scheduled',
    content: '',
    understanding_level: 3,
    homework: '',
    next_plan: '',
    teacher_note: '',
    parent_comment: '',
  }
}
