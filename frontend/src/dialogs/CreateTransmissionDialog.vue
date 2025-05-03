<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Create storage"
    class="w-11/12 md:w-10/12 xl:w-1/2 min-h-96"
  >
    <TransmissionForm
      submit-label="Create"
      :loading="loading"
      @submit="update"
    />
  </Dialog>
</template>

<script setup lang="ts">
import type { Transmission } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'
import TransmissionForm from '@/forms/TransmissionForm.vue'
import { useUpdateTransmission } from '@/backend/transmission'

const route = useRoute()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })

const { mutate: updateTransmission, isPending: loading } =
  useUpdateTransmission(route)

function update(transmission: Transmission): void {
  updateTransmission(
    {
      sitein_name: transmission.sitein,
      siteout_name: transmission.siteout,
      com_name: transmission.commodity,
      transmission: transmission,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Added',
          detail: `Transmission between ${transmission.sitein} and ${transmission.siteout} with commodity ${transmission.commodity} has been created`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error adding',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when creating transmission between ${transmission.sitein} and ${transmission.siteout} with commodity ${transmission.commodity}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
