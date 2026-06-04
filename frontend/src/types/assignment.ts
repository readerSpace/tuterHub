export type Assignment = {
  id: number
  student: number
  student_name: string
  teacher: number
  teacher_name: string
  title: string
  description: string
  due_date: string
  status: 'pending' | 'submitted' | 'reviewed'
  teacher_comment: string
  created_at: string
  updated_at: string
}
