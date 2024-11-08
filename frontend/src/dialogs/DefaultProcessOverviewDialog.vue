<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Default Processes"
    class="w-1/2 min-h-96"
  >
    <div
      v-if="def_processes?.length"
      class="grid grid-cols-[repeat(auto-fit,minmax(16rem,1fr))] gap-3"
    >
      <Transformer
        v-for="def_proc in def_processes"
        :key="def_proc.name"
        :title="def_proc.name"
        :description="def_proc.description"
        :in="def_proc.in"
        :out="def_proc.out"
        @click="() => add(def_proc.name)"
      />
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

const route = useRoute()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  site_name: string
}>()

const { data: def_processes } = useDefProcesses()
const { mutate: addDefProcess } = useAddDefProcess(route)

function add(def_proc_name: string) {
  visible.value = false
  addDefProcess({ site_name: props.site_name, def_proc_name })
}
</script>

<style scoped></style>
