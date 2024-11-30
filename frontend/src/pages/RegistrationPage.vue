<template>
  <div class="h-screen flex flex-col justify-center items-center">
    <div class="lg:w-6/12 w-full p-6">
      <Card>
        <template #header>
          <div class="text-center">
            <h1 class="font-bold text-5xl mt-2">URBS</h1>
            <span
              class="text-surface-600 dark:text-surface-200 font-medium leading-normal"
              >Already have an account?</span
            >
            <RouterLink
              to="/login"
              class="font-medium no-underline ml-2 text-primary cursor-pointer"
              >Login
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
                  @keydown.enter="cregister"
                />
                <label for="username">Username</label>
              </FloatLabel>

              <FloatLabel variant="on" class="w-full mb-6">
                <InputText
                  fluid
                  :disabled="loading"
                  id="email"
                  type="email"
                  v-model="email"
                  @keydown.enter="cregister"
                />
                <label for="email">E-Mail</label>
              </FloatLabel>

              <FloatLabel variant="on" class="w-full mb-6">
                <InputText
                  fluid
                  :disabled="loading"
                  id="password"
                  type="password"
                  v-model="password"
                  @keydown.enter="cregister"
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
                @click="cregister"
              />
              <Message v-if="error" class="mt-2" severity="error"
                >{{ error }}
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
import { register, useAuthenticated, useCSRF } from '@/backend/security'
import { useRoute, useRouter } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'

const { data: authenticated } = useAuthenticated()
const { data: csrf } = useCSRF()
const username = ref('')
const email = ref('')
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

async function cregister() {
  loading.value = true
  await register(csrf.value, username.value, email.value, password.value)
    .then(() => {
      toast.add({
        summary: 'Success',
        detail: `Account was created, you can now log in`,
        severity: 'success',
        life: 2000,
      })
      router.push({
        name: 'Login',
      })
    })
    .catch(error => {
      toast.add({
        summary: 'Registration failed',
        detail: (<{ detail: string }>(<AxiosError>error)?.response?.data)
          .detail,
        severity: 'error',
        life: 2000,
      })
    })
  loading.value = false
}
</script>

<style scoped></style>
