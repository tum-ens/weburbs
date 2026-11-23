<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    :header="'Edit Commodity \'' + props.commodity.name + '\''"
    class="w-11/12 md:w-10/12 lg:w-1/2"
  >
    <CommodityForm
      :commodity="commodity"
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
    header="Delete Commodity"
    :style="{ width: '450px' }"
    :closable="false"
  >
    <div class="flex items-center space-x-3 mb-4">
      <i class="pi pi-exclamation-triangle text-red-500 text-2xl"></i>
      <span class="text-lg">
        Are you sure you want to delete the commodity
        <strong>"{{ props.commodity.name }}"</strong>?
      </span>
    </div>
    <p class="text-gray-600 mb-4">
      This action cannot be undone. All data associated with this commodity will
      be permanently removed.
    </p>
    <template #footer>
      <Button @click="showDeleteDialog = false" text class="mr-2">
        Cancel
      </Button>
      <Button @click="deleteCom" :loading="deleting" severity="danger">
        <span v-if="deleting">Deleting...</span>
        <span v-else>Delete</span>
      </Button>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import type { Commodity } from '@/backend/interfaces'
import { useRoute, useRouter } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'
import { useDeleteCommodity, useUpdateCommodity } from '@/backend/commodities'
import CommodityForm from '@/forms/CommodityForm.vue'
import { watch, ref } from 'vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
  commodity: Commodity
  from_energy_diagram?: boolean
}>()

// Watch for dialog close and navigate back to energy diagram if needed
watch(visible, (newValue, oldValue) => {
  if (oldValue === true && newValue === false && props.from_energy_diagram) {
    console.log('Navigating back to energy diagram from commodity edit')
    router.push({
      name: 'ProjectEnergyDiagram',
      params: { proj: route.params.proj },
      query: { site: props.site_name },
    })
  }
})

const showDeleteDialog = ref(false)

const { mutate: updateCommodity, isPending: loading } =
  useUpdateCommodity(route)
const { mutate: deleteCommodity, isPending: deleting } =
  useDeleteCommodity(route)

function update(commodity: Commodity): void {
  updateCommodity(
    {
      site_name: props.site_name,
      commodity_name: props.commodity.name,
      commodity,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Added',
          detail: `Commodity ${commodity.name} has been updated`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error adding',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when updating ${commodity.name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}

function deleteCom(): void {
  deleteCommodity(
    {
      site_name: props.site_name,
      commodity_name: props.commodity.name,
    },
    {
      onSuccess() {
        showDeleteDialog.value = false
        visible.value = false
        toast.add({
          summary: 'Deleted',
          detail: `Commodity ${props.commodity.name} has been deleted`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error deleted',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when deleting ${props.commodity.name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
