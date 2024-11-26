<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    :header="'Edit \'' + props.process.name + '\''"
    class="w-11/12 md:w-10/12 lg:w-1/2"
  >
    <ProcessForm
      :process="process"
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
import ProcessForm from '@/forms/ProcessForm.vue'
import type { Process } from '@/backend/interfaces'
import { useDeleteProcess, useUpdateProcess } from '@/backend/processes'
import { useRoute } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'

const route = useRoute()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
  process: Process
}>()

const { mutate: updateProcess, isPending: loading } = useUpdateProcess(route)
const { mutate: deleteProcess, isPending: deleting } = useDeleteProcess(route)

function update(process: Process): void {
  updateProcess(
    {
      site_name: props.site_name,
      process_name: props.process.name,
      process,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Added',
          detail: `Process ${process.name} has been updated`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error adding',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when updating ${process.name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}

function deleteProc(): void {
  deleteProcess(
    {
      site_name: props.site_name,
      process_name: props.process.name,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Deleted',
          detail: `Process ${props.process.name} has been deleted`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error deleted',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when deleting ${props.process.name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
