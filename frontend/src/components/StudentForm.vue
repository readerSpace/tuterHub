<script setup lang="ts">
import { reactive, watch } from 'vue'

import type { StudentFormState } from '../types/student'
import LoadingButton from './LoadingButton.vue'

const props = withDefaults(
  defineProps<{
    modelValue: StudentFormState
    submitting?: boolean
    teacherLocked?: boolean
  }>(),
  {
    submitting: false,
    teacherLocked: false,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: StudentFormState]
  submit: []
}>()

const form = reactive<StudentFormState>({ ...props.modelValue })

watch(
  () => props.modelValue,
  (nextValue) => {
    Object.assign(form, nextValue)
  },
  { deep: true },
)

watch(
  form,
  () => {
    emit('update:modelValue', { ...form })
  },
  { deep: true },
)
</script>

<template>
  <form class="panel-surface form-stack" @submit.prevent="emit('submit')">
    <div class="section-header">
      <div>
        <p class="eyebrow">New Student</p>
        <h3>生徒を登録</h3>
      </div>
      <p class="muted">Django 側の `students` エンドポイントへ直接登録します。</p>
    </div>

    <div class="form-grid two-columns">
      <label class="field">
        <span>生徒名</span>
        <input v-model="form.full_name" required placeholder="山田太郎" />
      </label>
      <label class="field">
        <span>学年</span>
        <input v-model="form.grade" required placeholder="中3" />
      </label>
      <label class="field">
        <span>学校名</span>
        <input v-model="form.school" placeholder="大分中学校" />
      </label>
      <label class="field">
        <span>志望校</span>
        <input v-model="form.target_school" placeholder="大分上野丘高校" />
      </label>
      <label class="field">
        <span>苦手分野</span>
        <input v-model="form.weak_subjects" placeholder="数学, 英語" />
      </label>
      <label class="field">
        <span>保護者連絡先</span>
        <input v-model="form.guardian_contact" placeholder="parent@example.com" />
      </label>
      <label class="field">
        <span>担当講師 ID</span>
        <input v-model="form.teacher" :disabled="teacherLocked" inputmode="numeric" placeholder="1" />
      </label>
      <label class="field">
        <span>保護者 ID</span>
        <input v-model="form.parent" inputmode="numeric" placeholder="2" />
      </label>
      <label class="field field-wide">
        <span>メモ</span>
        <textarea v-model="form.notes" rows="4" placeholder="学習メモやフォロー方針" />
      </label>
    </div>

    <LoadingButton :loading="submitting" type="submit" loading-label="登録中...">
      生徒を登録
    </LoadingButton>
  </form>
</template>
