<template>
  <template v-if="!state.isAuthenticated">
    <div>
      <label>Username</label>
      <input type="text" v-model="state.username" />
    </div>
    <div>
      <label>Password</label>
      <input type="password" v-model="state.password" />
    </div>
    <div v-if="state.error">
      {{ state.error }}
    </div>
    <button @click="login">Login</button>
  </template>
  <template v-else>
    <h1>Cookie Auth</h1>
    <p>You are logged in!</p>
    <button @click="whoami">WhoAmI</button>
    <button @click="logout">Log out</button>
  </template>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const state = reactive({
  csrf: '',
  username: '',
  password: '',
  error: '',
  isAuthenticated: false,
})

function setState(nstate) {
  if (nstate.csrf) state.csrf = nstate.csrf
  if (nstate.username) state.username = nstate.username
  if (nstate.password) state.password = nstate.password
  if (nstate.error) state.error = nstate.error
  if (nstate.isAuthenticated) state.isAuthenticated = nstate.isAuthenticated
}

getSession()

function getCSRF() {
  fetch('http://localhost:8000/api/csrf/', {
    credentials: 'include',
  })
    .then(res => {
      const csrfToken = res.headers.get('X-CSRFToken')
      setState({ csrf: csrfToken })
      console.log(csrfToken)
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
      if (data.isAuthenticated) {
        setState({ isAuthenticated: true })
      } else {
        setState({ isAuthenticated: false })
        getCSRF()
      }
    })
    .catch(err => {
      console.log(err)
    })
}

function whoami() {
  fetch('http://localhost:8000/api/whoami/', {
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  })
    .then(res => res.json())
    .then(data => {
      console.log('You are logged in as: ' + data.username)
    })
    .catch(err => {
      console.log(err)
    })
}

function isResponseOk(response) {
  if (response.status >= 200 && response.status <= 299) {
    return response.json()
  } else {
    throw Error(response.statusText)
  }
}

function login(event) {
  event.preventDefault()
  fetch('http://localhost:8000/api/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': state.csrf,
    },
    credentials: 'include',
    body: JSON.stringify({
      username: state.username,
      password: state.password,
    }),
  })
    .then(isResponseOk)
    .then(data => {
      console.log(data)
      setState({
        isAuthenticated: true,
        username: '',
        password: '',
        error: '',
      })
    })
    .catch(err => {
      console.log(err)
      setState({ error: 'Wrong username or password.' })
    })
}

function logout() {
  fetch('http://localhost:8000/api/logout', {
    credentials: 'include',
  })
    .then(isResponseOk)
    .then(data => {
      console.log(data)
      setState({ isAuthenticated: false })
      getCSRF()
    })
    .catch(err => {
      console.log(err)
    })
}
</script>

<style></style>
