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
      @onDelete="deleteCom"
    />
  </Dialog>
</template>

<script setup lang="ts">
import type { Commodity } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'
import { useDeleteCommodity, useUpdateCommodity } from '@/backend/commodities'
import CommodityForm from '@/forms/CommodityForm.vue'

const route = useRoute()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
  commodity: Commodity
}>()

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
