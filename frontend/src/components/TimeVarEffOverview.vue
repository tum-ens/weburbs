<template>
  <div class="flex flex-col">
    <template v-if="processes">
      <template v-for="proc in processes" :key="proc.name">
        <TimeVarEffProcessOverview :site="site" :process="proc" />
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { Site } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import { useProcesses } from '@/backend/processes'
import TimeVarEffProcessOverview from '@/components/TimeVarEffProcessOverview.vue'

const route = useRoute()

const props = defineProps<{
  site: Site
}>()

const { data: processes } = useProcesses(route, props.site)
</script>

<style scoped></style>
