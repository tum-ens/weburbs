<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    :header="'Edit Storage \'' + props.storage.name + '\''"
    class="w-11/12 md:w-10/12 lg:w-1/2"
  >
    <StorageForm
      :storage="storage"
      submit-label="Update"
      :loading="loading || deleting"
      @submit="update"
      :site_name="site_name"
      delete
      @onDelete="showDeleteDialog = true"
    />
  </Dialog>

  <!-- Delete Confirmation Dialog -->
  <Dialog
    v-model:visible="showDeleteDialog"
    modal
    header="Delete Storage"
    :style="{ width: '450px' }"
    :closable="false"
  >
    <div class="flex items-center space-x-3 mb-4">
      <i class="pi pi-exclamation-triangle text-red-500 text-2xl"></i>
      <span class="text-lg">
        Are you sure you want to delete the storage
        <strong>"{{ props.storage.name }}"</strong>?
      </span>
    </div>
    <p class="text-gray-600 mb-4">
      This action cannot be undone. All data associated with this storage will
      be permanently removed.
    </p>
    <template #footer>
      <Button @click="showDeleteDialog = false" text class="mr-2">
        Cancel
      </Button>
      <Button @click="deleteProc" :loading="deleting" severity="danger">
        <span v-if="deleting">Deleting...</span>
        <span v-else>Delete</span>
      </Button>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import type { Storage } from '@/backend/interfaces'
import { useRoute, useRouter } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'
import StorageForm from '@/forms/StorageForm.vue'
import { useDeleteStorage, useUpdateStorage } from '@/backend/storage'
import { watch, ref } from 'vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
  storage: Storage
  from_energy_diagram?: boolean
}>()

// Watch for dialog close and navigate back to energy diagram if needed
watch(visible, (newValue, oldValue) => {
  if (oldValue === true && newValue === false && props.from_energy_diagram) {
    console.log('Navigating back to energy diagram from storage edit')
    router.push({
      name: 'ProjectEnergyDiagram',
      params: { proj: route.params.proj },
      query: { site: props.site_name },
    })
  }
})

const showDeleteDialog = ref(false)

const { mutate: updateStorage, isPending: loading } = useUpdateStorage(route)
const { mutate: deleteStorage, isPending: deleting } = useDeleteStorage(route)

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
      storage_name: props.storage.name,
    },
    {
      onSuccess() {
        showDeleteDialog.value = false
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
