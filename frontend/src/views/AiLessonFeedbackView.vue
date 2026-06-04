<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import { generateLessonFeedback } from '../api/aiApi'
import AppLayout from '../components/AppLayout.vue'
import AiResultCard from '../components/AiResultCard.vue'
import LoadingButton from '../components/LoadingButton.vue'
import { getErrorMessage } from '../lib/errors'

const route = useRoute()

const form = reactive({
  student_name: '',
  subject: '',
  lesson_content: '',
  understanding_level: 3,
  teacher_note: '',
})
const feedback = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleGenerate() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await generateLessonFeedback({ ...form })
    feedback.value = response.feedback
  } catch (error) {
    errorMessage.value = getErrorMessage(error, 'AI コメント生成に失敗しました。')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (typeof route.query.studentName === 'string') {
    form.student_name = route.query.studentName
  }
})
</script>

<template>
  <AppLayout>
    <div class="page-stack">
      <section class="hero-card">
        <p class="eyebrow">AI Feedback</p>
        <h2 class="hero-title">AI 保護者コメント生成</h2>
        <p class="hero-copy">授業内容と理解度から、保護者にそのまま送れる自然なコメント文を生成します。</p>
      </section>

      <div class="split-grid">
        <form class="panel-surface form-stack" @submit.prevent="handleGenerate">
          <div class="section-header compact">
            <div>
              <p class="eyebrow">Prompt Inputs</p>
              <h3>入力</h3>
            </div>
          </div>

          <div class="form-grid two-columns">
            <label class="field">
              <span>生徒名</span>
              <input v-model="form.student_name" required placeholder="山田太郎" />
            </label>
            <label class="field">
              <span>科目</span>
              <input v-model="form.subject" required placeholder="英語" />
            </label>
            <label class="field field-wide">
              <span>授業内容</span>
              <textarea v-model="form.lesson_content" rows="5" required placeholder="長文読解と要約" />
            </label>
            <label class="field">
              <span>理解度</span>
              <input v-model.number="form.understanding_level" type="number" min="1" max="5" required />
            </label>
            <label class="field field-wide">
              <span>講師メモ</span>
              <textarea v-model="form.teacher_note" rows="4" required placeholder="接続詞の見落としがあった" />
            </label>
          </div>

          <p v-if="errorMessage" class="helper-text warning-text">{{ errorMessage }}</p>

          <LoadingButton :loading="loading" type="submit" loading-label="生成中...">
            AIコメントを生成
          </LoadingButton>
        </form>

        <AiResultCard
          title="生成結果"
          description="FastAPI の /ai/lesson-feedback を呼び出しています。"
          :text="feedback"
          tone="accent"
        />
      </div>
    </div>
  </AppLayout>
</template>
