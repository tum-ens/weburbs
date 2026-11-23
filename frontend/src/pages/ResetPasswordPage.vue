<template>
  <div class="h-screen flex flex-col justify-center items-center">
    <div class="lg:w-6/12 w-full p-6">
      <Card>
        <template #header>
          <div class="text-center">
            <h1 class="font-bold text-5xl mt-2">URBS</h1>
            <span
              class="text-surface-600 dark:text-surface-200 font-medium leading-normal"
            >
              {{ hasToken ? 'Set a new password' : 'Reset your password' }}
            </span>
          </div>
        </template>
        <template #content>
          <!-- Step 2: set a new password (came from email link) -->
          <div v-if="hasToken">
            <div v-if="!done">
              <FloatLabel variant="on" class="w-full mb-6">
                <InputText
                  fluid
                  :disabled="loading"
                  id="password"
                  type="password"
                  v-model="password"
                  @keydown.enter="csetPassword"
                />
                <label for="password">New password</label>
              </FloatLabel>

              <FloatLabel variant="on" class="w-full mb-6">
                <InputText
                  fluid
                  :disabled="loading"
                  id="confirm"
                  type="password"
                  v-model="confirmPassword"
                  @keydown.enter="csetPassword"
                />
                <label for="confirm">Confirm new password</label>
              </FloatLabel>

              <Button
                :loading="loading"
                label="Set new password"
                icon="pi pi-lock"
                class="w-full"
                @click="csetPassword"
              />
              <Message v-if="error" class="mt-2" severity="error">
                {{ error }}
              </Message>
            </div>
            <div v-else class="flex flex-col items-center gap-3">
              <span>Your password has been updated.</span>
              <RouterLink
                to="/login"
                class="font-medium no-underline text-primary cursor-pointer"
              >
                Back to login
              </RouterLink>
            </div>
          </div>

          <!-- Step 1: request a reset link -->
          <div v-else>
            <div v-if="!requested">
              <p class="text-surface-600 dark:text-surface-300 mb-4">
                Enter the email address for your account and we'll send you a
                link to set a new password.
              </p>
              <FloatLabel variant="on" class="w-full mb-6">
                <InputText
                  fluid
                  :disabled="loading"
                  id="email"
                  type="email"
                  v-model="email"
                  @keydown.enter="crequestReset"
                />
                <label for="email">Email</label>
              </FloatLabel>

              <Button
                :loading="loading"
                label="Send reset link"
                icon="pi pi-envelope"
                class="w-full"
                @click="crequestReset"
              />
              <Message v-if="error" class="mt-2" severity="error">
                {{ error }}
              </Message>
            </div>
            <div v-else class="flex flex-col items-center gap-3 text-center">
              <i class="pi pi-check-circle text-3xl text-green-500" />
              <span>
                If an account with that email exists, a reset link has been
                sent. Please check your inbox.
              </span>
              <RouterLink
                to="/login"
                class="font-medium no-underline text-primary cursor-pointer"
              >
                Back to login
              </RouterLink>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  request_password_reset,
  reset_password,
  useCSRF,
} from '@/backend/security'
import { useRoute, useRouter } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { data: csrf } = useCSRF()

const hasToken = computed(() => !!route.params.username && !!route.params.token)

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)
const requested = ref(false)
const done = ref(false)

function extractDetail(err: unknown, fallback: string) {
  const detail = (<{ detail?: string }>(<AxiosError>err)?.response?.data)
    ?.detail
  return detail || fallback
}

async function crequestReset() {
  error.value = ''
  if (!email.value.trim()) {
    error.value = 'Please enter your email.'
    return
  }
  loading.value = true
  try {
    await request_password_reset(csrf.value, email.value.trim())
    requested.value = true
  } catch (err) {
    error.value = extractDetail(err, 'Could not send reset link.')
  } finally {
    loading.value = false
  }
}

async function csetPassword() {
  error.value = ''
  if (password.value.length < 5) {
    error.value = 'Password must be at least 5 characters.'
    return
  }
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match.'
    return
  }
  loading.value = true
  try {
    await reset_password(
      csrf.value,
      <string>route.params.username,
      <string>route.params.token,
      password.value,
    )
    done.value = true
    toast.add({
      summary: 'Password updated',
      detail: 'You can now log in with your new password.',
      severity: 'success',
      life: 3000,
    })
    setTimeout(() => router.push({ name: 'Login' }), 1500)
  } catch (err) {
    error.value = extractDetail(err, 'Could not reset password.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped></style>
