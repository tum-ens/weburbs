<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Default Storage"
    class="w-11/12 md:w-10/12 xl:w-1/2 min-h-96"
  >
    <div
      v-if="def_storage?.length"
      class="grid grid-cols-[repeat(auto-fit,minmax(16rem,1fr))] gap-3"
    >
      <TransformerComponent
        v-for="def_sto in def_storage"
        :key="def_sto.name"
        :title="def_sto.name"
        :description="def_sto.description"
        :in="[def_sto.commodity]"
        :out="[def_sto.commodity]"
        @click="() => add(def_sto.name)"
      />
    </div>
    <div v-else>
      <span>No default processes defined</span>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import type { AxiosError } from 'axios'
import { useAddDefStorage, useDefStorage } from '@/backend/storage'
import TransformerComponent from '@/components/TransformerComponent.vue'

const toast = useToast()
const route = useRoute()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
}>()

const { data: def_storage } = useDefStorage()
const { mutate: addDefProcess } = useAddDefStorage(route)

function add(def_storage_name: string) {
  visible.value = false
  addDefProcess(
    { site_name: props.site_name, def_storage_name },
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
            `An error occurred when adding ${def_storage_name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
