import {
  QueryClient,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/vue-query'
import axios, { type AxiosResponse } from 'axios'
import { onUnmounted, watch } from 'vue'

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
        .get<{ isAuthenticated: boolean }>('/api/security/session/')
        .then(res => res.data.isAuthenticated),
  })
}

export function usePresenceHeartbeat() {
  const { data: authenticated } = useAuthenticated()
  const { data: csrf, isSuccess: csrfReady } = useCSRF()

  let intervalId: ReturnType<typeof setInterval> | undefined

  const ping = () => {
    if (!authenticated.value || !csrf.value) return
    axios
      .post(
        '/api/security/presence/',
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      )
      .catch(() => {})
  }

  watch(
    [authenticated, csrfReady],
    () => {
      if (intervalId) {
        clearInterval(intervalId)
        intervalId = undefined
      }
      if (!authenticated.value || !csrfReady.value) return
      ping()
      intervalId = setInterval(ping, 60_000)
    },
    { immediate: true },
  )

  onUnmounted(() => {
    if (intervalId) clearInterval(intervalId)
  })
}

export type MeResponse = {
  isAuthenticated: true
  username: string
  email: string
  isStaff: boolean
  isSuperuser: boolean
}

export function useMe() {
  return useQuery({
    queryKey: ['me'],
    queryFn: () =>
      axios.get<MeResponse>('/api/security/me/').then(res => res.data),
    retry: false,
  })
}

export type PendingUser = {
  username: string
  email: string
  date_joined: string
  is_active: boolean
  rejected_at?: string
  token_date?: string
  is_online?: boolean
  last_seen_at?: string
}

export function usePendingUsers() {
  return useQuery({
    queryKey: ['pendingUsers'],
    queryFn: () =>
      axios
        .get<{ pending: PendingUser[] }>('/api/security/pending/')
        .then(res => res.data.pending),
  })
}

export type UserListStatus = 'pending' | 'unverified' | 'approved' | 'rejected'

export type UserListResponse = {
  results: PendingUser[]
  page: number
  page_size: number
  total: number
  total_pages: number
  status: UserListStatus
  search: string
}

export async function fetchUsers(
  status: UserListStatus,
  page: number,
  search: string,
  pageSize = 50,
) {
  return axios
    .get<UserListResponse>('/api/security/users/', {
      params: {
        status,
        page,
        page_size: pageSize,
        search,
      },
    })
    .then(res => res.data)
}

export function useApproveUser() {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (username: string) =>
      axios.post(
        `/api/security/approve/${encodeURIComponent(username)}/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    async onSuccess() {
      await client.invalidateQueries({ queryKey: ['pendingUsers'] })
    },
  })
}

export function useRejectUser() {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (username: string) =>
      axios.post(
        `/api/security/reject/${encodeURIComponent(username)}/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    async onSuccess() {
      await client.invalidateQueries({ queryKey: ['pendingUsers'] })
    },
  })
}

export function useDeleteUserPermanently() {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (username: string) =>
      axios.post(
        `/api/security/delete/${encodeURIComponent(username)}/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    async onSuccess() {
      await client.invalidateQueries({ queryKey: ['pendingUsers'] })
    },
  })
}

export type RunningSimulationInfo = {
  id: string
  project: string
  timestamp: string
}

export async function fetchRunningSimulations() {
  return axios
    .get<{
      by_user: Record<string, RunningSimulationInfo[]>
    }>('/api/security/running_simulations/')
    .then(res => res.data.by_user)
}

export function useAdminStopSimulation() {
  const { data: csrf } = useCSRF()
  return useMutation({
    mutationFn: (simId: string) =>
      axios.post(
        `/api/security/running_simulations/${simId}/stop/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
  })
}

function isResponseOk(response: AxiosResponse) {
  if (response.status >= 200 && response.status <= 299) {
    return response.data
  } else {
    throw Error(response.statusText)
  }
}

export type LoginResult =
  | true
  | 'verification'
  | 'approval'
  | { ok: false; detail: string }

export async function login(
  queryClient: QueryClient,
  csrf: string,
  username: string,
  password: string,
): Promise<LoginResult> {
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
    .then(async (): Promise<LoginResult> => {
      await queryClient.invalidateQueries({ queryKey: ['authenticated'] })
      await queryClient.invalidateQueries({ queryKey: ['me'] })
      return true
    })
    .catch(err => {
      const status = err.response?.status
      const detail = err.response?.data?.detail
      if (status === 406) return 'verification'
      if (status === 403) return 'approval'
      if (typeof detail === 'string' && detail)
        return { ok: false as const, detail }
      return { ok: false as const, detail: '' }
    })
}

export async function logout(queryClient: QueryClient) {
  return axios
    .get('/api/security/logout/')
    .then(isResponseOk)
    .then(async () => {
      await queryClient.invalidateQueries({ queryKey: ['authenticated'] })
      await queryClient.invalidateQueries({ queryKey: ['me'] })
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

export async function request_password_reset(csrf: string, email: string) {
  return axios
    .post(
      '/api/security/request_password_reset/',
      { email },
      {
        headers: {
          'X-CSRFToken': csrf,
        },
      },
    )
    .then(isResponseOk)
}

export async function reset_password(
  csrf: string,
  username: string,
  token: string,
  password: string,
) {
  return axios
    .post(
      `/api/security/reset_password/${username}/${token}/`,
      { password },
      {
        headers: {
          'X-CSRFToken': csrf,
        },
      },
    )
    .then(isResponseOk)
}
