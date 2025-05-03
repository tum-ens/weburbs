<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Edit transmission"
    class="w-11/12 md:w-10/12 lg:w-1/2"
  >
    <TransmissionForm
      :transmission="transmission"
      submit-label="Update"
      :loading="loading || deleting"
      @submit="update"
      delete
      @onDelete="deleteProc"
    />
  </Dialog>
</template>

<script setup lang="ts">
import type { Transmission } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'
import TransmissionForm from '@/forms/TransmissionForm.vue'
import {
  useDeleteTransmission,
  useUpdateTransmission,
} from '@/backend/transmission'

const route = useRoute()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  transmission: Transmission
}>()

const { mutate: updateTransmission, isPending: loading } =
  useUpdateTransmission(route)
const { mutate: deleteTransmission, isPending: deleting } =
  useDeleteTransmission(route)

function update(transmission: Transmission): void {
  updateTransmission(
    {
      sitein_name: props.transmission.sitein,
      siteout_name: props.transmission.siteout,
      com_name: props.transmission.commodity,
      transmission: transmission,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Added',
          detail: `Transmission has been updated`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error adding',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when updating transmission between ${transmission.sitein} and ${transmission.siteout} with commodity ${transmission.commodity}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}

function deleteProc(): void {
  deleteTransmission(
    {
      sitein_name: props.transmission.sitein,
      siteout_name: props.transmission.siteout,
      com_name: props.transmission.commodity,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Deleted',
          detail: `Transmission has been deleted`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error deleted',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when deleting transmission`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
