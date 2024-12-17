<template>
  <div
    class="w-full h-14 p-3 bg-surface-0 dark:bg-surface-800 flex flex-row justify-between items-center"
  >
    <Button
      class="lg:invisible"
      text
      rounded
      icon="pi pi-bars"
      aria-label="Logout"
      @click="() => (sidebar = !sidebar)"
    />
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
import { useRouter } from 'vue-router'

const sidebar = defineModel<boolean>('sidebar', { default: false })

const queryClient = useQueryClient()
const router = useRouter()

async function clogout() {
  await router.push({
    name: 'Landing',
  })
  await logout(queryClient)
}
</script>

<style scoped></style>
