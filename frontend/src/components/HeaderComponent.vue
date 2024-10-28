<template>
  <div
    class="w-full h-14 p-3 bg-surface-0 flex flex-row justify-between items-center"
  >
    <Button
      class="invisible"
      text
      rounded
      icon="pi pi-bars"
      aria-label="Logout"
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
