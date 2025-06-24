<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Create Commodity"
    class="w-11/12 md:w-10/12 xl:w-1/2"
  >
    <CommodityForm
      submit-label="Create"
      :loading="loading"
      @submit="update"
      :site_name="site_name"
    />
  </Dialog>
</template>

<script setup lang="ts">
import type { Commodity } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import type { AxiosError } from 'axios'
import { useToast } from 'primevue/usetoast'
import { useUpdateCommodity } from '@/backend/commodities'
import CommodityForm from '@/forms/CommodityForm.vue'

const route = useRoute()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
}>()

const { mutate: updateCommodity, isPending: loading } =
  useUpdateCommodity(route)

function update(commodity: Commodity): void {
  updateCommodity(
    {
      site_name: props.site_name,
      commodity_name: commodity.name,
      commodity,
    },
    {
      onSuccess() {
        visible.value = false
        toast.add({
          summary: 'Added',
          detail: `Commodity ${commodity.name} has been created`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error adding',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when creating ${commodity.name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
