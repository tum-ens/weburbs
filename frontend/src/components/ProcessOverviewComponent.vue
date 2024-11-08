<template>
  <div
    v-if="processes?.length"
    class="grid grid-cols-[repeat(auto-fit,minmax(16rem,1fr))] gap-3"
  >
    <Transformer
      v-for="proc in processes"
      :key="proc.name"
      :title="proc.name"
      :description="proc.description"
      :in="proc.in"
      :out="proc.out"
    />
  </div>
  <div v-else>
    <span>No processes added</span>
  </div>
</template>

<script setup lang="ts">
import { useProcesses } from '@/backend/processes'
import Transformer from '@/components/TransformerComponent.vue'
import { useRoute } from 'vue-router'
import type { Site } from '@/backend/interfaces'

const route = useRoute()

const props = defineProps<{
  site: Site
}>()

const { data: processes } = useProcesses(route, props.site)
</script>

<style scoped></style>
