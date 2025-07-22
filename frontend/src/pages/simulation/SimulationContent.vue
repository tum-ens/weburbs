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
              overview.Invest > 0 ? overview.Invest : undefined,
              overview.Fixed > 0 ? overview.Fixed : undefined,
              overview.Fuel > 0 ? overview.Fuel : undefined,
              overview.Variable > 0 ? overview.Variable : undefined,
            ],
            labels: [
              overview.Invest ? 'Invest' : null,
              overview.Fixed > 0 ? 'Fixed' : null,
              overview.Fuel ? 'Fuel' : null,
              overview.Variable ? 'Variable' : null,
            ],
            type: 'pie',
          },
        ]"
        :margin="{ l: 0, b: 0, r: 0 }"
      />
      <div class="grid grid-cols-2 gap-3 justify-items-center">
        <DataPoint
          name="LCOE"
          :value="
            ((overview.Invest +
              overview.Fixed +
              overview.Fuel +
              overview.Variable) /
              elecConsumed) *
            100
          "
          suffix="ct/kWh"
          classes="bg-yellow-200 text-black"
        />
        <DataPoint
          name="Share of Renewables"
          :value="Math.max(1 - fossilProduced / elecConsumed, 0) * 100"
          suffix="%"
          classes="bg-green-300  text-black"
        />
        <DataPoint name="Invest" :value="overview.Invest" suffix="$" />
        <DataPoint name="Fixed" :value="overview.Fixed" suffix="$" />
        <DataPoint name="Fuel" :value="overview.Fuel" suffix="$" />
        <DataPoint name="Variable" :value="overview.Variable" suffix="$" />
        <DataPoint
          name="Energy produced"
          :value="elecProduced"
          classes="bg-green-300 text-black"
          suffix="kWh"
        />
        <DataPoint
          name="Energy consumed"
          :value="elecConsumed"
          classes="bg-red-300 text-black"
          suffix="kWh"
        />
        <DataPoint
          name="CO2 saved"
          :value="(560 * elecConsumed) / 1000 - co2Produced"
          classes="bg-green-300 text-black"
          suffix="kg"
        />
        <DataPoint
          name="Energy lost"
          :value="elecProduced - elecConsumed"
          classes="bg-red-300 text-black"
          suffix="kWh"
        />
      </div>
      <PlotlyDiagram
        title="Share of Renewables"
        class="min-h-96"
        :data="[
          {
            values: [
              Math.max(elecConsumed - fossilProduced, 0),
              fossilProduced > 0.1 ? fossilProduced : 0,
            ],
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

    <Accordion multiple lazy>
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

const elecProduced = ref(0)
const fossilProduced = ref(0)
const elecConsumed = ref(0)
const slackProduction = ref(0)

const co2Produced = ref(0)
watch(
  [simulation, config],
  () => {
    if (!simulation.value || !config.value) return

    overview.value = simulation.value.result.costs

    elecConsumed.value = 0
    elecProduced.value = 0
    fossilProduced.value = 0
    slackProduction.value = 0
    co2Produced.value = 0
    for (const siteName in simulation.value.result.results) {
      const siteResults = simulation.value.result.results[siteName]
      const siteConfig = config.value['site'][siteName]
      for (const comName in siteResults) {
        if (comName.toUpperCase().includes('CO2')) {
          const comResults = siteResults[comName]
          for (const procName in comResults.created) {
            co2Produced.value += comResults.created[procName].reduce(
              (a, b) => a + b,
              0,
            )
          }
        }
        if (comName.toUpperCase().includes('ELEC')) {
          const comResults = siteResults[comName]
          for (const procName in comResults.created) {
            const procCreated = comResults.created[procName].reduce(
              (a, b) => a + b,
              0,
            )
            const procConfig = siteConfig['process'][procName] || {
              commodity: {},
            }
            elecProduced.value += procCreated
            if (
              Object.keys(procConfig['commodity']).some(comName =>
                comName.toUpperCase().includes('CO2'),
              )
            )
              fossilProduced.value += procCreated
            if (procName.toLowerCase().includes('slack power plant'))
              slackProduction.value += procCreated
          }
          elecConsumed.value += comResults.demand.reduce((a, b) => a + b, 0)
        }
      }
    }
  },
  { immediate: true },
)
</script>

<style scoped></style>
