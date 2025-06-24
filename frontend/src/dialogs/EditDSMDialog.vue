<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Edit DSM"
    class="w-11/12 md:w-10/12 lg:w-1/2"
  >
    <DSMForm
      :dsm="dsm"
      :site_name="props.site_name"
      submit-label="Update"
      :loading="loading || deleting"
      @submit="update"
      delete
      @onDelete="deleteDsm"
    />
  </Dialog>
</template>

<script setup lang="ts">
import type { DSM } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'
import DSMForm from '@/forms/DSMForm.vue'
import { useDeleteDSM, useUpdateDSM } from '@/backend/dsm'

const route = useRoute()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
  dsm: DSM
}>()

const { mutate: updateDSM, isPending: loading } = useUpdateDSM(route)
const { mutate: deleteDSM, isPending: deleting } = useDeleteDSM(route)

function update(dsm: DSM): void {
  updateDSM(
    {
      site_name: props.site_name,
      com_name: props.dsm.commodity,
      dsm: dsm,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Added',
          detail: `DSM for commodity ${dsm.commodity} has been updated`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error adding',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when updating DSM for commodity ${dsm.commodity}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}

function deleteDsm(): void {
  deleteDSM(
    {
      site_name: props.site_name,
      com_name: props.dsm.commodity,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Deleted',
          detail: `DSM has been deleted`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error deleted',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when deleting DSM`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
