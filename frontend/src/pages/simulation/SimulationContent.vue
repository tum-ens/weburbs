<template>
  <div v-if="overview" class="grid grid-cols-1 gap-3">
    <div class="grid grid-cols-4 gap-3">
      <Fieldset legend="Overview">
        <ul>
          <li>Environmental: {{ overview.Environmental.toFixed(2) }}</li>
          <li>Fixed: {{ overview.Invest.toFixed(2) }}</li>
          <li>Fuel: {{ overview.Fuel.toFixed(2) }}</li>
          <li>Invest: {{ overview.Invest.toFixed(2) }}</li>
          <li>Variable: {{ overview.Variable.toFixed(2) }}</li>
        </ul>
      </Fieldset>
      <DataTable :value="procs" class="col-span-3">
        <Column field="site" header="Site"></Column>
        <Column field="proc" header="Commodity"></Column>
        <Column field="new" header="New"></Column>
        <Column field="total" header="Total"></Column>
      </DataTable>
    </div>

    <Accordion lazy>
      <AccordionPanel v-for="site in sites" :key="site.name" :value="site.name">
        <AccordionHeader>{{ site.name }}</AccordionHeader>
        <AccordionContent>
          <div class="overflow-hidden">
            <SiteResults
              v-if="site.name in demand && site.name in created"
              :site="site"
              :demand="demand[site.name]"
              :created="created[site.name]"
              :storageLevel="
                site.name in storageLevel ? storageLevel[site.name] : undefined
              "
            />
          </div>
        </AccordionContent>
      </AccordionPanel>
    </Accordion>
  </div>
</template>

<script setup lang="ts">
import SiteResults from '@/pages/simulation/SiteResults.vue'
import { useSites } from '@/backend/sites'
import { useRoute } from 'vue-router'
import { ref, watch } from 'vue'
import Plotly from 'plotly.js-dist'
import { chunkAdd, chunkAvg, groupOptions } from '@/helper/diagrams'
import type { SimulationDetails } from '@/backend/interfaces'

const route = useRoute()
const { data: sites } = useSites(route)

const props = defineProps<{
  simulation: SimulationDetails
}>()

const overview = ref()
const procs = ref<{ site: string; proc: string; total: number; new: number }[]>(
  [],
)
const demand = ref<{
  [key: string]: { [key: string]: Partial<Plotly.Data>[] }
}>({})
const created = ref<{
  [key: string]: { [key: string]: Partial<Plotly.Data>[] }
}>({})
const storageLevel = ref<{
  [key: string]: { [key: string]: Partial<Plotly.Data>[] }
}>({})

watch(
  props,
  () => {
    procs.value = []
    overview.value = props.simulation.result.costs
    for (const site in props.simulation.result.process) {
      for (const proc in props.simulation.result.process[site]) {
        procs.value.push({
          site,
          proc,
          total: props.simulation.result.process[site][proc].Total.toFixed(2),
          new: props.simulation.result.process[site][proc].New.toFixed(2),
        })
      }
    }

    demand.value = {}
    created.value = {}
    storageLevel.value = {}
    for (const site in props.simulation.result.results) {
      demand.value[site] = {}
      created.value[site] = {}
      storageLevel.value[site] = {}
      for (const com in props.simulation.result.results[site]) {
        demand.value[site][com] = [
          {
            name: com,
            y: chunkAdd(
              props.simulation.result.results[site][com].demand,
              groupOptions[0].groupSize,
            ),
            x: Array.from(
              { length: groupOptions[0].groupSize },
              (_, i) => i + 1,
            ),
            type: 'bar',
          },
        ]
        created.value[site][com] = []
        for (const proc in props.simulation.result.results[site][com].created) {
          created.value[site][com].push({
            name: proc,
            y: chunkAdd(
              props.simulation.result.results[site][com].created[proc],
              groupOptions[0].groupSize,
            ),
            x: Array.from(
              { length: groupOptions[0].groupSize },
              (_, i) => i + 1,
            ),
            type: 'bar',
          })
        }
        if (props.simulation.result.results[site][com].storage) {
          storageLevel.value[site][com] = [
            {
              name: com,
              y: chunkAvg(
                props.simulation.result.results[site][com].storage.Level,
                groupOptions[0].groupSize,
              ),
              x: Array.from(
                { length: groupOptions[0].groupSize },
                (_, i) => i + 1,
              ),
              type: 'scatter',
            },
          ]
        }
      }
    }
  },
  { immediate: true },
)
</script>

<style scoped></style>
