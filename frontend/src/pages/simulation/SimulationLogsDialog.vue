<template>
  <Dialog v-model:visible="visible" :draggable="false" header="Logs" modal>
    <p style="white-space: pre-line">
      {{ logs }}
    </p>
  </Dialog>
</template>

<script setup lang="ts">
import { useGetSimulationLogs } from '@/backend/simulate'
import type { SimulationResult } from '@/backend/interfaces'
import { useRoute } from 'vue-router'

const route = useRoute()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  result: SimulationResult
}>()

const { data: logs } = useGetSimulationLogs(route, props.result)
</script>

<style scoped></style>
