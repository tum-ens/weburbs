<template>
  <div class="flex flex-col gap-3">
    <template v-for="com in coms" :key="com.name">
      <template v-if="com.name in props.demand">
        <h1>{{ com.name }}</h1>
        <BarDiagramm
          title="Ratio of Costs"
          :data="[
            {
              values: [1, 2, 3, 1],
              labels: ['Solar', 'Wind', 'Water', 'Nuclear'],
              type: 'pie',
            },
          ]"
          title-x=""
          title-y=""
        />
        <BarDiagramm
          title="Demand"
          :data="props.demand[com.name]"
          title-x="steps"
          title-y="kwh"
          :bargroupgap="0.1"
        />
        <BarDiagramm
          title="Create"
          :data="props.created[com.name]"
          title-x="steps"
          title-y="kwh"
          :bargroupgap="0.1"
        />
        <BarDiagramm
          v-if="props.storageLevel"
          title="Storage Level"
          :data="props.storageLevel[com.name]"
          title-x="steps"
          title-y="kwh"
          :bargroupgap="0.1"
        />
      </template>
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
