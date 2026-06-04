<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import { listAiLogs } from '../api/aiApi'
import { listAssignments } from '../api/assignmentsApi'
import { listLessons } from '../api/lessonsApi'
import { listScores } from '../api/scoresApi'
import { getStudent } from '../api/studentsApi'
import AppLayout from '../components/AppLayout.vue'
import { getErrorMessage } from '../lib/errors'
import type { AIGenerationLogItem } from '../types/ai'
import type { Assignment } from '../types/assignment'
import type { Lesson } from '../types/lesson'
import type { Score } from '../types/score'
import type { Student } from '../types/student'

const route = useRoute()

const student = ref<Student | null>(null)
const lessons = ref<Lesson[]>([])
const assignments = ref<Assignment[]>([])
const scores = ref<Score[]>([])
const aiLogs = ref<AIGenerationLogItem[]>([])
const loading = ref(true)
const errorMessage = ref('')

const studentId = computed(() => Number(route.params.id))
const focusTags = computed(() => student.value?.weak_subjects.split(',').map((item) => item.trim()).filter(Boolean) || [])

const dateFormatter = new Intl.DateTimeFormat('ja-JP', { year: 'numeric', month: 'numeric', day: 'numeric' })
const dateTimeFormatter = new Intl.DateTimeFormat('ja-JP', {
  month: 'numeric',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

function featureLabel(featureType: string) {
  if (featureType === 'lesson_feedback') {
    return '保護者コメント'
  }
  if (featureType === 'homework_suggestion') {
    return '宿題提案'
  }
  if (featureType === 'study_plan') {
    return '学習計画'
  }
  return featureType
}

function formatDate(value: string) {
  return dateFormatter.format(new Date(value))
}

function formatDateTime(value: string) {
  return dateTimeFormatter.format(new Date(value))
}

async function loadStudentDetail() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [studentResponse, lessonsResponse, assignmentsResponse, scoresResponse, aiLogsResponse] = await Promise.all([
      getStudent(studentId.value),
      listLessons({ student: studentId.value, ordering: '-start_time' }),
      listAssignments({ student: studentId.value }),
      listScores({ student: studentId.value, ordering: '-exam_date' }),
      listAiLogs({ studentId: studentId.value, limit: 10 }),
    ])

    student.value = studentResponse
    lessons.value = lessonsResponse.results
    assignments.value = assignmentsResponse.results
    scores.value = scoresResponse.results
    aiLogs.value = aiLogsResponse
  } catch (error) {
    errorMessage.value = getErrorMessage(error, '生徒詳細の取得に失敗しました。')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadStudentDetail()
})

watch(studentId, () => {
  void loadStudentDetail()
})
</script>

<template>
  <AppLayout>
    <div class="page-stack">
      <section v-if="student" class="hero-card">
        <div class="hero-grid">
          <div>
            <p class="eyebrow">Student Detail</p>
            <h2 class="hero-title">{{ student.full_name }}</h2>
            <p class="hero-copy">
              {{ student.school || '学校未設定' }} / {{ student.grade }} / {{ student.target_school || '志望校未設定' }}
            </p>
            <div class="hero-actions">
              <RouterLink
                class="outline-button"
                :to="{ path: '/studio/ai/lesson-feedback', query: { studentName: student.full_name } }"
              >
                この生徒で AI コメント生成
              </RouterLink>
              <RouterLink class="ghost-link" to="/lessons/new">授業記録を追加</RouterLink>
            </div>
          </div>

          <div class="panel-surface">
            <div class="section-header compact">
              <div>
                <p class="eyebrow">Profile</p>
                <h3>基本情報</h3>
              </div>
            </div>
            <div class="data-list">
              <div class="data-item">
                <span class="muted">担当講師</span>
                <strong>{{ student.teacher_name || '未設定' }}</strong>
              </div>
              <div class="data-item">
                <span class="muted">保護者</span>
                <strong>{{ student.parent_name || '未設定' }}</strong>
              </div>
              <div class="data-item">
                <span class="muted">連絡先</span>
                <strong>{{ student.guardian_contact || '未設定' }}</strong>
              </div>
            </div>

            <div v-if="focusTags.length" class="hero-actions">
              <span v-for="tag in focusTags" :key="tag" class="pill neutral">{{ tag }}</span>
            </div>
          </div>
        </div>
      </section>

      <p v-if="errorMessage" class="helper-text warning-text">{{ errorMessage }}</p>

      <div class="metric-grid">
        <article class="metric-card">
          <p class="metric-label">授業履歴</p>
          <p class="metric-value">{{ lessons.length }}</p>
          <p class="metric-note">取得した授業レコード数</p>
        </article>
        <article class="metric-card">
          <p class="metric-label">課題</p>
          <p class="metric-value">{{ assignments.length }}</p>
          <p class="metric-note">この生徒に紐づく課題</p>
        </article>
        <article class="metric-card">
          <p class="metric-label">成績</p>
          <p class="metric-value">{{ scores.length }}</p>
          <p class="metric-note">直近の成績ログ</p>
        </article>
        <article class="metric-card">
          <p class="metric-label">AI 履歴</p>
          <p class="metric-value">{{ aiLogs.length }}</p>
          <p class="metric-note">FastAPI の AI generation log</p>
        </article>
      </div>

      <div class="split-grid">
        <div class="stack-grid">
          <section class="panel-surface">
            <div class="section-header">
              <div>
                <p class="eyebrow">Lessons</p>
                <h3>授業履歴</h3>
              </div>
            </div>

            <div v-if="loading" class="empty-state">
              <h3>読み込み中</h3>
              <p class="section-note">授業履歴を取得しています。</p>
            </div>
            <div v-else-if="lessons.length" class="card-list">
              <article v-for="lesson in lessons" :key="lesson.id" class="list-card">
                <div class="card-row">
                  <div>
                    <p class="kicker">{{ formatDateTime(lesson.start_time) }}</p>
                    <h3>{{ lesson.subject }}</h3>
                    <p class="list-meta">{{ lesson.teacher_name }}</p>
                  </div>
                  <span class="pill" :class="lesson.status === 'completed' ? '' : 'warm'">{{ lesson.status }}</span>
                </div>
              </article>
            </div>
            <div v-else class="empty-state">
              <h3>授業履歴がありません</h3>
              <p class="section-note">まだこの生徒の授業は登録されていません。</p>
            </div>
          </section>

          <section class="panel-surface">
            <div class="section-header">
              <div>
                <p class="eyebrow">Assignments</p>
                <h3>課題</h3>
              </div>
            </div>

            <div v-if="assignments.length" class="card-list">
              <article v-for="assignment in assignments" :key="assignment.id" class="list-card">
                <div class="card-row">
                  <div>
                    <p class="kicker">期限: {{ formatDate(assignment.due_date) }}</p>
                    <h3>{{ assignment.title }}</h3>
                    <p class="list-meta">{{ assignment.description || '説明なし' }}</p>
                  </div>
                  <span class="pill" :class="assignment.status === 'pending' ? 'warm' : ''">{{ assignment.status }}</span>
                </div>
              </article>
            </div>
            <div v-else class="empty-state">
              <h3>課題はまだありません</h3>
              <p class="section-note">必要に応じて Django 側の assignment API から追加してください。</p>
            </div>
          </section>
        </div>

        <div class="stack-grid">
          <section class="panel-surface">
            <div class="section-header">
              <div>
                <p class="eyebrow">Scores</p>
                <h3>成績推移</h3>
              </div>
            </div>

            <div v-if="scores.length" class="card-list">
              <article v-for="score in scores" :key="score.id" class="list-card">
                <div class="card-row">
                  <div>
                    <p class="kicker">{{ formatDate(score.exam_date) }} ・ {{ score.exam_type }}</p>
                    <h3>{{ score.subject }}</h3>
                    <p class="list-meta">{{ score.score }} / {{ score.max_score }}</p>
                  </div>
                  <span class="pill neutral">{{ score.percentage }}%</span>
                </div>
              </article>
            </div>
            <div v-else class="empty-state">
              <h3>成績データがありません</h3>
              <p class="section-note">Score API に記録されるとここへ表示されます。</p>
            </div>
          </section>

          <section class="panel-surface">
            <div class="section-header">
              <div>
                <p class="eyebrow">AI History</p>
                <h3>AI 生成履歴</h3>
              </div>
            </div>

            <div v-if="aiLogs.length" class="timeline">
              <article v-for="log in aiLogs" :key="log.id" class="log-entry">
                <div class="card-row">
                  <div>
                    <p class="kicker">{{ formatDateTime(log.created_at) }}</p>
                    <h3>{{ featureLabel(log.feature_type) }}</h3>
                  </div>
                  <span class="pill neutral">log #{{ log.id }}</span>
                </div>
                <p class="log-body">{{ log.response }}</p>
              </article>
            </div>
            <div v-else class="empty-state">
              <h3>AI 履歴はまだありません</h3>
              <p class="section-note">AI 画面から生成するとここに蓄積されます。</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
