<template>
  <i v-if="!completed" class="pi pi-hourglass"></i>
  <i
    v-else-if="status === SimulationResultStatus.Optimal"
    class="pi pi-check-circle"
  ></i>
  <i
    v-else-if="status === SimulationResultStatus.Infeasible"
    class="pi pi-exclamation-circle"
  ></i>
  <i v-else class="pi pi-times-circle"></i>
</template>

<script setup lang="ts">
import { SimulationResultStatus } from '@/backend/interfaces'

defineProps<{
  completed: boolean
  status: SimulationResultStatus
}>()
</script>

<style scoped></style>
