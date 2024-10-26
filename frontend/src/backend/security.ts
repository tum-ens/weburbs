import { QueryClient, useQuery } from '@tanstack/vue-query'
import axios, { type AxiosResponse } from 'axios'

export function useCSRF() {
  return useQuery({
    queryKey: ['csrftoken'],
    queryFn: () =>
      axios.get('/api/csrf').then(res => res.headers['x-csrftoken']),
  })
}

export function useAuthenticated() {
  return useQuery({
    queryKey: ['authenticated'],
    queryFn: () =>
      axios
        .get('/api/session/')
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
      '/api/login/',
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
    .catch(() => {
      return false
    })
}

export async function logout(queryClient: QueryClient) {
  return axios
    .get('/api/logout')
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
