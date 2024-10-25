<template>
  <div class="w-screen p-3">
    <Menubar :model="items">
      <template #end>
        <Button
          text
          rounded
          icon="pi pi-sign-out"
          aria-label="Logout"
          @click="clogout"
        />
      </template>
    </Menubar>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { logout } from '@/backend/security'
import { useQueryClient } from '@tanstack/vue-query'
import { useRouter } from 'vue-router'

const items = ref([
  {
    label: 'Home',
    icon: 'pi pi-home',
  },
])

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
