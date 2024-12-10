<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    :header="'Edit \'' + props.storage.name + '\''"
    class="w-11/12 md:w-10/12 lg:w-1/2"
  >
    <StorageForm
      :storage="storage"
      submit-label="Update"
      :loading="loading || deleting"
      @submit="update"
      :site_name="site_name"
      delete
      @onDelete="deleteProc"
    />
  </Dialog>
</template>

<script setup lang="ts">
import type { Storage } from '@/backend/interfaces'
import { useDeleteProcess } from '@/backend/processes'
import { useRoute } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'
import StorageForm from '@/forms/StorageForm.vue'
import { useUpdateStorage } from '@/backend/storage'

const route = useRoute()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
  storage: Storage
}>()

const { mutate: updateStorage, isPending: loading } = useUpdateStorage(route)
const { mutate: deleteStorage, isPending: deleting } = useDeleteProcess(route)

function update(storage: Storage): void {
  updateStorage(
    {
      site_name: props.site_name,
      storage_name: props.storage.name,
      storage: storage,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Added',
          detail: `Storage ${storage.name} has been updated`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error adding',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when updating ${storage.name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}

function deleteProc(): void {
  deleteStorage(
    {
      site_name: props.site_name,
      process_name: props.storage.name,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Deleted',
          detail: `Storage ${props.storage.name} has been deleted`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error deleted',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when deleting ${props.storage.name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
