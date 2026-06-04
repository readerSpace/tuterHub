<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { getAiSummary } from '../api/aiApi'
import { getDashboardSummary } from '../api/dashboardApi'
import { listLessons } from '../api/lessonsApi'
import { listStudents } from '../api/studentsApi'
import AppLayout from '../components/AppLayout.vue'
import { getErrorMessage } from '../lib/errors'
import { useAuthStore } from '../stores/authStore'
import type { AIGenerationSummary } from '../types/ai'
import type { DashboardSummary } from '../types/dashboard'
import type { Lesson } from '../types/lesson'
import type { Student } from '../types/student'

const authStore = useAuthStore()

const dashboardSummary = ref<DashboardSummary>({
  students_count: 0,
  current_month_lessons_count: 0,
  pending_assignments_count: 0,
})
const aiSummary = ref<AIGenerationSummary>({
  total_generations: 0,
  lesson_feedback_count: 0,
  homework_suggestion_count: 0,
  study_plan_count: 0,
})
const recentStudents = ref<Student[]>([])
const recentLessons = ref<Lesson[]>([])
const loading = ref(true)
const errorMessage = ref('')

const dateTimeFormatter = new Intl.DateTimeFormat('ja-JP', {
  month: 'numeric',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

const metrics = computed(() => [
  {
    label: '登録生徒数',
    value: dashboardSummary.value.students_count,
    note: '担当範囲に見えている生徒数です。',
  },
  {
    label: '今月の授業数',
    value: dashboardSummary.value.current_month_lessons_count,
    note: '当月開始日の授業レコードを集計しています。',
  },
  {
    label: '未提出課題数',
    value: dashboardSummary.value.pending_assignments_count,
    note: 'ステータスが pending の課題数です。',
  },
  {
    label: 'AI生成回数',
    value: aiSummary.value.total_generations,
    note: 'FastAPI 側の AI generation log を参照しています。',
  },
])

function formatDateTime(value: string) {
  return dateTimeFormatter.format(new Date(value))
}

async function loadDashboard() {
  loading.value = true
  errorMessage.value = ''

  try {
    await authStore.initialize()
    const [dashboard, ai, students, lessons] = await Promise.all([
      getDashboardSummary(),
      getAiSummary(),
      listStudents({ ordering: '-created_at' }),
      listLessons({ ordering: '-start_time' }),
    ])

    dashboardSummary.value = dashboard
    aiSummary.value = ai
    recentStudents.value = students.results.slice(0, 4)
    recentLessons.value = lessons.results.slice(0, 5)
  } catch (error) {
    errorMessage.value = getErrorMessage(error, 'ダッシュボードの読み込みに失敗しました。')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadDashboard()
})
</script>

<template>
  <AppLayout>
    <div class="page-stack">
      <section class="hero-card">
        <div class="hero-grid">
          <div>
            <p class="eyebrow">Dashboard</p>
            <h2 class="hero-title">{{ authStore.displayName }} さんの学習支援ダッシュボード</h2>
            <p class="hero-copy">
              Django 側の授業管理と FastAPI 側の AI 補助機能を、今日の運用単位でひとつに集約しています。
            </p>
            <div class="hero-actions">
              <RouterLink class="outline-button" to="/lessons/new">授業記録を追加</RouterLink>
              <RouterLink class="ghost-link" to="/studio/ai/lesson-feedback">AI コメント生成</RouterLink>
            </div>
          </div>

          <div class="panel-surface">
            <div class="section-header compact">
              <div>
                <p class="eyebrow">AI Breakdown</p>
                <h3>生成ログの内訳</h3>
              </div>
            </div>
            <div class="mini-stat-grid">
              <article class="mini-stat">
                <span class="muted">保護者コメント</span>
                <strong>{{ aiSummary.lesson_feedback_count }}</strong>
              </article>
              <article class="mini-stat">
                <span class="muted">宿題提案</span>
                <strong>{{ aiSummary.homework_suggestion_count }}</strong>
              </article>
              <article class="mini-stat">
                <span class="muted">学習計画</span>
                <strong>{{ aiSummary.study_plan_count }}</strong>
              </article>
              <article class="mini-stat">
                <span class="muted">ログイン中ロール</span>
                <strong>{{ authStore.user?.role || 'unknown' }}</strong>
              </article>
            </div>
          </div>
        </div>
      </section>

      <div class="metric-grid">
        <article v-for="metric in metrics" :key="metric.label" class="metric-card">
          <p class="metric-label">{{ metric.label }}</p>
          <p class="metric-value">{{ metric.value }}</p>
          <p class="metric-note">{{ metric.note }}</p>
        </article>
      </div>

      <p v-if="errorMessage" class="helper-text warning-text">{{ errorMessage }}</p>

      <div class="split-grid">
        <section class="panel-surface">
          <div class="section-header">
            <div>
              <p class="eyebrow">Students</p>
              <h3>最近追加された生徒</h3>
            </div>
            <RouterLink class="ghost-link" to="/students">一覧を開く</RouterLink>
          </div>

          <div v-if="loading" class="empty-state">
            <h3>読み込み中</h3>
            <p class="section-note">生徒データを取得しています。</p>
          </div>
          <div v-else-if="recentStudents.length" class="card-list">
            <RouterLink
              v-for="student in recentStudents"
              :key="student.id"
              class="list-card"
              :to="`/students/${student.id}`"
            >
              <div class="card-row">
                <div>
                  <p class="kicker">{{ student.grade }} ・ {{ student.teacher_name || '担当未設定' }}</p>
                  <h3>{{ student.full_name }}</h3>
                  <p class="list-meta">{{ student.target_school || student.school || '進路情報未設定' }}</p>
                </div>
                <span class="pill neutral">{{ student.weak_subjects || '基礎管理' }}</span>
              </div>
            </RouterLink>
          </div>
          <div v-else class="empty-state">
            <h3>生徒データがありません</h3>
            <p class="section-note">まずは生徒登録から始めてください。</p>
          </div>
        </section>

        <div class="stack-grid">
          <section class="panel-surface">
            <div class="section-header">
              <div>
                <p class="eyebrow">Lessons</p>
                <h3>最近の授業</h3>
              </div>
              <RouterLink class="ghost-link" to="/lessons/new">新規入力</RouterLink>
            </div>

            <div v-if="loading" class="empty-state">
              <h3>読み込み中</h3>
              <p class="section-note">授業レコードを取得しています。</p>
            </div>
            <div v-else-if="recentLessons.length" class="compact-list">
              <article v-for="lesson in recentLessons" :key="lesson.id" class="list-card">
                <div class="card-row">
                  <div>
                    <p class="kicker">{{ formatDateTime(lesson.start_time) }}</p>
                    <h3>{{ lesson.student_name }}</h3>
                    <p class="list-meta">{{ lesson.subject }} ・ {{ lesson.teacher_name }}</p>
                  </div>
                  <span class="pill" :class="lesson.status === 'completed' ? '' : 'warm'">{{ lesson.status }}</span>
                </div>
              </article>
            </div>
            <div v-else class="empty-state">
              <h3>授業データがありません</h3>
              <p class="section-note">授業記録を追加するとここに表示されます。</p>
            </div>
          </section>

          <section class="panel-surface">
            <div class="section-header compact">
              <div>
                <p class="eyebrow">Quick Tools</p>
                <h3>AI ワークフローへ移動</h3>
              </div>
              <p class="muted">日々の授業フローに近い順で並べています。</p>
            </div>

            <div class="card-list">
              <RouterLink class="list-card" to="/studio/ai/lesson-feedback">
                <p class="kicker">保護者連絡</p>
                <h3>AI コメント生成</h3>
                <p class="list-meta">授業内容から保護者向けコメントを作成します。</p>
              </RouterLink>
              <RouterLink class="list-card" to="/studio/ai/homework-suggestion">
                <p class="kicker">宿題作成</p>
                <h3>宿題提案</h3>
                <p class="list-meta">苦手分野と時間から課題案を出します。</p>
              </RouterLink>
              <RouterLink class="list-card" to="/studio/ai/study-plan">
                <p class="kicker">進路支援</p>
                <h3>学習計画生成</h3>
                <p class="list-meta">成績に応じた複数週の計画を生成します。</p>
              </RouterLink>
            </div>
          </section>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
