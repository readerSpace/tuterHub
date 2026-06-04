<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    description?: string
    text?: string
    items?: string[]
    tone?: 'calm' | 'accent'
  }>(),
  {
    description: '',
    text: '',
    items: () => [],
    tone: 'calm',
  },
)
</script>

<template>
  <section class="result-card" :class="tone">
    <div class="section-header compact">
      <div>
        <p class="eyebrow">AI Output</p>
        <h3>{{ title }}</h3>
      </div>
      <p v-if="description" class="description">{{ description }}</p>
    </div>

    <p v-if="text" class="result-text">{{ text }}</p>

    <ol v-if="items.length" class="result-list">
      <li v-for="item in items" :key="item">{{ item }}</li>
    </ol>
  </section>
</template>

<style scoped>
.result-card {
  padding: 1.4rem;
  border-radius: var(--radius-xl);
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
}

.result-card.calm {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.88) 0%, rgba(243, 250, 248, 0.92) 100%);
}

.result-card.accent {
  background: linear-gradient(180deg, rgba(255, 247, 238, 0.94) 0%, rgba(255, 255, 255, 0.92) 100%);
}

.compact {
  align-items: start;
}

h3 {
  margin: 0.45rem 0 0;
  color: var(--ink-strong);
  font-family: var(--font-heading);
}

.description {
  margin: 0;
  color: var(--ink-soft);
}

.result-text {
  margin: 1rem 0 0;
  color: var(--ink-strong);
  white-space: pre-wrap;
}

.result-list {
  margin: 1rem 0 0;
  padding-left: 1.2rem;
  display: grid;
  gap: 0.7rem;
  color: var(--ink-strong);
}
</style>
