<script setup lang="ts">
import { reactive, watch } from 'vue'

import type { SelectOption } from '../types/common'
import type { LessonFormState } from '../types/lesson'
import LoadingButton from './LoadingButton.vue'

const props = withDefaults(
  defineProps<{
    modelValue: LessonFormState
    studentOptions: SelectOption[]
    saving?: boolean
    generating?: boolean
  }>(),
  {
    saving: false,
    generating: false,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: LessonFormState]
  submit: []
  'generate-feedback': []
}>()

const form = reactive<LessonFormState>({ ...props.modelValue })

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
        <p class="eyebrow">Lesson Studio</p>
        <h3>授業記録を保存</h3>
      </div>
      <p class="muted">Lesson と LessonReport を続けて保存し、必要なら AI で保護者コメントも生成します。</p>
    </div>

    <div class="form-grid two-columns">
      <label class="field">
        <span>生徒</span>
        <select v-model="form.student" required>
          <option value="">生徒を選択してください</option>
          <option v-for="option in studentOptions" :key="option.value" :value="String(option.value)">
            {{ option.label }}
          </option>
        </select>
      </label>
      <label class="field">
        <span>科目</span>
        <input v-model="form.subject" required placeholder="数学" />
      </label>
      <label class="field">
        <span>開始日時</span>
        <input v-model="form.start_time" type="datetime-local" required />
      </label>
      <label class="field">
        <span>終了日時</span>
        <input v-model="form.end_time" type="datetime-local" required />
      </label>
      <label class="field">
        <span>授業形式</span>
        <select v-model="form.lesson_format">
          <option value="in_person">対面</option>
          <option value="online">オンライン</option>
        </select>
      </label>
      <label class="field">
        <span>授業ステータス</span>
        <select v-model="form.status">
          <option value="scheduled">予定</option>
          <option value="completed">実施済み</option>
          <option value="absent">欠席</option>
          <option value="rescheduled">振替</option>
        </select>
      </label>
      <label class="field field-wide">
        <span>授業内容</span>
        <textarea v-model="form.content" rows="4" required placeholder="今日扱った単元や学習内容" />
      </label>
      <label class="field">
        <span>理解度</span>
        <input v-model.number="form.understanding_level" type="number" min="1" max="5" required />
      </label>
      <label class="field field-wide">
        <span>講師メモ</span>
        <textarea v-model="form.teacher_note" rows="4" placeholder="AI コメント生成時に使う補足メモ" />
      </label>
      <label class="field field-wide">
        <span>宿題</span>
        <textarea v-model="form.homework" rows="3" placeholder="宿題内容" />
      </label>
      <label class="field field-wide">
        <span>次回計画</span>
        <textarea v-model="form.next_plan" rows="3" placeholder="次回の指導方針" />
      </label>
      <label class="field field-wide">
        <span>保護者コメント</span>
        <textarea v-model="form.parent_comment" rows="5" placeholder="AI 生成結果または手入力コメント" />
      </label>
    </div>

    <div class="button-row">
      <LoadingButton :loading="generating" type="button" loading-label="生成中..." @click="emit('generate-feedback')">
        AIで保護者向けコメント生成
      </LoadingButton>
      <LoadingButton :loading="saving" type="submit" loading-label="保存中...">
        保存
      </LoadingButton>
    </div>
  </form>
</template>
