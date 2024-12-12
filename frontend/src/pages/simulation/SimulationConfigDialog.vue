<template>
  <Dialog v-model:visible="visible" :draggable="false" header="Logs" modal>
    <p style="white-space: pre-wrap">
      {{ config }}
    </p>
  </Dialog>
</template>

<script setup lang="ts">
import { useGetSimulationConfig } from '@/backend/simulate'
import type { SimulationResult } from '@/backend/interfaces'
import { useRoute } from 'vue-router'

const route = useRoute()

const visible = defineModel<boolean>('visible', { default: false })
const props = defineProps<{
  result: SimulationResult
}>()

const { data: config } = useGetSimulationConfig(route, props.result)
</script>

<style scoped></style>
