<template>
  <DefaultLayout>
    <router-view />
  </DefaultLayout>
</template>

<script setup lang="ts">
import { useAuthenticated } from '@/backend/security'
import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DefaultLayout from '@/layout/DefaultLayout.vue'

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
