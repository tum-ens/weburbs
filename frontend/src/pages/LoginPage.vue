<template>
  <div class="w-screen min-h-screen flex flex-col justify-center items-center">
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
              <label
                for="username"
                class="text-surface-900 dark:text-surface-0 font-medium mb-2 block"
                >Username</label
              >
              <InputText
                :disabled="loading"
                autofocus
                id="username"
                v-model="username"
                type="text"
                placeholder="Username"
                class="w-full mb-4"
              />

              <label
                for="password"
                class="text-surface-900 dark:text-surface-0 font-medium mb-2 block"
                >Password</label
              >
              <InputText
                :disabled="loading"
                id="password"
                v-model="password"
                type="password"
                placehoder="Password"
                class="w-full mb-4"
              />

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
                @click="login"
              />
              <Message v-if="error" class="mt-2" severity="error">{{
                error
              }}</Message>
            </div>
          </div>
          <div v-else>
            <p>Already authenticated!</p>
            <Button
              label="Logout"
              icon="pi pi-user"
              class="w-full"
              @click="logout"
            />
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { inject, ref, type Ref } from 'vue'

const authenticated = inject<Ref<boolean>>('authenticated')
const csrf = ref('')
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

getSession()

function setAuthenticated(auth: boolean) {
  if (authenticated) authenticated.value = auth
}

function getCSRF() {
  fetch('http://localhost:8000/api/csrf/', {
    credentials: 'include',
  })
    .then(res => {
      const csrfToken = res.headers.get('X-CSRFToken')
      if (csrfToken) {
        csrf.value = csrfToken
        console.log(csrfToken)
      }
    })
    .catch(err => {
      console.log(err)
    })
}

function getSession() {
  fetch('http://localhost:8000/api/session/', {
    credentials: 'include',
  })
    .then(res => res.json())
    .then(data => {
      console.log(data)
      setAuthenticated(data.isAuthenticated)
      if (!data.isAuthenticated) getCSRF()
    })
    .catch(err => {
      console.log(err)
    })
}

function isResponseOk(response: Response) {
  if (response.status >= 200 && response.status <= 299) {
    return response.json()
  } else {
    throw Error(response.statusText)
  }
}

function login() {
  loading.value = true
  fetch('http://localhost:8000/api/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf.value,
    },
    credentials: 'include',
    body: JSON.stringify({
      username: username.value,
      password: password.value,
    }),
  })
    .then(isResponseOk)
    .then(() => {
      username.value = ''
      password.value = ''
      error.value = ''
      setAuthenticated(true)
      loading.value = false
    })
    .catch(err => {
      console.log(err)
      error.value = 'Wrong username or password.'
      loading.value = false
    })
}

function logout() {
  fetch('http://localhost:8000/api/logout', {
    credentials: 'include',
  })
    .then(isResponseOk)
    .then(data => {
      console.log(data)
      setAuthenticated(false)
      getCSRF()
    })
    .catch(err => {
      console.log(err)
    })
}
</script>

<style scoped></style>
