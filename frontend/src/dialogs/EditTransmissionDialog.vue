<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Edit Transmission"
    class="w-11/12 md:w-10/12 lg:w-1/2"
  >
    <TransmissionForm
      :transmission="transmission"
      submit-label="Update"
      :loading="loading || deleting"
      @submit="update"
      delete
      @onDelete="showDeleteDialog = true"
    />
  </Dialog>

  <!-- Delete Confirmation Dialog -->
  <Dialog
    v-model:visible="showDeleteDialog"
    modal
    header="Delete Transmission"
    :style="{ width: '450px' }"
    :closable="false"
  >
    <div class="flex items-center space-x-3 mb-4">
      <i class="pi pi-exclamation-triangle text-red-500 text-2xl"></i>
      <span class="text-lg">
        Are you sure you want to delete the transmission from
        <strong>"{{ props.transmission.sitein }}"</strong> to
        <strong>"{{ props.transmission.siteout }}"</strong> for commodity
        <strong>"{{ props.transmission.commodity }}"</strong>?
      </span>
    </div>
    <p class="text-gray-600 mb-4">
      This action cannot be undone. All data associated with this transmission
      will be permanently removed.
    </p>
    <template #footer>
      <Button @click="showDeleteDialog = false" text class="mr-2">
        Cancel
      </Button>
      <Button @click="deleteTrans" :loading="deleting" severity="danger">
        <span v-if="deleting">Deleting...</span>
        <span v-else>Delete</span>
      </Button>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import type { Transmission } from '@/backend/interfaces'
import { useRoute, useRouter } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'
import TransmissionForm from '@/forms/TransmissionForm.vue'
import {
  useDeleteTransmission,
  useUpdateTransmission,
} from '@/backend/transmission'
import { watch, ref } from 'vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  transmission: Transmission
  from_energy_diagram?: boolean
}>()

// Watch for dialog close and navigate back to energy diagram if needed
watch(visible, (newValue, oldValue) => {
  if (oldValue === true && newValue === false && props.from_energy_diagram) {
    console.log('Navigating back to energy diagram from transmission edit')
    // Get the site from the route query (passed from the config page)
    const siteName = route.query.site as string
    router.push({
      name: 'ProjectEnergyDiagram',
      params: { proj: route.params.proj },
      query: { site: siteName },
    })
  }
})

const showDeleteDialog = ref(false)

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

function deleteTrans(): void {
  deleteTransmission(
    {
      sitein_name: props.transmission.sitein,
      siteout_name: props.transmission.siteout,
      com_name: props.transmission.commodity,
    },
    {
      onSuccess() {
        showDeleteDialog.value = false
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
