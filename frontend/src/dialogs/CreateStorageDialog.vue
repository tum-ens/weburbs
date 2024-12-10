<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Create storage"
    class="w-11/12 md:w-10/12 xl:w-1/2 min-h-96"
  >
    <StorageForm
      submit-label="Create"
      :loading="loading"
      @submit="update"
      :site_name="site_name"
    />
  </Dialog>
</template>

<script setup lang="ts">
import type { Storage } from '@/backend/interfaces'
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
}>()

const { mutate: updateStorage, isPending: loading } = useUpdateStorage(route)

function update(storage: Storage): void {
  updateStorage(
    {
      site_name: props.site_name,
      storage_name: storage.name,
      storage: storage,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Added',
          detail: `Storage ${storage.name} has been created`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error adding',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when creating ${storage.name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
