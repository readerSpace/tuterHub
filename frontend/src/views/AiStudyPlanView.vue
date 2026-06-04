<script setup lang="ts">
import { reactive, ref } from 'vue'

import { generateStudyPlan } from '../api/aiApi'
import AppLayout from '../components/AppLayout.vue'
import AiResultCard from '../components/AiResultCard.vue'
import LoadingButton from '../components/LoadingButton.vue'
import { getErrorMessage } from '../lib/errors'
import type { ScoreInput, StudyPlanItem } from '../types/ai'

const form = reactive({
  student_name: '',
  grade: '',
  target_school: '',
  weeks: 4,
})
const scores = ref<ScoreInput[]>([
  { subject: '数学', score: 58, max_score: 100 },
  { subject: '英語', score: 66, max_score: 100 },
])
const plan = ref<StudyPlanItem[]>([])
const loading = ref(false)
const errorMessage = ref('')

function addScoreRow() {
  scores.value = [...scores.value, { subject: '', score: 0, max_score: 100 }]
}

function removeScoreRow(index: number) {
  if (scores.value.length === 1) {
    return
  }
  scores.value = scores.value.filter((_, rowIndex) => rowIndex !== index)
}

async function handleGenerate() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await generateStudyPlan({
      student_name: form.student_name,
      grade: form.grade,
      target_school: form.target_school,
      weeks: form.weeks,
      scores: scores.value,
    })
    plan.value = response.plan
  } catch (error) {
    errorMessage.value = getErrorMessage(error, '学習計画の生成に失敗しました。')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppLayout>
    <div class="page-stack">
      <section class="hero-card">
        <p class="eyebrow">AI Study Plan</p>
        <h2 class="hero-title">学習計画を生成</h2>
        <p class="hero-copy">複数科目のスコアと志望校を入力すると、数週間分の学習アクションを自動生成します。</p>
      </section>

      <div class="split-grid">
        <form class="panel-surface form-stack" @submit.prevent="handleGenerate">
          <div class="section-header compact">
            <div>
              <p class="eyebrow">Study Plan Inputs</p>
              <h3>入力</h3>
            </div>
          </div>

          <div class="form-grid two-columns">
            <label class="field">
              <span>生徒名</span>
              <input v-model="form.student_name" required placeholder="山田太郎" />
            </label>
            <label class="field">
              <span>学年</span>
              <input v-model="form.grade" required placeholder="中3" />
            </label>
            <label class="field field-wide">
              <span>志望校</span>
              <input v-model="form.target_school" required placeholder="大分上野丘高校" />
            </label>
            <label class="field">
              <span>計画週数</span>
              <input v-model.number="form.weeks" type="number" min="1" max="12" required />
            </label>
          </div>

          <section class="stack-grid">
            <div class="section-header">
              <div>
                <p class="eyebrow">Scores</p>
                <h3>科目スコア</h3>
              </div>
              <button class="quiet-button" type="button" @click="addScoreRow">科目を追加</button>
            </div>

            <article v-for="(score, index) in scores" :key="index" class="list-card">
              <div class="form-grid two-columns">
                <label class="field">
                  <span>科目</span>
                  <input v-model="score.subject" required placeholder="数学" />
                </label>
                <label class="field">
                  <span>得点</span>
                  <input v-model.number="score.score" type="number" min="0" required />
                </label>
                <label class="field">
                  <span>満点</span>
                  <input v-model.number="score.max_score" type="number" min="1" required />
                </label>
                <div class="page-actions">
                  <button class="quiet-button" type="button" @click="removeScoreRow(index)">削除</button>
                </div>
              </div>
            </article>
          </section>

          <p v-if="errorMessage" class="helper-text warning-text">{{ errorMessage }}</p>

          <LoadingButton :loading="loading" type="submit" loading-label="生成中...">
            学習計画を生成
          </LoadingButton>
        </form>

        <AiResultCard
          title="学習計画"
          description="FastAPI の /ai/study-plan を呼び出しています。"
          :items="plan.map((item) => `Week ${item.week}: ${item.task}`)"
        />
      </div>
    </div>
  </AppLayout>
</template>
