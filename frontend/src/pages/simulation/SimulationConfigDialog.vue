<template>
  <Dialog v-model:visible="visible" :draggable="false" header="Config" modal>
    <p style="white-space: pre-wrap">
      {{ config }}
    </p>
  </Dialog>
</template>

<script setup lang="ts">
import { useGetSimulationConfig } from '@/backend/simulate'
import { useRoute } from 'vue-router'

const route = useRoute()

const visible = defineModel<boolean>('visible', { default: false })

const { data: config } = useGetSimulationConfig(route)
</script>

<style scoped></style>
