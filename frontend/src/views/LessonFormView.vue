<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { generateLessonFeedback } from '../api/aiApi'
import { createLesson } from '../api/lessonsApi'
import { createLessonReport } from '../api/reportsApi'
import { listStudents } from '../api/studentsApi'
import AppLayout from '../components/AppLayout.vue'
import AiResultCard from '../components/AiResultCard.vue'
import LessonForm from '../components/LessonForm.vue'
import { getErrorMessage } from '../lib/errors'
import type { SelectOption } from '../types/common'
import { emptyLessonForm, type LessonFormState } from '../types/lesson'
import type { Student } from '../types/student'

const students = ref<Student[]>([])
const studentsTotal = ref(0)
const lessonForm = ref<LessonFormState>(emptyLessonForm())
const saving = ref(false)
const generating = ref(false)
const loadingStudents = ref(true)
const errorMessage = ref('')
const successMessage = ref('')

const studentOptions = computed<SelectOption[]>(() =>
  students.value.map((student) => ({
    label: `${student.full_name} (${student.grade})`,
    value: student.id,
  })),
)

const selectedStudent = computed(() => students.value.find((student) => String(student.id) === lessonForm.value.student))
const generatedComment = computed(() => lessonForm.value.parent_comment.trim())
const studentOptionsNote = computed(() =>
  studentsTotal.value > students.value.length
    ? `候補は最初の ${students.value.length} 件を表示しています。`
    : '表示中の生徒候補は全件です。',
)

function toIsoString(localDateTime: string) {
  return new Date(localDateTime).toISOString()
}

function buildNextPlanPayload() {
  const sections = []
  if (lessonForm.value.next_plan.trim()) {
    sections.push(lessonForm.value.next_plan.trim())
  }
  if (lessonForm.value.teacher_note.trim()) {
    sections.push(`講師メモ: ${lessonForm.value.teacher_note.trim()}`)
  }
  return sections.join('\n')
}

async function loadStudentOptions() {
  loadingStudents.value = true
  errorMessage.value = ''

  try {
    const response = await listStudents({ ordering: 'full_name' })
    students.value = response.results
    studentsTotal.value = response.count
  } catch (error) {
    errorMessage.value = getErrorMessage(error, '生徒候補の取得に失敗しました。')
  } finally {
    loadingStudents.value = false
  }
}

async function handleGenerateFeedback() {
  generating.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    if (!selectedStudent.value) {
      throw new Error('生徒を選択してください。')
    }

    const response = await generateLessonFeedback({
      student_name: selectedStudent.value.full_name,
      subject: lessonForm.value.subject,
      lesson_content: lessonForm.value.content,
      understanding_level: lessonForm.value.understanding_level,
      teacher_note: lessonForm.value.teacher_note || lessonForm.value.next_plan || '補足メモなし',
    })
    lessonForm.value = {
      ...lessonForm.value,
      parent_comment: response.feedback,
    }
    successMessage.value = 'AI コメントを生成しました。保存前に内容を確認してください。'
  } catch (error) {
    errorMessage.value = getErrorMessage(error, 'AI コメント生成に失敗しました。')
  } finally {
    generating.value = false
  }
}

async function handleSaveLesson() {
  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    if (!lessonForm.value.student) {
      throw new Error('生徒を選択してください。')
    }

    const lesson = await createLesson({
      student: Number(lessonForm.value.student),
      subject: lessonForm.value.subject,
      start_time: toIsoString(lessonForm.value.start_time),
      end_time: toIsoString(lessonForm.value.end_time),
      lesson_format: lessonForm.value.lesson_format,
      status: lessonForm.value.status,
    })

    await createLessonReport({
      lesson: lesson.id,
      content: lessonForm.value.content,
      understanding_level: lessonForm.value.understanding_level,
      homework: lessonForm.value.homework,
      next_plan: buildNextPlanPayload(),
      parent_comment: lessonForm.value.parent_comment,
    })

    successMessage.value = '授業記録とレポートを保存しました。'
    lessonForm.value = emptyLessonForm()
    await loadStudentOptions()
  } catch (error) {
    errorMessage.value = getErrorMessage(error, '授業記録の保存に失敗しました。')
  } finally {
    saving.value = false
  }
}

function handleLessonFormUpdate(value: LessonFormState) {
  lessonForm.value = value
}

onMounted(() => {
  void loadStudentOptions()
})
</script>

<template>
  <AppLayout>
    <div class="page-stack">
      <section class="hero-card">
        <div class="hero-grid">
          <div>
            <p class="eyebrow">Lesson Studio</p>
            <h2 class="hero-title">授業記録入力</h2>
            <p class="hero-copy">
              Lesson と LessonReport をまとめて保存し、同じ画面で保護者コメント生成まで完結できます。
            </p>
          </div>

          <div class="panel-surface">
            <div class="section-header compact">
              <div>
                <p class="eyebrow">Student Source</p>
                <h3>生徒候補</h3>
              </div>
            </div>
            <p class="section-note">{{ studentOptionsNote }}</p>
            <p v-if="loadingStudents" class="helper-text">候補を読み込み中です。</p>
          </div>
        </div>
      </section>

      <p v-if="errorMessage" class="helper-text warning-text">{{ errorMessage }}</p>
      <p v-if="successMessage" class="helper-text">{{ successMessage }}</p>

      <div class="split-grid">
        <LessonForm
          :model-value="lessonForm"
          :student-options="studentOptions"
          :saving="saving"
          :generating="generating"
          @update:model-value="handleLessonFormUpdate"
          @generate-feedback="handleGenerateFeedback"
          @submit="handleSaveLesson"
        />

        <div class="stack-grid">
          <AiResultCard
            v-if="generatedComment"
            title="保護者コメントの下書き"
            description="保存前に文面を最終確認できます。"
            :text="generatedComment"
            tone="accent"
          />
          <section v-else class="empty-state">
            <h3>AI コメント未生成</h3>
            <p class="section-note">「AIで保護者向けコメント生成」を押すとここに結果を表示します。</p>
          </section>

          <section class="panel-surface">
            <div class="section-header compact">
              <div>
                <p class="eyebrow">Save Flow</p>
                <h3>保存される内容</h3>
              </div>
            </div>
            <div class="data-list">
              <div class="data-item">
                <span class="muted">Lesson</span>
                <strong>{{ lessonForm.subject || '科目未入力' }}</strong>
              </div>
              <div class="data-item">
                <span class="muted">理解度</span>
                <strong>{{ lessonForm.understanding_level }}/5</strong>
              </div>
              <div class="data-item">
                <span class="muted">選択中の生徒</span>
                <strong>{{ selectedStudent?.full_name || '未選択' }}</strong>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
