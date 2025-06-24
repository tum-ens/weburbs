<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Create DSM"
    class="w-11/12 md:w-10/12 xl:w-1/2"
  >
    <DSMForm
      submit-label="Create"
      :site_name="props.site_name"
      :loading="loading"
      @submit="update"
    />
  </Dialog>
</template>

<script setup lang="ts">
import type { DSM } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'
import DSMForm from '@/forms/DSMForm.vue'
import { useUpdateDSM } from '@/backend/dsm'

const route = useRoute()
const toast = useToast()

const props = defineProps<{
  site_name: string
}>()
const visible = defineModel<boolean>('visible', { default: false })

const { mutate: updateTransmission, isPending: loading } = useUpdateDSM(route)

function update(dsm: DSM): void {
  updateTransmission(
    {
      site_name: props.site_name,
      com_name: dsm.commodity,
      dsm: dsm,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Added',
          detail: `DSM for commodity ${dsm.commodity} has been created`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error adding',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when creating DSM for commodity ${dsm.commodity}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
