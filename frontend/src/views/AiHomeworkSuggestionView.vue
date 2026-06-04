<script setup lang="ts">
import { computed, reactive, ref } from 'vue'

import { generateHomeworkSuggestion } from '../api/aiApi'
import AppLayout from '../components/AppLayout.vue'
import AiResultCard from '../components/AiResultCard.vue'
import LoadingButton from '../components/LoadingButton.vue'
import { getErrorMessage } from '../lib/errors'

const form = reactive({
  student_name: '',
  grade: '',
  subject: '',
  weak_points: '',
  available_minutes: 30,
})
const homework = ref<string[]>([])
const loading = ref(false)
const errorMessage = ref('')

const weakPointsPreview = computed(() =>
  form.weak_points
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean),
)

async function handleGenerate() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await generateHomeworkSuggestion({
      student_name: form.student_name,
      grade: form.grade,
      subject: form.subject,
      weak_points: weakPointsPreview.value,
      available_minutes: form.available_minutes,
    })
    homework.value = response.homework
  } catch (error) {
    errorMessage.value = getErrorMessage(error, '宿題提案の生成に失敗しました。')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppLayout>
    <div class="page-stack">
      <section class="hero-card">
        <p class="eyebrow">AI Homework</p>
        <h2 class="hero-title">宿題提案を生成</h2>
        <p class="hero-copy">苦手分野と可処分時間から、すぐ配布できる宿題案を複数生成します。</p>
      </section>

      <div class="split-grid">
        <form class="panel-surface form-stack" @submit.prevent="handleGenerate">
          <div class="section-header compact">
            <div>
              <p class="eyebrow">Homework Inputs</p>
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
              <input v-model="form.grade" required placeholder="中2" />
            </label>
            <label class="field">
              <span>科目</span>
              <input v-model="form.subject" required placeholder="数学" />
            </label>
            <label class="field">
              <span>学習可能時間</span>
              <input v-model.number="form.available_minutes" type="number" min="1" max="300" required />
            </label>
            <label class="field field-wide">
              <span>苦手分野</span>
              <textarea v-model="form.weak_points" rows="4" required placeholder="一次関数, 連立方程式" />
            </label>
          </div>

          <div class="hero-actions">
            <span v-for="item in weakPointsPreview" :key="item" class="pill neutral">{{ item }}</span>
          </div>

          <p v-if="errorMessage" class="helper-text warning-text">{{ errorMessage }}</p>

          <LoadingButton :loading="loading" type="submit" loading-label="生成中...">
            宿題提案を生成
          </LoadingButton>
        </form>

        <AiResultCard
          title="宿題候補"
          description="FastAPI の /ai/homework-suggestion を利用しています。"
          :items="homework"
        />
      </div>
    </div>
  </AppLayout>
</template>
