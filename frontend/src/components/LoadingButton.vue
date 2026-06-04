<script setup lang="ts">
withDefaults(
  defineProps<{
    loading?: boolean
    disabled?: boolean
    loadingLabel?: string
    type?: 'button' | 'submit' | 'reset'
  }>(),
  {
    loading: false,
    disabled: false,
    loadingLabel: '処理中...',
    type: 'button',
  },
)
</script>

<template>
  <button class="loading-button" :type="type" :disabled="disabled || loading">
    <span v-if="loading" class="button-inline">
      <span class="spinner" />
      {{ loadingLabel }}
    </span>
    <span v-else>
      <slot />
    </span>
  </button>
</template>

<style scoped>
.loading-button {
  border: none;
  border-radius: 999px;
  padding: 0.95rem 1.2rem;
  background: linear-gradient(135deg, var(--sea) 0%, var(--coral) 100%);
  color: white;
  font-weight: 600;
  box-shadow: 0 12px 28px rgba(15, 118, 110, 0.2);
}

.loading-button:disabled {
  cursor: not-allowed;
  opacity: 0.75;
}

.button-inline {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
}

.spinner {
  width: 0.95rem;
  height: 0.95rem;
  border-radius: 999px;
  border: 2px solid rgba(255, 255, 255, 0.32);
  border-top-color: white;
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
