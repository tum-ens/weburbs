<template>
  <div class="h-screen flex flex-col justify-center items-center">
    <div class="lg:w-6/12 w-full p-6">
      <Card>
        <template #header>
          <div class="text-center">
            <h1 class="font-bold text-5xl mt-2">URBS</h1>
            <span
              class="text-surface-600 dark:text-surface-200 font-medium leading-normal"
              >Don't have an account?</span
            >
            <RouterLink
              to="/register"
              class="font-medium no-underline ml-2 text-primary cursor-pointer"
            >
              Create today!
            </RouterLink>
          </div>
        </template>
        <template #content>
          <div v-if="!authenticated">
            <div>
              <FloatLabel variant="on" class="w-full mb-6">
                <InputText
                  fluid
                  :disabled="loading"
                  id="username"
                  type="text"
                  v-model="username"
                  @keydown.enter="clogin"
                />
                <label for="username">Username</label>
              </FloatLabel>

              <FloatLabel variant="on" class="w-full mb-6">
                <InputText
                  fluid
                  :disabled="loading"
                  id="password"
                  type="password"
                  v-model="password"
                  @keydown.enter="clogin"
                />
                <label for="password">Password</label>
              </FloatLabel>

              <div class="flex justify-end mb-12">
                <RouterLink
                  to="/resetPassword"
                  class="font-medium no-underline ml-2 text-primary text-right cursor-pointer"
                  >Forgot password?
                </RouterLink>
              </div>

              <Button
                :loading="loading"
                label="Sign In"
                icon="pi pi-user"
                class="w-full"
                @click="clogin"
              />
              <Message
                v-if="error"
                class="flex-grow mt-2"
                fluid
                severity="error"
              >
                <div class="flex flex-row gap-3 items-center">
                  <span>{{ error }}</span>
                  <Button
                    class=""
                    label="Resend Token"
                    severity="info"
                    @click="cresend_token"
                  />
                </div>
              </Message>
            </div>
          </div>
          <div v-else>
            <p>Already authenticated!</p>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  login,
  resend_token,
  useAuthenticated,
  useCSRF,
} from '@/backend/security'
import { useQueryClient } from '@tanstack/vue-query'
import { useRoute, useRouter } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'

const { data: authenticated } = useAuthenticated()
const { data: csrf } = useCSRF()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const router = useRouter()
const route = useRoute()
const toast = useToast()
watch(
  authenticated,
  () => {
    if (authenticated.value) {
      if (route.query['redirect'])
        router.push({ path: <string>route.query['redirect'] })
      else router.push({ name: 'Home' })
    }
  },
  { immediate: true },
)

const queryClient = useQueryClient()

async function clogin() {
  loading.value = true
  const login_result = await login(
    queryClient,
    csrf.value,
    username.value,
    password.value,
  )
  console.log(login_result)
  if (login_result === 'verification') {
    error.value = 'Please verify your mail first'
    loading.value = false
    return
  }

  if (!login_result) {
    error.value = 'Wrong username or password.'
  } else {
    error.value = ''
  }
  loading.value = false
}

function cresend_token() {
  resend_token(csrf.value, username.value)
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
