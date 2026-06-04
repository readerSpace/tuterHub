<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { createStudent, listStudents } from '../api/studentsApi'
import AppLayout from '../components/AppLayout.vue'
import StudentForm from '../components/StudentForm.vue'
import { getErrorMessage } from '../lib/errors'
import { useAuthStore } from '../stores/authStore'
import { emptyStudentForm, type Student, type StudentCreatePayload, type StudentFormState } from '../types/student'

const authStore = useAuthStore()
const router = useRouter()

const students = ref<Student[]>([])
const studentForm = ref<StudentFormState>(emptyStudentForm())
const loading = ref(true)
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const totalCount = ref(0)
const currentPage = ref(1)
const hasNextPage = ref(false)
const hasPreviousPage = ref(false)
const search = ref('')
const grade = ref('')
const ACCESS_TOKEN_KEY = 'tutorhub.accessToken'

const teacherLocked = computed(() => authStore.user?.role === 'teacher')
const paginationSummary = computed(() => {
  if (!students.value.length) {
    return '0 / 0'
  }

  const from = (currentPage.value - 1) * 10 + 1
  const to = from + students.value.length - 1
  return `${from}-${to} / ${totalCount.value}`
})

function buildEmptyStudentForm(): StudentFormState {
  return {
    ...emptyStudentForm(),
    teacher: '',
  }
}

function getCurrentUserIdFromToken() {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)
  if (!accessToken) {
    return null
  }

  try {
    const [, payload] = accessToken.split('.')
    if (!payload) {
      return null
    }

    const normalizedPayload = payload.replace(/-/g, '+').replace(/_/g, '/')
    const claims = JSON.parse(atob(normalizedPayload)) as { user_id?: number | string }
    const userId = Number(claims.user_id)
    return Number.isFinite(userId) ? userId : null
  } catch {
    return null
  }
}

async function loadStudents(page = 1) {
  loading.value = true
  errorMessage.value = ''

  try {
    await authStore.initialize()
    const currentUserId = getCurrentUserIdFromToken()

    if (!studentForm.value.teacher && currentUserId) {
      studentForm.value = {
        ...buildEmptyStudentForm(),
        teacher: String(currentUserId),
      }
    }

    const response = await listStudents({
      page,
      search: search.value || undefined,
      grade: grade.value || undefined,
      ordering: 'full_name',
    })

    students.value = response.results
    totalCount.value = response.count
    currentPage.value = page
    hasNextPage.value = Boolean(response.next)
    hasPreviousPage.value = Boolean(response.previous)
  } catch (error) {
    errorMessage.value = getErrorMessage(error, '生徒一覧の取得に失敗しました。')
  } finally {
    loading.value = false
  }
}

async function handleCreateStudent() {
  submitting.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await authStore.initialize()
    const currentUserId = getCurrentUserIdFromToken()

    const payload: StudentCreatePayload = {
      full_name: studentForm.value.full_name,
      grade: studentForm.value.grade,
      school: studentForm.value.school,
      target_school: studentForm.value.target_school,
      weak_subjects: studentForm.value.weak_subjects,
      guardian_contact: studentForm.value.guardian_contact,
      notes: studentForm.value.notes,
    }

    if (studentForm.value.teacher.trim()) {
      payload.teacher = Number(studentForm.value.teacher)
    } else if (currentUserId) {
      payload.teacher = currentUserId
    }
    if (studentForm.value.parent.trim()) {
      payload.parent = Number(studentForm.value.parent)
    }

    await createStudent(payload)
    successMessage.value = '生徒を登録しました。'
    studentForm.value = {
      ...buildEmptyStudentForm(),
      teacher: currentUserId ? String(currentUserId) : '',
    }
    await loadStudents(1)
  } catch (error) {
    errorMessage.value = getErrorMessage(error, '生徒登録に失敗しました。')
  } finally {
    submitting.value = false
  }
}

function handleStudentFormUpdate(value: StudentFormState) {
  studentForm.value = value
}

function openStudent(studentId: number) {
  void router.push(`/students/${studentId}`)
}

onMounted(() => {
  void loadStudents()
})
</script>

<template>
  <AppLayout>
    <div class="page-stack">
      <section class="hero-card">
        <div class="hero-grid">
          <div>
            <p class="eyebrow">Students</p>
            <h2 class="hero-title">生徒台帳と検索</h2>
            <p class="hero-copy">講師が担当する生徒を検索し、そのまま詳細画面や授業記録入力へ接続できます。</p>
          </div>

          <div class="panel-surface toolbar">
            <div class="section-header compact">
              <div>
                <p class="eyebrow">Search</p>
                <h3>一覧フィルター</h3>
              </div>
              <p class="muted">{{ paginationSummary }}</p>
            </div>

            <form class="form-grid two-columns" @submit.prevent="loadStudents(1)">
              <label class="field field-wide">
                <span>キーワード</span>
                <input v-model="search" placeholder="氏名、学校名、志望校、弱点で検索" />
              </label>
              <label class="field">
                <span>学年</span>
                <input v-model="grade" placeholder="中3 / 高1" />
              </label>
              <div class="page-actions">
                <button class="quiet-button" type="button" @click="search = ''; grade = ''; loadStudents(1)">
                  クリア
                </button>
                <button class="outline-button" type="submit">検索</button>
              </div>
            </form>
          </div>
        </div>
      </section>

      <p v-if="errorMessage" class="helper-text warning-text">{{ errorMessage }}</p>
      <p v-if="successMessage" class="helper-text">{{ successMessage }}</p>

      <div class="split-grid">
        <section class="panel-surface">
          <div class="section-header">
            <div>
              <p class="eyebrow">Directory</p>
              <h3>生徒一覧</h3>
            </div>
            <span class="pill neutral">{{ totalCount }} students</span>
          </div>

          <div v-if="loading" class="empty-state">
            <h3>読み込み中</h3>
            <p class="section-note">生徒データを読み込んでいます。</p>
          </div>
          <div v-else-if="students.length" class="card-list">
            <article v-for="student in students" :key="student.id" class="list-card" @click="openStudent(student.id)">
              <div class="card-row">
                <div>
                  <p class="kicker">{{ student.grade }} ・ {{ student.teacher_name || '担当未設定' }}</p>
                  <h3>{{ student.full_name }}</h3>
                  <p class="list-meta">
                    {{ student.school || '学校未設定' }} / {{ student.target_school || '志望校未設定' }}
                  </p>
                </div>
                <span class="pill">{{ student.weak_subjects || '弱点未設定' }}</span>
              </div>
            </article>
          </div>
          <div v-else class="empty-state">
            <h3>該当する生徒がいません</h3>
            <p class="section-note">検索条件を変えるか、新しい生徒を登録してください。</p>
          </div>

          <div class="page-actions">
            <button class="quiet-button" type="button" :disabled="!hasPreviousPage || loading" @click="loadStudents(currentPage - 1)">
              前のページ
            </button>
            <button class="outline-button" type="button" :disabled="!hasNextPage || loading" @click="loadStudents(currentPage + 1)">
              次のページ
            </button>
          </div>
        </section>

        <StudentForm
          :model-value="studentForm"
          :submitting="submitting"
          :teacher-locked="teacherLocked"
          @update:model-value="handleStudentFormUpdate"
          @submit="handleCreateStudent"
        />
      </div>
    </div>
  </AppLayout>
</template>
