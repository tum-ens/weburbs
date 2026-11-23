<template>
  <DefaultLayout>
    <Card>
      <template #title>
        <div class="flex items-center justify-between gap-3">
          <span>User approvals</span>
          <Button
            severity="secondary"
            icon="pi pi-refresh"
            label="Refresh"
            :loading="loading"
            @click="refresh()"
          />
        </div>
      </template>
      <template #content>
        <div
          v-if="!authenticated"
          class="text-surface-600 dark:text-surface-300"
        >
          Please log in first.
        </div>

        <div
          v-else-if="!isAdmin"
          class="text-surface-600 dark:text-surface-300"
        >
          You don’t have permission to view this page.
        </div>

        <div v-else>
          <div class="flex flex-col gap-3">
            <div class="flex flex-col md:flex-row md:items-center gap-2">
              <div class="flex gap-2">
                <Button
                  :severity="status === 'pending' ? 'primary' : 'secondary'"
                  label="Pending"
                  @click="setStatus('pending')"
                />
                <Button
                  :severity="status === 'approved' ? 'primary' : 'secondary'"
                  label="Approved"
                  @click="setStatus('approved')"
                />
                <Button
                  :severity="status === 'rejected' ? 'primary' : 'secondary'"
                  label="Rejected"
                  @click="setStatus('rejected')"
                />
              </div>

              <div class="flex-1" />

              <div class="flex gap-2 items-center">
                <Button
                  :severity="status === 'unverified' ? 'primary' : 'secondary'"
                  label="Email unverified"
                  @click="setStatus('unverified')"
                />
                <InputText
                  v-model="searchInput"
                  placeholder="Search username or email"
                  :disabled="loading"
                  class="w-full md:w-80"
                  @keydown.enter="applySearch"
                />
                <Button
                  severity="secondary"
                  icon="pi pi-search"
                  label="Search"
                  :disabled="loading"
                  @click="applySearch"
                />
                <Button
                  v-if="search"
                  severity="secondary"
                  icon="pi pi-times"
                  label="Clear"
                  :disabled="loading"
                  @click="clearSearch"
                />
              </div>
            </div>

            <div v-if="error" class="text-red-500">Failed to load users.</div>
            <div
              v-else-if="loading"
              class="text-surface-600 dark:text-surface-300"
            >
              Loading…
            </div>
            <div
              v-else-if="!users?.length"
              class="text-surface-600 dark:text-surface-300"
            >
              No users found.
            </div>

            <div v-else class="flex flex-col gap-2">
              <div
                v-for="u in users"
                :key="u.username"
                class="flex flex-col md:flex-row md:items-center md:justify-between gap-2 p-3 border rounded border-surface-200 dark:border-surface-800"
              >
                <div class="flex flex-col">
                  <span class="font-semibold flex items-center gap-2">
                    <span
                      v-if="status === 'approved' && u.is_online"
                      class="inline-block w-2.5 h-2.5 rounded-full bg-blue-500 shrink-0"
                      title="Online now"
                    />
                    <span
                      v-if="
                        status === 'approved' &&
                        runningForUser(u.username).length
                      "
                      class="inline-block w-2.5 h-2.5 rounded-full bg-green-500 shrink-0"
                      title="Simulation running"
                    />
                    {{ u.username }}
                  </span>
                  <span
                    class="text-sm text-surface-600 dark:text-surface-300"
                    >{{ u.email }}</span
                  >
                  <span
                    v-if="
                      status === 'approved' && !u.is_online && u.last_seen_at
                    "
                    class="text-xs text-surface-500 dark:text-surface-400"
                  >
                    Last seen {{ formatDateTime(u.last_seen_at) }}
                  </span>
                  <span
                    v-else-if="
                      status === 'approved' && !u.is_online && !u.last_seen_at
                    "
                    class="text-xs text-surface-500 dark:text-surface-400"
                  >
                    Last seen: never
                  </span>
                  <div
                    v-if="
                      status === 'approved' && runningForUser(u.username).length
                    "
                    class="flex flex-col gap-1 mt-1"
                  >
                    <div
                      v-for="sim in runningForUser(u.username)"
                      :key="sim.id"
                      class="flex flex-wrap items-center gap-2 text-xs text-surface-500 dark:text-surface-400"
                    >
                      <span>Simulating project “{{ sim.project }}”</span>
                      <Button
                        size="small"
                        severity="danger"
                        icon="pi pi-stop-circle"
                        label="Stop simulation"
                        outlined
                        :loading="stopSimPending && stopSimId === sim.id"
                        @click="adminStopSimulation(sim.id, u.username)"
                      />
                    </div>
                  </div>
                  <span
                    v-if="status === 'rejected' && u.rejected_at"
                    class="text-xs text-surface-500 dark:text-surface-400"
                  >
                    Rejected {{ formatDateTime(u.rejected_at) }} · removed
                    automatically after 30 days
                  </span>
                  <span
                    v-if="status === 'unverified'"
                    class="text-xs text-surface-500 dark:text-surface-400"
                  >
                    Registered {{ formatDateTime(u.date_joined) }}
                    <template v-if="u.token_date">
                      · verification email sent
                      {{ formatDateTime(u.token_date) }}
                    </template>
                    · removed automatically after 30 days
                  </span>
                </div>

                <div v-if="status === 'pending'" class="flex gap-2">
                  <Button
                    severity="success"
                    icon="pi pi-check"
                    label="Approve"
                    :loading="approvePending && approveUserName === u.username"
                    @click="approve(u.username)"
                  />
                  <Button
                    severity="danger"
                    icon="pi pi-times"
                    label="Reject"
                    :loading="rejectPending && rejectUserName === u.username"
                    @click="reject(u.username)"
                  />
                </div>
                <div v-else-if="status === 'approved'" class="flex gap-2">
                  <Button
                    severity="danger"
                    icon="pi pi-user-minus"
                    label="Remove"
                    :loading="rejectPending && rejectUserName === u.username"
                    @click="reject(u.username)"
                  />
                </div>
                <div v-else-if="status === 'unverified'" class="flex gap-2">
                  <Button
                    severity="danger"
                    icon="pi pi-trash"
                    label="Delete permanently"
                    outlined
                    :loading="deletePending && deleteUserName === u.username"
                    @click="confirmDelete(u.username)"
                  />
                </div>
                <div
                  v-else-if="status === 'rejected'"
                  class="flex gap-2 flex-wrap"
                >
                  <Button
                    severity="success"
                    icon="pi pi-user-plus"
                    label="Add"
                    :loading="approvePending && approveUserName === u.username"
                    @click="approve(u.username)"
                  />
                  <Button
                    severity="danger"
                    icon="pi pi-trash"
                    label="Delete permanently"
                    outlined
                    :loading="deletePending && deleteUserName === u.username"
                    @click="confirmDelete(u.username)"
                  />
                </div>
              </div>
            </div>

            <div
              class="flex items-center justify-between gap-2 pt-2 border-t border-surface-200 dark:border-surface-800"
            >
              <span class="text-sm text-surface-600 dark:text-surface-300">
                {{ totalLabel }}
              </span>
              <div class="flex gap-2 items-center">
                <Button
                  severity="secondary"
                  label="Previous"
                  icon="pi pi-angle-left"
                  :disabled="loading || page <= 1"
                  @click="prevPage"
                />
                <span class="text-sm text-surface-600 dark:text-surface-300">
                  Page {{ page }} / {{ totalPages }}
                </span>
                <Button
                  severity="secondary"
                  label="Next"
                  icon="pi pi-angle-right"
                  iconPos="right"
                  :disabled="loading || page >= totalPages"
                  @click="nextPage"
                />
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>
    <ConfirmDialog group="admin-delete" />
  </DefaultLayout>
</template>

<script setup lang="ts">
import DefaultLayout from '@/layout/DefaultLayout.vue'
import {
  useApproveUser,
  useAuthenticated,
  fetchUsers,
  fetchRunningSimulations,
  useMe,
  type PendingUser,
  type RunningSimulationInfo,
  type UserListStatus,
  useAdminStopSimulation,
  useDeleteUserPermanently,
  useRejectUser,
} from '@/backend/security'
import { computed, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const confirm = useConfirm()
const router = useRouter()
const route = useRoute()

const { data: authenticated } = useAuthenticated()
const { data: me } = useMe()

watch(
  authenticated,
  () => {
    if (authenticated.value === false) {
      router.push({
        name: 'Login',
        query: {
          redirect: route.fullPath,
        },
      })
    }
  },
  { immediate: true },
)

const isAdmin = computed(() => !!me.value?.isStaff || !!me.value?.isSuperuser)

const status = ref<UserListStatus>('pending')
const page = ref(1)
const pageSize = 50
const total = ref(0)
const totalPages = ref(1)

const search = ref('')
const searchInput = ref('')

const users = ref<PendingUser[] | null>(null)
const loading = ref(false)
const error = ref(false)

const { mutateAsync: approveMutate, isPending: approvePending } =
  useApproveUser()
const { mutateAsync: rejectMutate, isPending: rejectPending } = useRejectUser()
const { mutateAsync: deleteMutate, isPending: deletePending } =
  useDeleteUserPermanently()
const { mutateAsync: adminStopMutate, isPending: stopSimPending } =
  useAdminStopSimulation()

const approveUserName = ref<string | null>(null)
const rejectUserName = ref<string | null>(null)
const deleteUserName = ref<string | null>(null)
const stopSimId = ref<string | null>(null)

const runningByUser = ref<Record<string, RunningSimulationInfo[]>>({})
let runningPoll: ReturnType<typeof setInterval> | null = null

const totalLabel = computed(() => `${total.value} users`)

function runningForUser(username: string) {
  return runningByUser.value[username] ?? []
}

async function loadRunningSimulations() {
  if (!authenticated.value || !isAdmin.value || status.value !== 'approved')
    return
  try {
    runningByUser.value = await fetchRunningSimulations()
  } catch {
    runningByUser.value = {}
  }
}

async function refreshApprovedStatus() {
  if (!authenticated.value || !isAdmin.value || status.value !== 'approved')
    return
  try {
    const res = await fetchUsers(
      status.value,
      page.value,
      search.value,
      pageSize,
    )
    users.value = res.results
  } catch {
    // keep existing list on transient errors
  }
}

function setupRunningPoll() {
  if (runningPoll) {
    clearInterval(runningPoll)
    runningPoll = null
  }
  if (status.value === 'approved' && authenticated.value && isAdmin.value) {
    loadRunningSimulations()
    refreshApprovedStatus()
    runningPoll = setInterval(() => {
      loadRunningSimulations()
      refreshApprovedStatus()
    }, 5000)
  } else {
    runningByUser.value = {}
  }
}

async function load() {
  if (!authenticated.value || !isAdmin.value) return
  loading.value = true
  error.value = false
  try {
    const res = await fetchUsers(
      status.value,
      page.value,
      search.value,
      pageSize,
    )
    users.value = res.results
    total.value = res.total
    totalPages.value = res.total_pages || 1
    page.value = res.page
  } catch {
    error.value = true
    users.value = []
    total.value = 0
    totalPages.value = 1
  } finally {
    loading.value = false
  }
}

watch([authenticated, isAdmin], () => {
  load()
  setupRunningPoll()
})

watch(status, () => {
  setupRunningPoll()
})

onUnmounted(() => {
  if (runningPoll) clearInterval(runningPoll)
})

async function approve(username: string) {
  approveUserName.value = username
  try {
    await approveMutate(username)
    await load()
    toast.add({
      severity: 'success',
      summary: 'Approved',
      detail: username,
      life: 2000,
    })
  } catch (e: unknown) {
    const detail =
      typeof e === 'object' &&
      e !== null &&
      'response' in e &&
      typeof (e as { response?: { data?: { detail?: string } } }).response?.data
        ?.detail === 'string'
        ? (e as { response: { data: { detail: string } } }).response.data.detail
        : username
    toast.add({
      severity: 'error',
      summary: 'Approve failed',
      detail,
      life: 5000,
    })
  } finally {
    approveUserName.value = null
  }
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString()
}

function confirmDelete(username: string) {
  confirm.require({
    group: 'admin-delete',
    message: `Permanently delete "${username}"? All account data will be removed and cannot be undone.`,
    header: 'Delete permanently',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: { label: 'Cancel' },
    acceptProps: {
      label: 'Delete permanently',
      severity: 'danger',
    },
    accept: async () => {
      await deletePermanently(username)
    },
  })
}

async function deletePermanently(username: string) {
  deleteUserName.value = username
  try {
    await deleteMutate(username)
    await load()
    toast.add({
      severity: 'success',
      summary: 'Deleted',
      detail: `${username} was permanently removed`,
      life: 3000,
    })
  } catch (e: unknown) {
    const detail =
      typeof e === 'object' &&
      e !== null &&
      'response' in e &&
      typeof (e as { response?: { data?: { detail?: string } } }).response?.data
        ?.detail === 'string'
        ? (e as { response: { data: { detail: string } } }).response.data.detail
        : username
    toast.add({
      severity: 'error',
      summary: 'Delete failed',
      detail,
      life: 5000,
    })
  } finally {
    deleteUserName.value = null
  }
}

async function reject(username: string) {
  rejectUserName.value = username
  try {
    await rejectMutate(username)
    await load()
    toast.add({
      severity: 'warn',
      summary: 'Rejected',
      detail: username,
      life: 2000,
    })
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Reject failed',
      detail: username,
      life: 3000,
    })
  } finally {
    rejectUserName.value = null
  }
}

function refresh() {
  load()
  loadRunningSimulations()
}

async function adminStopSimulation(simId: string, username: string) {
  stopSimId.value = simId
  try {
    await adminStopMutate(simId)
    await loadRunningSimulations()
    toast.add({
      severity: 'warn',
      summary: 'Simulation stopped',
      detail: `${username} — project run cancelled`,
      life: 3000,
    })
  } catch (e: unknown) {
    const detail =
      typeof e === 'object' &&
      e !== null &&
      'response' in e &&
      typeof (e as { response?: { data?: { detail?: string } } }).response?.data
        ?.detail === 'string'
        ? (e as { response: { data: { detail: string } } }).response.data.detail
        : 'Could not stop simulation'
    toast.add({
      severity: 'error',
      summary: 'Stop failed',
      detail,
      life: 4000,
    })
  } finally {
    stopSimId.value = null
  }
}

function setStatus(s: UserListStatus) {
  status.value = s
  page.value = 1
  load()
}

function applySearch() {
  search.value = searchInput.value.trim()
  page.value = 1
  load()
}

function clearSearch() {
  search.value = ''
  searchInput.value = ''
  page.value = 1
  load()
}

function nextPage() {
  if (page.value < totalPages.value) {
    page.value += 1
    load()
  }
}

function prevPage() {
  if (page.value > 1) {
    page.value -= 1
    load()
  }
}
</script>
