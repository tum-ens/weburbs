<template>
  <Card>
    <template #title>Simulations</template>
    <template #content>
      <Button @click="() => triggerSimulation()">Simulate</Button>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { useTriggerSimulation } from '@/backend/simulate'
import { useRoute } from 'vue-router'

const route = useRoute()

const { mutate: triggerSimulation } = useTriggerSimulation(route)
</script>

<style scoped></style>
