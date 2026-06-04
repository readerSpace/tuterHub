<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import LoadingButton from '../components/LoadingButton.vue'
import { getErrorMessage } from '../lib/errors'
import { useAuthStore } from '../stores/authStore'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  password: '',
})
const errorMessage = ref('')

const redirectTo = computed(() => {
  if (typeof route.query.redirect === 'string' && route.query.redirect.startsWith('/')) {
    return route.query.redirect
  }
  return '/dashboard'
})

async function handleSubmit() {
  errorMessage.value = ''

  try {
    await authStore.login({ ...form })
    await router.replace(redirectTo.value)
  } catch (error) {
    errorMessage.value = getErrorMessage(error, 'ログインに失敗しました。資格情報を確認してください。')
  }
}
</script>

<template>
  <main class="login-view">
    <section class="login-card">
      <p class="eyebrow">TutorHub Frontend</p>
      <h1>Sign in to the studio</h1>
      <p class="copy">JWT 認証で Django API と AI サービスをまとめて利用するフロントエンドです。</p>

      <form class="field-grid" @submit.prevent="handleSubmit">
        <label>
          <span>Username</span>
          <input v-model="form.username" type="text" autocomplete="username" placeholder="admin" />
        </label>
        <label>
          <span>Password</span>
          <input v-model="form.password" type="password" autocomplete="current-password" placeholder="••••••••" />
        </label>

        <p v-if="errorMessage" class="warning">{{ errorMessage }}</p>

        <LoadingButton :loading="authStore.busy" type="submit" loading-label="認証中...">
          ログイン
        </LoadingButton>
      </form>

      <div class="tip-row">
        <span class="tip">Django: /api/auth/token/</span>
        <span class="tip">FastAPI: /ai/*</span>
      </div>
    </section>
  </main>
</template>

<style scoped>
.login-view {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.5rem;
}

.login-card {
  width: min(560px, 100%);
  padding: 2rem;
  border-radius: 2rem;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: var(--shadow);
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: var(--sea);
  font-family: var(--font-heading);
  font-size: 0.76rem;
}

h1 {
  margin: 0.8rem 0 0;
  font-size: clamp(2.2rem, 8vw, 4rem);
  line-height: 0.94;
  font-family: var(--font-heading);
  color: var(--ink-strong);
}

.copy {
  margin: 1rem 0 0;
  color: var(--ink-soft);
}

.field-grid {
  display: grid;
  gap: 1rem;
  margin-top: 1.8rem;
}

label {
  display: grid;
  gap: 0.5rem;
}

span {
  color: var(--ink-strong);
}

input {
  border: 1px solid rgba(18, 33, 38, 0.12);
  border-radius: 1rem;
  padding: 0.95rem 1rem;
  background: rgba(255, 255, 255, 0.82);
}

.warning {
  margin: 0;
  color: #9a4f2d;
}

.tip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-top: 1.2rem;
}

.tip {
  border-radius: 999px;
  padding: 0.45rem 0.8rem;
  background: rgba(15, 118, 110, 0.08);
  color: var(--sea-deep);
  font-size: 0.9rem;
}
</style>
