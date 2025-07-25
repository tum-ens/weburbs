import { QueryClient, useQuery } from '@tanstack/vue-query'
import axios, { type AxiosResponse } from 'axios'

export function useCSRF() {
  return useQuery({
    queryKey: ['csrftoken'],
    queryFn: () =>
      axios.get('/api/security/csrf/').then(res => res.headers['x-csrftoken']),
  })
}

export function useAuthenticated() {
  return useQuery({
    queryKey: ['authenticated'],
    queryFn: () =>
      axios
        .get('/api/security/session/')
        .then<{ isAuthenticated: boolean }>(res => res.data.isAuthenticated),
  })
}

function isResponseOk(response: AxiosResponse) {
  if (response.status >= 200 && response.status <= 299) {
    return response.data
  } else {
    throw Error(response.statusText)
  }
}

export async function login(
  queryClient: QueryClient,
  csrf: string,
  username: string,
  password: string,
) {
  return axios
    .post(
      '/api/security/login/',
      { username, password },
      {
        headers: {
          'X-CSRFToken': csrf,
        },
      },
    )
    .then(isResponseOk)
    .then(async () => {
      await queryClient.invalidateQueries({ queryKey: ['authenticated'] })
      return true
    })
    .catch(response => {
      if (response.response.status === 406) return 'verification'
      return false
    })
}

export async function logout(queryClient: QueryClient) {
  return axios
    .get('/api/security/logout/')
    .then(isResponseOk)
    .then(async () => {
      await queryClient.invalidateQueries({ queryKey: ['authenticated'] })
      return true
    })
    .catch(err => {
      console.log(err)
      return false
    })
}

export async function register(
  csrf: string,
  username: string,
  email: string,
  password: string,
) {
  return axios
    .post(
      '/api/security/register/',
      { username, email, password },
      {
        headers: {
          'X-CSRFToken': csrf,
        },
      },
    )
    .then(isResponseOk)
}

export async function verify_mail(
  csrf: string,
  username: string,
  token: string,
) {
  return axios
    .post(
      `/api/security/verify_mail/${username}/${token}/`,
      {},
      {
        headers: {
          'X-CSRFToken': csrf,
        },
      },
    )
    .then(isResponseOk)
}

export async function resend_token(csrf: string, username: string) {
  return axios
    .post(
      `/api/security/resend_token/${username}/`,
      {},
      {
        headers: {
          'X-CSRFToken': csrf,
        },
      },
    )
    .then(isResponseOk)
}
