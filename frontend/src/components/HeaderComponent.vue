<template>
  <div
    class="w-full h-14 p-3 bg-surface-0 dark:bg-surface-800 flex flex-row justify-between items-center"
  >
    <div
      class="bg-surface-0 dark:bg-surface-800 flex flex-row justify-start items-center gap-2"
    >
      <Button
        class="lg:invisible"
        text
        rounded
        icon="pi pi-bars"
        aria-label="Logout"
        @click="() => (sidebar = !sidebar)"
      />
      <router-link to="/home">
        <strong>URBS</strong>
      </router-link>
      <span>{{ route.params.proj }}</span>
    </div>
    <Button
      text
      rounded
      icon="pi pi-sign-out"
      aria-label="Logout"
      @click="clogout"
    />
  </div>
</template>

<script setup lang="ts">
import { logout } from '@/backend/security'
import { useQueryClient } from '@tanstack/vue-query'
import { useRoute, useRouter } from 'vue-router'

const sidebar = defineModel<boolean>('sidebar', { default: false })

const queryClient = useQueryClient()
const router = useRouter()
const route = useRoute()

async function clogout() {
  await router.push({
    name: 'Landing',
  })
  await logout(queryClient)
}
</script>

<style scoped></style>
