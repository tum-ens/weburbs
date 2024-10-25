<template>
  <div class="flex flex-col w-full">
    <Header />
  </div>
</template>

<script setup lang="ts">
import Header from '@/components/HeaderComponent.vue'
import { useAuthenticated } from '@/backend/security'
import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const { data: authenticated } = useAuthenticated()
const router = useRouter()
const route = useRoute()
watch(
  authenticated,
  () => {
    if (!authenticated.value) {
      router.push({
        name: 'Login',
        query: {
          redirect: route.fullPath,
        },
      })
    }
  },
  { immediate: true },
)
</script>

<style scoped></style>
