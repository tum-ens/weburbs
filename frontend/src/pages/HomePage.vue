<template>
  <div class="h-screen flex flex-col">
    <Header />
    <div class="flex-grow p-3 gap-3 flex flex-row">
      <SidebarComponent />
      <div class="flex-grow">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Header from '@/components/HeaderComponent.vue'
import { useAuthenticated } from '@/backend/security'
import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SidebarComponent from '@/components/SidebarComponent.vue'

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
