import { createRouter, createWebHistory } from 'vue-router'

const ACCESS_TOKEN_KEY = 'tutorhub.accessToken'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/students',
      name: 'students',
      component: () => import('../views/StudentListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/students/:id',
      name: 'student-detail',
      component: () => import('../views/StudentDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/lessons/new',
      name: 'lesson-form',
      component: () => import('../views/LessonFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/studio/ai/lesson-feedback',
      name: 'ai-lesson-feedback',
      component: () => import('../views/AiLessonFeedbackView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/studio/ai/homework-suggestion',
      name: 'ai-homework-suggestion',
      component: () => import('../views/AiHomeworkSuggestionView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/studio/ai/study-plan',
      name: 'ai-study-plan',
      component: () => import('../views/AiStudyPlanView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to) => {
  const hasToken = Boolean(localStorage.getItem(ACCESS_TOKEN_KEY))

  if (to.meta.requiresAuth && !hasToken) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && hasToken) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
