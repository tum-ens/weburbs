<template>
  <div class="flex flex-col gap-3">
    <template v-for="com in coms" :key="com.name">
      <div v-if="com.name in props.demand">
        <h1>{{ com.name }}</h1>
        <div>
          <BarDiagramm
            title="Demand"
            :data="props.demand[com.name]"
            title-x="steps"
            title-y="kwh"
            :bargroupgap="0.1"
          />
        </div>
        <div>
          <BarDiagramm
            title="Create"
            :data="props.created[com.name]"
            title-x="steps"
            title-y="kwh"
            :bargroupgap="0.1"
          />
        </div>
        <div v-if="props.storageLevel">
          <BarDiagramm
            title="Storage Level"
            :data="props.storageLevel[com.name]"
            title-x="steps"
            title-y="kwh"
            :bargroupgap="0.1"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { Site } from '@/backend/interfaces'
import { useProjectSiteCommodities } from '@/backend/commodities'
import { useRoute } from 'vue-router'
import BarDiagramm from '@/plotly/BarDiagramm.vue'
import Plotly from 'plotly.js-dist'

const route = useRoute()

const props = defineProps<{
  site: Site
  demand: { [key: string]: Partial<Plotly.Data>[] }
  created: { [key: string]: Partial<Plotly.Data>[] }
  storageLevel?: { [key: string]: Partial<Plotly.Data>[] }
}>()

const { data: coms } = useProjectSiteCommodities(route, props.site.name)
</script>

<style scoped></style>
