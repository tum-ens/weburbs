<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Create process"
    class="w-11/12 md:w-10/12 xl:w-1/2 min-h-96"
  >
    <ProcessForm
      submit-label="Create"
      :loading="loading"
      @submit="update"
      :site_name="site_name"
    />
  </Dialog>
</template>

<script setup lang="ts">
import type { Process } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'
import ProcessForm from '@/forms/ProcessForm.vue'
import { useUpdateProcess } from '@/backend/processes'

const route = useRoute()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
}>()

const { mutate: updateProcess, isPending: loading } = useUpdateProcess(route)

function update(process: Process): void {
  updateProcess(
    {
      site_name: props.site_name,
      process_name: process.name,
      process: process,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Added',
          detail: `Commodity ${process.name} has been created`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error adding',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when creating ${process.name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
