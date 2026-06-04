<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../stores/authStore'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

onMounted(() => {
  void authStore.initialize()
})

const navigation = [
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Students', to: '/students' },
  { label: 'New Lesson', to: '/lessons/new' },
  { label: 'AI Feedback', to: '/studio/ai/lesson-feedback' },
  { label: 'Homework', to: '/studio/ai/homework-suggestion' },
  { label: 'Study Plan', to: '/studio/ai/study-plan' },
]

const initials = computed(() => authStore.displayName.slice(0, 1).toUpperCase())

function isActive(path: string) {
  if (path === '/dashboard') {
    return route.path === path
  }
  return route.path === path || route.path.startsWith(`${path}/`)
}

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<template>
  <div class="shell">
    <aside class="sidebar">
      <div>
        <p class="eyebrow">TutorHub</p>
        <h1>AI Learning Studio</h1>
        <p class="lead">講師向けの授業管理と AI 支援をひとつの画面に集約します。</p>
      </div>

      <nav class="nav-grid">
        <RouterLink
          v-for="item in navigation"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          :class="{ active: isActive(item.to) }"
        >
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="profile-chip">
        <div class="avatar">{{ initials }}</div>
        <div>
          <strong>{{ authStore.displayName }}</strong>
          <p>{{ authStore.user?.role || 'authorized' }}</p>
        </div>
        <button class="ghost-button" type="button" @click="handleLogout">Sign out</button>
      </div>
    </aside>

    <main class="content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.shell {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  min-height: 100vh;
}

.sidebar {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 2rem;
  padding: 2rem;
  background: linear-gradient(180deg, rgba(255, 248, 236, 0.88) 0%, rgba(219, 239, 234, 0.82) 100%);
  border-right: 1px solid rgba(18, 33, 38, 0.1);
  backdrop-filter: blur(18px);
}

.eyebrow {
  margin: 0 0 0.75rem;
  font-family: var(--font-heading);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.74rem;
  color: var(--sea);
}

h1 {
  margin: 0;
  font-family: var(--font-heading);
  font-size: clamp(2rem, 4vw, 3.4rem);
  line-height: 0.96;
  color: var(--ink-strong);
}

.lead {
  margin: 1rem 0 0;
  color: var(--ink-soft);
}

.nav-grid {
  display: grid;
  gap: 0.7rem;
}

.nav-link {
  padding: 0.95rem 1rem;
  border-radius: 1rem;
  border: 1px solid rgba(18, 33, 38, 0.08);
  background: rgba(255, 255, 255, 0.56);
  color: var(--ink-strong);
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.nav-link:hover,
.nav-link.active {
  transform: translateY(-1px);
  border-color: rgba(15, 118, 110, 0.28);
  background: rgba(15, 118, 110, 0.12);
}

.profile-chip {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.85rem;
  align-items: center;
  padding: 1rem;
  border-radius: 1.2rem;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: var(--shadow);
}

.avatar {
  width: 2.8rem;
  height: 2.8rem;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--sea) 0%, var(--coral) 100%);
  color: white;
  font-family: var(--font-heading);
  font-weight: 700;
}

strong,
.profile-chip p {
  display: block;
}

.profile-chip p {
  margin: 0.1rem 0 0;
  color: var(--ink-soft);
  text-transform: capitalize;
}

.ghost-button {
  border: none;
  border-radius: 999px;
  padding: 0.75rem 1rem;
  background: rgba(18, 33, 38, 0.06);
  color: var(--ink-strong);
}

.content {
  padding: 2rem;
}

@media (max-width: 960px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    border-right: none;
    border-bottom: 1px solid rgba(18, 33, 38, 0.1);
  }

  .content {
    padding: 1rem;
  }
}
</style>
