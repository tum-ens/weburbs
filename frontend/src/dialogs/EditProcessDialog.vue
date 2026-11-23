<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    :header="'Edit Process \'' + props.process.name + '\''"
    class="w-11/12 md:w-10/12 lg:w-1/2"
  >
    <ProcessForm
      :process="process"
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
    header="Delete Process"
    :style="{ width: '450px' }"
    :closable="false"
  >
    <div class="flex items-center space-x-3 mb-4">
      <i class="pi pi-exclamation-triangle text-red-500 text-2xl"></i>
      <span class="text-lg">
        Are you sure you want to delete the process
        <strong>"{{ props.process.name }}"</strong>?
      </span>
    </div>
    <p class="text-gray-600 mb-4">
      This action cannot be undone. All data associated with this process will
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
import ProcessForm from '@/forms/ProcessForm.vue'
import type { Process } from '@/backend/interfaces'
import { useDeleteProcess, useUpdateProcess } from '@/backend/processes'
import { useRoute, useRouter } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'
import { watch, ref } from 'vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
  process: Process
  from_energy_diagram?: boolean
}>()

// Watch for dialog close and navigate back to energy diagram if needed
watch(visible, (newValue, oldValue) => {
  if (oldValue === true && newValue === false && props.from_energy_diagram) {
    console.log('Navigating back to energy diagram from process edit')
    router.push({
      name: 'ProjectEnergyDiagram',
      params: { proj: route.params.proj },
      query: { site: props.site_name },
    })
  }
})

const showDeleteDialog = ref(false)

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
        showDeleteDialog.value = false
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
