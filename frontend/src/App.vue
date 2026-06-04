<script setup lang="ts">
import { onMounted } from 'vue'

import { useAuthStore } from './stores/authStore'

const authStore = useAuthStore()

onMounted(() => {
  void authStore.initialize()
})
</script>

<template>
  <RouterView />
</template>
