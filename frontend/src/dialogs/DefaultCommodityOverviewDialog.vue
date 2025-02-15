<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Default Commodities"
    class="w-11/12 md:w-10/12 xl:w-1/2 min-h-96"
  >
    <div
      v-if="def_commodities?.length"
      class="grid grid-cols-[repeat(auto-fit,minmax(16rem,1fr))] gap-3"
    >
      <template v-for="def_com in def_commodities" :key="def_com.name">
        <Transformer
          :title="def_com.name"
          :description="commodityTypeToName(def_com.type)"
          :in="[]"
          :out="[]"
          @click="() => add(def_com.name)"
        />
      </template>
    </div>
    <div v-else>
      <span>No default commodity defined</span>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import Transformer from '@/components/TransformerComponent.vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import type { AxiosError } from 'axios'
import { useAddDefCommodity, useDefCommodities } from '@/backend/commodities'
import { commodityTypeToName } from '@/backend/interfaces'

const toast = useToast()
const route = useRoute()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
}>()

const { data: def_commodities } = useDefCommodities()
const { mutate: addDefCommodity } = useAddDefCommodity(route)

function add(def_com_name: string) {
  visible.value = false
  addDefCommodity(
    { site_name: props.site_name, def_com_name },
    {
      onSuccess() {
        toast.add({
          summary: 'Added',
          detail: `Default has been added to site ${props.site_name}`,
          severity: 'success',
          life: 2000,
        })
      },
      onError(error) {
        toast.add({
          summary: 'Error adding',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when adding ${def_com_name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
