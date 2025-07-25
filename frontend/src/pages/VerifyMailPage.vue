<template>
  <div class="h-screen flex flex-col justify-center items-center">
    <div class="lg:w-6/12 w-full p-6">
      <Card>
        <template #header>
          <div class="text-center">
            <h1 class="font-bold text-5xl mt-2">URBS</h1>
            <span
              class="text-surface-600 dark:text-surface-200 font-medium leading-normal"
              >Mail Verification</span
            >
          </div>
        </template>
        <template #content>
          <div v-if="loading" class="flex flex-col items-center">
            <ProgressSpinner />
            <span>Verifying Mail...</span>
          </div>
          <div v-else class="flex flex-col items-center gap-3">
            <span>If something failed you can re-request a token</span>
            <Button label="Request token" @click="cresend_token" />
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { resend_token, useCSRF, verify_mail } from '@/backend/security'
import { useRoute, useRouter } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'

const loading = ref(true)

const router = useRouter()
const route = useRoute()
const toast = useToast()

const { data: csrf, isSuccess } = useCSRF()

watch(isSuccess, () => {
  verify_mail(
    csrf.value,
    <string>route.params.username,
    <string>route.params.token,
  )
    .then(() => {
      toast.add({
        summary: 'Success',
        detail: `E-Mail was verified, you can now log in.`,
        severity: 'success',
        life: 2000,
      })
      router.push({
        name: 'Login',
      })
    })
    .catch(error => {
      toast.add({
        summary: 'Verification failed',
        detail: (<{ detail: string }>(<AxiosError>error)?.response?.data)
          .detail,
        severity: 'error',
        life: 2000,
      })
    })
    .finally(() => {
      loading.value = false
    })
})

function cresend_token() {
  resend_token(csrf.value, <string>route.params.username)
    .then(() => {
      toast.add({
        summary: 'Success',
        detail: `New token was sent out`,
        severity: 'success',
        life: 2000,
      })
    })
    .catch(error => {
      toast.add({
        summary: 'Sending token failed',
        detail: (<{ detail: string }>(<AxiosError>error)?.response?.data)
          .detail,
        severity: 'error',
        life: 2000,
      })
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<style scoped></style>
