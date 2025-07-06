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
              overview.Purchase > 0 ? overview.Purchase : undefined,
              // Check if Environment exists and is positive for display in pie chart
              overview.Environment > 0 ? overview.Environment : undefined,
            ],
            labels: [
              overview.Invest ? 'Invest' : null,
              overview.Fixed > 0 ? 'Fixed' : null,
              overview.Fuel ? 'Fuel' : null,
              overview.Variable ? 'Variable' : null,
              // Label for Environment if present
              overview.Purchase > 0 ? 'Purchase' : null,
              overview.Environment > 0 ? 'Environment' : null,
            ],
            type: 'pie',
          },
        ]"
        :margin="{ l: 0, b: 0, r: 0 }"
      />
      <div class="grid grid-cols-2 gap-3 justify-items-center">
        <div class="col-span-2 flex items-center justify-center gap-2 mb-2">
          <label for="commodity-select" class="font-bold"
            >Show Results For:</label
          >
          <select
            id="commodity-select"
            v-model="selectedCommodityType"
            class="p-2 border rounded-md"
          >
            <option value="elec">Electricity</option>
            <option value="heat">Heat</option>
          </select>
        </div>

        <div class="col-span-2 flex items-center justify-center gap-2 mb-2">
          <label for="display-unit-select" class="font-bold"
            >Display Units:</label
          >
          <select
            id="display-unit-select"
            v-model="selectedDisplayUnit"
            class="p-2 border rounded-md"
          >
            <option value="kW">kW & kg</option>
            <option value="MW">MW & tonnes</option>
          </select>
        </div>

        <DataPoint
          name="Total Cost"
          :value="totalCost"
          suffix="€"
          classes="bg-blue-200 text-black"
        />

        <DataPoint
          :name="lcoName"
          :value="lcoValue"
          :suffix="lcoSuffix"
          classes="bg-yellow-200 text-black"
        />

        <!--        <DataPoint-->
        <!--          name="Share of Renewables"-->
        <!--          :value="Math.max(1 - currentFossilProduced / currentConsumed, 0) * 100"-->
        <!--          suffix="%"-->
        <!--          classes="bg-green-300 text-black"-->
        <!--        />-->
        <DataPoint name="Invest" :value="overview.Invest" suffix="€" />
        <DataPoint name="Fixed" :value="overview.Fixed" suffix="€" />
        <DataPoint name="Fuel" :value="overview.Fuel" suffix="€" />
        <DataPoint name="Variable" :value="overview.Variable" suffix="€" />
        <DataPoint name="Purchase" :value="overview.Purchase" suffix="€" />
        <DataPoint
          :name="`${selectedCommodityType === 'elec' ? 'Energy' : 'Heat'} produced`"
          :value="currentProducedDisplay"
          classes="bg-green-300 text-black"
          :suffix="energySuffix"
        />
        <DataPoint
          :name="`${selectedCommodityType === 'elec' ? 'Energy' : 'Heat'} consumed`"
          :value="currentConsumedDisplay"
          classes="bg-red-300 text-black"
          :suffix="energySuffix"
        />
        <!--        <DataPoint-->
        <!--          name="CO2 saved"-->
        <!--          :value="co2SavedDisplay"-->
        <!--          classes="bg-green-300 text-black"-->
        <!--          :suffix="co2Suffix"-->
        <!--        />-->
        <!--        <DataPoint-->
        <!--          :name="`${selectedCommodityType === 'elec' ? 'Energy' : 'Heat'} lost`"-->
        <!--          :value="currentLostDisplay"-->
        <!--          classes="bg-red-300 text-black"-->
        <!--          :suffix="energySuffix"-->
        <!--        />-->
      </div>
      <!--      <PlotlyDiagram-->
      <!--        title="Share of Renewables"-->
      <!--        class="min-h-96"-->
      <!--        :data="[-->
      <!--          {-->
      <!--            values: [-->
      <!--              Math.max(currentConsumed - currentFossilProduced, 0),-->
      <!--              currentFossilProduced > 0.1 ? currentFossilProduced : 0,-->
      <!--            ],-->
      <!--            labels: ['Renewables', 'Fossils'],-->
      <!--            marker: {-->
      <!--              colors: ['rgb(44, 160, 44)', 'rgb(214, 39, 40)'],-->
      <!--            },-->
      <!--            type: 'pie',-->
      <!--            hole: 0.6,-->
      <!--          },-->
      <!--        ]"-->
      <!--        :margin="{ l: 0, b: 0, r: 0 }"-->
      <!--      />-->
    </div>

    <Accordion lazy>
      <AccordionPanel v-for="site in sites" :key="site.name" :value="site.name">
        <AccordionHeader>{{ site.name }}</AccordionHeader>
        <AccordionContent>
          <SiteResults
            :site="site"
            :selected-commodity-type="selectedCommodityType"
            :selected-display-unit="selectedDisplayUnit"
          />
        </AccordionContent>
      </AccordionPanel>
    </Accordion>
  </div>
</template>

<script setup lang="ts">
import { useSites } from '@/backend/sites'
import { useRoute } from 'vue-router'
import { ref, watch, computed } from 'vue'
import PlotlyDiagram from '@/plotly/PlotlyDiagram.vue'
import DataPoint from '@/pages/simulation/DataPoint.vue'
import { useGetSimulation, useGetSimulationConfig } from '@/backend/simulate'
import SiteResults from '@/pages/simulation/SiteResults.vue'
import Accordion from 'primevue/accordion'
import AccordionPanel from 'primevue/accordionpanel'
import AccordionHeader from 'primevue/accordionheader'
import AccordionContent from 'primevue/accordioncontent'

const route = useRoute()
const { data: sites } = useSites(route)
const { data: simulation } = useGetSimulation(route)
const { data: config } = useGetSimulationConfig(route)

const overview = ref()

// Electricity-specific metrics (BASE UNIT: MWh)
const elecProduced = ref(0)
const fossilElecProduced = ref(0)
const elecConsumed = ref(0)
const slackElecProduction = ref(0)

// Heat-specific metrics (BASE UNIT: MWh)
const heatProduced = ref(0)
const fossilHeatProduced = ref(0)
const heatConsumed = ref(0)
const slackHeatProduction = ref(0)

// Global CO2 produced (BASE UNIT: tonnes)
const co2Produced = ref(0)

// Dropdown selection for which commodity's results to show
const selectedCommodityType = ref('elec') // Default to Electricity

// Display Units dropdown (now controls LCO units too)
const selectedDisplayUnit = ref('MW') // Default to MW & tonnes (meaning MWh and tonnes base units)

// Watcher to calculate ALL base metrics for both commodities
watch(
  [simulation, config],
  () => {
    if (!simulation.value || !config.value) return

    overview.value = simulation.value.result.costs

    // Reset ALL base values before recalculating
    elecConsumed.value = 0
    elecProduced.value = 0
    fossilElecProduced.value = 0
    slackElecProduction.value = 0

    heatConsumed.value = 0
    heatProduced.value = 0
    fossilHeatProduced.value = 0
    slackHeatProduction.value = 0

    co2Produced.value = 0

    for (const siteName in simulation.value.result.results) {
      const siteResults = simulation.value.result.results[siteName]
      const siteConfig = config.value['site'][siteName]

      for (const comName in siteResults) {
        // --- Electricity Tracking (base MWh) ---
        // Assuming your simulation data for ELEC created/demand is already in MWh.
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
              Object.keys(procConfig['commodity']).some(cName =>
                cName.toUpperCase().includes('CO2'),
              )
            ) {
              fossilElecProduced.value += procCreated
            }
            if (procName.toLowerCase().includes('slack power plant'))
              slackElecProduction.value += procCreated
          }
          elecConsumed.value += comResults.demand.reduce((a, b) => a + b, 0)
        }

        // --- Heat Tracking (base MWh) ---
        // Assuming your simulation data for HEAT created/demand is already in MWh.
        if (
          comName.toUpperCase().includes('HEAT') ||
          comName.toUpperCase().includes('THERMAL') ||
          comName.toUpperCase().includes('MJ') ||
          comName.toUpperCase().includes('GJ') ||
          comName.toUpperCase().includes('KWH_TH')
        ) {
          const comResults = siteResults[comName]
          for (const procName in comResults.created) {
            const procCreated = comResults.created[procName].reduce(
              (a, b) => a + b,
              0,
            )
            const procConfig = siteConfig['process'][procName] || {
              commodity: {},
            }
            heatProduced.value += procCreated
            if (
              Object.keys(procConfig['commodity']).some(cName =>
                cName.toUpperCase().includes('CO2'),
              )
            ) {
              fossilHeatProduced.value += procCreated
            }
            if (procName.toLowerCase().includes('slack heat source'))
              slackHeatProduction.value += procCreated
          }
          heatConsumed.value += comResults.demand.reduce((a, b) => a + b, 0)
        }

        // --- CO2 Tracking (GLOBAL, base tonnes) ---
        // Assuming your simulation data for CO2 created is already in tonnes.
        if (comName.toUpperCase().includes('CO2')) {
          const comResults = siteResults[comName]
          for (const procName in comResults.created) {
            co2Produced.value += comResults.created[procName].reduce(
              (a, b) => a + b,
              0,
            )
          }
        }
      }
    }
  },
  { immediate: true },
)

// Computed property for Total Cost
const totalCost = computed(() => {
  if (!overview.value) return 0
  return (
    overview.value.Invest +
    overview.value.Fixed +
    overview.value.Fuel +
    overview.value.Variable +
    (overview.value.Purchase || 0) +
    (overview.value.Environment || 0) // Safely add Environment, defaulting to 0 if not present
  )
})

// Computed properties to get selected commodity's base data (MWh for energy, tonnes for CO2)
const currentProduced = computed(() => {
  return selectedCommodityType.value === 'elec'
    ? elecProduced.value
    : heatProduced.value
})

const currentFossilProduced = computed(() => {
  return selectedCommodityType.value === 'elec'
    ? fossilElecProduced.value
    : fossilHeatProduced.value
})

const currentConsumed = computed(() => {
  return selectedCommodityType.value === 'elec'
    ? elecConsumed.value
    : heatConsumed.value
})

const currentSlackProduction = computed(() => {
  return selectedCommodityType.value === 'elec'
    ? slackElecProduction.value
    : slackHeatProduction.value
})

// Computed properties for Energy/Mass DISPLAY values and Suffixes
const convertEnergyToDisplayUnit = (value: number) => {
  // Base is MWh. If kW is selected, convert to kWh by multiplying by 1000.
  return selectedDisplayUnit.value === 'kW' ? value * 1000 : value
}

const convertCO2ToDisplayUnit = (value: number) => {
  // Base is tonnes. If kW is selected (implying kg), convert to kg by multiplying by 1000.
  return selectedDisplayUnit.value === 'kW' ? value * 1000 : value
}

const currentProducedDisplay = computed(() =>
  convertEnergyToDisplayUnit(currentProduced.value),
)
const currentConsumedDisplay = computed(() =>
  convertEnergyToDisplayUnit(currentConsumed.value),
)
const currentLostDisplay = computed(() =>
  convertEnergyToDisplayUnit(currentProduced.value - currentConsumed.value),
)

const energySuffix = computed(() =>
  selectedDisplayUnit.value === 'kW' ? 'kWh' : 'MWh',
)

const co2Suffix = computed(() =>
  selectedDisplayUnit.value === 'kW' ? 'kg' : 'tonnes',
)

const co2SavedDisplay = computed(() => {
  // Baseline: 560 kg CO2 per MWh.
  // currentConsumed.value is now in MWh (base unit).
  const baselineCO2_kg = 560 * currentConsumed.value

  // co2Produced.value is now in tonnes (base unit). Convert to kg for calculation.
  const actualCO2Produced_kg = co2Produced.value * 1000

  const savedCO2_kg = baselineCO2_kg - actualCO2Produced_kg

  // Convert the final saved CO2 to the display unit (kg or tonnes)
  return convertCO2ToDisplayUnit(savedCO2_kg / 1000) // Divide by 1000 to get tonnes, then use convertCO2ToDisplayUnit
})

// Computed property for dynamic LCO name (LCOE or LCOH)
const lcoName = computed(() => {
  return selectedCommodityType.value === 'elec' ? 'LCOE' : 'LCOH'
})

// Computed property for dynamic LCO value, now tied to selectedDisplayUnit
const lcoValue = computed(() => {
  if (!overview.value) return 0

  const totalCosts =
    overview.value.Invest +
    overview.value.Fixed +
    overview.value.Fuel +
    overview.value.Variable +
    (overview.value.Purchase || 0) +
    (overview.value.Environment || 0) // Include Environment cost here too

  let denominator_MWh = 0
  if (selectedCommodityType.value === 'elec') {
    denominator_MWh = elecConsumed.value // Already in MWh
  } else {
    denominator_MWh = heatProduced.value // Already in MWh
  }

  if (denominator_MWh > 0) {
    const value_EurosPerMWh = totalCosts / denominator_MWh // Value in Euros/MWh

    // Adjust LCO value based on selectedDisplayUnit
    if (selectedDisplayUnit.value === 'kW') {
      // If display is kW (meaning kWh for energy), LCO should be in cents/kWh
      return value_EurosPerMWh / 10 // Euros/MWh -> cents/kWh (divide by 10)
    } else if (selectedDisplayUnit.value === 'MW') {
      // If display is MW (meaning MWh for energy), LCO should be in Euros/MWh
      return value_EurosPerMWh
    }
    return value_EurosPerMWh // Fallback
  }
  return 0
})

// Computed property for dynamic LCO suffix, now tied to selectedDisplayUnit
const lcoSuffix = computed(() => {
  return selectedDisplayUnit.value === 'kW' ? 'Euros/kWh' : 'Euros/MWh'
})
</script>

<style scoped></style>
