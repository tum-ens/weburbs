<template>
  <div v-if="overview" class="grid grid-cols-1 gap-3">
    <div
      class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 items-center"
    >
      <PlotlyDiagram
        title="Costs"
        class="min-h-96"
        :data="[
          {
            values: [
              overview.Invest,
              overview.Fixed,
              overview.Fuel,
              overview.Variable,
            ],
            labels: ['Invest', 'Fixed', 'Fuel', 'Variable'],
            type: 'pie',
          },
        ]"
        :margin="{ l: 0, b: 0, r: 0 }"
      />
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 justify-items-center">
        <DataPoint
          name="LCOE"
          :value="42"
          suffix="ct/kwh"
          classes="bg-yellow-200"
        />
        <DataPoint
          name="Share of Renewables"
          :value="45"
          suffix="%"
          classes="bg-green-300"
        />
        <DataPoint
          name="Invest"
          :value="overview.Invest"
          classes="bg-yellow-100"
        />
        <DataPoint name="Fixed" :value="overview.Fixed" classes="bg-blue-300" />
        <DataPoint name="Fuel" :value="overview.Fuel" classes="bg-stone-300" />
        <DataPoint
          name="Variable"
          :value="overview.Variable"
          classes="bg-orange-300"
        />
        <DataPoint name="Energy produced" :value="1" classes="bg-green-300" />
        <DataPoint name="Energy consumed" :value="2" classes="bg-red-300" />
        <DataPoint
          name="Slack production"
          :value="1"
          classes="bg-green-800 text-white"
        />
        <DataPoint
          name="Curtailpower consumption"
          :value="2"
          classes="bg-red-800 text-white"
        />
      </div>
      <PlotlyDiagram
        title="Renewable Share"
        class="min-h-96"
        :data="[
          {
            values: [9, 100],
            labels: ['Renewables', 'Fossils'],
            marker: {
              colors: ['rgb(44, 160, 44)', 'rgb(214, 39, 40)'],
            },
            type: 'pie',
            hole: 0.6,
          },
        ]"
        :margin="{ l: 0, b: 0, r: 0 }"
      />
    </div>

    <Accordion lazy>
      <AccordionPanel v-for="site in sites" :key="site.name" :value="site.name">
        <AccordionHeader>{{ site.name }}</AccordionHeader>
        <AccordionContent>
          <SiteResults :site="site" />
        </AccordionContent>
      </AccordionPanel>
    </Accordion>
  </div>
</template>

<script setup lang="ts">
import { useSites } from '@/backend/sites'
import { useRoute } from 'vue-router'
import { ref, watch } from 'vue'
import PlotlyDiagram from '@/plotly/PlotlyDiagram.vue'
import DataPoint from '@/pages/simulation/DataPoint.vue'
import { useGetSimulation, useGetSimulationConfig } from '@/backend/simulate'
import SiteResults from '@/pages/simulation/SiteResults.vue'

const route = useRoute()
const { data: sites } = useSites(route)
const { data: simulation } = useGetSimulation(route)
const { data: config } = useGetSimulationConfig(route)

const overview = ref()

watch(
  simulation,
  () => {
    if (!simulation.value) return

    overview.value = simulation.value.result.costs
    // demand.value = {}
    // created.value = {}
    // storageLevel.value = {}
    // for (const site in props.simulation.result.results) {
    //   demand.value[site] = {}
    //   created.value[site] = {}
    //   storageLevel.value[site] = {}
    //   for (const com in props.simulation.result.results[site]) {
    //     demand.value[site][com] = [
    //       {
    //         name: com,
    //         y: chunkAdd(
    //           props.simulation.result.results[site][com].demand,
    //           groupOptions[0].groupSize
    //         ),
    //         x: Array.from(
    //           { length: groupOptions[0].groupSize },
    //           (_, i) => i + 1
    //         ),
    //         type: 'bar'
    //       }
    //     ]
    //     created.value[site][com] = []
    //     for (const proc in props.simulation.result.results[site][com].created) {
    //       created.value[site][com].push({
    //         name: proc,
    //         y: chunkAdd(
    //           props.simulation.result.results[site][com].created[proc],
    //           groupOptions[0].groupSize
    //         ),
    //         x: Array.from(
    //           { length: groupOptions[0].groupSize },
    //           (_, i) => i + 1
    //         ),
    //         type: 'bar'
    //       })
    //     }
    //     if (props.simulation.result.results[site][com].storage) {
    //       storageLevel.value[site][com] = [
    //         {
    //           name: com,
    //           y: chunkAvg(
    //             props.simulation.result.results[site][com].storage.Level,
    //             groupOptions[0].groupSize
    //           ),
    //           x: Array.from(
    //             { length: groupOptions[0].groupSize },
    //             (_, i) => i + 1
    //           ),
    //           type: 'scatter'
    //         }
    //       ]
    //     }
    //   }
    // }
  },
  { immediate: true },
)
</script>

<style scoped></style>
