export type Student = {
  id: number
  user: number | null
  user_name: string
  parent: number | null
  parent_name: string
  teacher: number | null
  teacher_name: string
  full_name: string
  grade: string
  school: string
  target_school: string
  weak_subjects: string
  guardian_contact: string
  notes: string
  created_at: string
  updated_at: string
}

export type StudentCreatePayload = {
  full_name: string
  grade: string
  school: string
  target_school: string
  weak_subjects: string
  teacher?: number | null
  parent?: number | null
  guardian_contact: string
  notes: string
}

export type StudentFormState = {
  full_name: string
  grade: string
  school: string
  target_school: string
  weak_subjects: string
  teacher: string
  parent: string
  guardian_contact: string
  notes: string
}

export function emptyStudentForm(): StudentFormState {
  return {
    full_name: '',
    grade: '',
    school: '',
    target_school: '',
    weak_subjects: '',
    teacher: '',
    parent: '',
    guardian_contact: '',
    notes: '',
  }
}
