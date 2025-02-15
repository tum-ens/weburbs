<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Default Processes"
    class="w-11/12 md:w-10/12 xl:w-1/2 min-h-96"
  >
    <div
      v-if="def_processes?.length"
      class="grid grid-cols-[repeat(auto-fit,minmax(16rem,1fr))] gap-3"
    >
      <template v-for="def_proc in def_processes" :key="def_proc.name">
        <Transformer
          v-if="
            (def_proc.in.length !== 0 && def_proc.out.length !== 0) || advanced
          "
          :title="def_proc.name"
          :description="def_proc.description"
          :in="def_proc.in.map(proccom => proccom.name)"
          :out="def_proc.out.map(proccom => proccom.name)"
          @click="() => add(def_proc.name)"
        />
      </template>
    </div>
    <div v-else>
      <span>No default processes defined</span>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import Transformer from '@/components/TransformerComponent.vue'
import { useAddDefProcess, useDefProcesses } from '@/backend/processes'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import type { AxiosError } from 'axios'
import { inject } from 'vue'

const toast = useToast()
const route = useRoute()

const advanced = inject('advanced')

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
}>()

const { data: def_processes } = useDefProcesses()
const { mutate: addDefProcess } = useAddDefProcess(route)

function add(def_proc_name: string) {
  visible.value = false
  addDefProcess(
    { site_name: props.site_name, def_proc_name },
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
            `An error occurred when adding ${def_proc_name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
