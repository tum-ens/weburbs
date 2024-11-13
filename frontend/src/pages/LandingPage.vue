<template>
  <div class="h-screen flex flex-col justify-center text-center">
    <h1 class="text-9xl font-bold">URBS</h1>
    <RouterLink to="/login" class="hover:underline">Login</RouterLink>
  </div>
</template>

<script setup lang="ts">
import { useAuthenticated } from '@/backend/security'
import { watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const { data: authenticated } = useAuthenticated()

watch(
  authenticated,
  () => {
    if (authenticated.value) {
      router.push({ name: 'Home' })
    }
  },
  { immediate: true },
)
</script>

<style scoped></style>
