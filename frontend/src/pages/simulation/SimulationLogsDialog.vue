<template>
  <Dialog v-model:visible="visible" :draggable="false" header="Logs" modal>
    <p style="white-space: pre-line">
      {{ logs }}
    </p>
  </Dialog>
</template>

<script setup lang="ts">
import { useGetSimulationLogs } from '@/backend/simulate'
import { useRoute } from 'vue-router'

const route = useRoute()

const visible = defineModel<boolean>('visible', { default: false })

const { data: logs } = useGetSimulationLogs(route)
</script>

<style scoped></style>
