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
              environmentalCost > 0 ? environmentalCost : undefined,
            ],
            labels: [
              overview.Invest ? 'Invest' : null,
              overview.Fixed > 0 ? 'Fixed' : null,
              overview.Fuel ? 'Fuel' : null,
              overview.Variable ? 'Variable' : null,
              overview.Purchase > 0 ? 'Purchase' : null,
              environmentalCost > 0 ? 'Environmental' : null,
            ],
            type: 'pie',
          },
        ]"
        :margin="{ l: 0, b: 0, r: 0 }"
      />
      <div class="grid grid-cols-2 gap-3 justify-items-center">
        <div class="col-span-2 flex items-center justify-center gap-2 mb-2">
          <label for="commodity-select" class="font-bold">Show Results For:</label>
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
          <label for="display-unit-select" class="font-bold">Display Units:</label>
          <select
            id="display-unit-select"
            v-model="selectedDisplayUnit"
            class="p-2 border rounded-md"
          >
            <option value="kW">kW & kg</option>
            <option value="MW">MW & tonnes</option>
          </select>
        </div>

        <!-- KPI block (totals and price metrics) stays at the top -->
        <DataPoint
          name="Total Cost"
          :value="totalCost"
          suffix="€"
          classes="bg-blue-200 text-black"
        />

        <DataPoint
          name="Total CO2 Environment"
          :value="co2EnvironmentDisplay"
          :suffix="co2Suffix"
          classes="bg-orange-200 text-black"
        />

        <DataPoint name="Invest" :value="overview.Invest" suffix="€" />
        <DataPoint name="Fixed" :value="overview.Fixed" suffix="€" />
        <DataPoint name="Fuel" :value="overview.Fuel" suffix="€" />
        <DataPoint name="Variable" :value="overview.Variable" suffix="€" />
        <DataPoint name="Purchase" :value="overview.Purchase" suffix="€" />
        <DataPoint name="Environmental" :value="environmentalCost" suffix="€" />

        <DataPoint
          :name="`${lcoName} (${selectedCommodityType === 'elec' ? 'per delivered' : 'per generated'})`"
          :value="lcoDeliveredValue"
          :suffix="lcoSuffix"
          classes="bg-green-200 text-black"
        />
        <DataPoint
          :name="`${lcoName} (per consumed)`"
          :value="lcoConsumedValue"
          :suffix="lcoSuffix"
          classes="bg-green-200 text-black"
        />

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
          <SiteResults :site="site" :selected-display-unit="selectedDisplayUnit" />
        </AccordionContent>
      </AccordionPanel>
    </Accordion>

    <!-- Transmission Section -->
    <div v-if="transmissionCharts && Object.keys(transmissionCharts).length > 0" class="grid grid-cols-1 gap-3 mt-6">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <h2 class="text-xl font-bold">Transmission Flows</h2>
        <div class="flex items-center gap-3">
          <FloatLabel variant="on" class="w-64">
            <Select
              fluid
              id="transmission-select"
              :options="transmissionOptions"
              optionLabel="label"
              v-model="selectedTransmission"
            />
            <label for="transmission-select">Select Transmission</label>
          </FloatLabel>
          <FloatLabel variant="on" class="w-48">
            <Select
              fluid
              id="transmission-groupoptions"
              :options="groupOptions"
              optionLabel="name"
              v-model="transmissionGroupOption"
            />
            <label for="transmission-groupoptions">Group values</label>
          </FloatLabel>
        </div>
      </div>
      <div v-if="selectedTransmission && transmissionCharts[selectedTransmission.key]" class="grid grid-cols-1 gap-3">
        <PlotlyDiagram
          :title="`${selectedTransmission.siteA} → ${selectedTransmission.siteB}`"
          :data="transmissionCharts[selectedTransmission.key].data"
          titleX="Time"
          :titleY="transmissionCharts[selectedTransmission.key].unit"
          :bargap="0.2"
          :margin="{
            t: 150,
            l: 100,
            r: 50,
            b: 50,
          }"
        />
      </div>
      <div
        v-else-if="selectedTransmission"
        class="flex items-center justify-center p-8 text-gray-500"
      >
        <p>No data available for selected transmission</p>
      </div>
    </div>

    <!-- Cost breakdown tables at end of page -->
    <div class="grid grid-cols-1 gap-6 mt-8">
      <div v-if="techCostCommodityList.length">
        <h3 class="font-bold mb-2">
          {{ techCostCommodityLabel }} technology annual cost breakdown
        </h3>
        <table class="w-full text-xs md:text-sm border-collapse">
          <thead>
            <tr class="border-b">
              <th class="text-left py-1 pr-2">Technology</th>
              <th class="text-right py-1 px-2">Energy [{{ energySuffix }}]</th>
              <th class="text-right py-1 pl-2">Invest [€]</th>
              <th class="text-right py-1 pl-2">Fixed [€]</th>
              <th class="text-right py-1 pl-2">Fuel [€]</th>
              <th class="text-right py-1 pl-2">Variable [€]</th>
              <th class="text-right py-1 pl-2">CO2 / Env [€]</th>
              <th class="text-right py-1 pl-2">Total [€]</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="tech in techCostCommodityList"
              :key="`${selectedCommodityType}-${tech.name}`"
              class="border-b last:border-0"
            >
              <td class="py-1 pr-2">{{ tech.name }}</td>
              <td class="py-1 px-2 text-right">
                {{ convertEnergyToDisplayUnit(tech.energy).toFixed(1) }}
              </td>
              <td class="py-1 pl-2 text-right">
                  {{ tech.invest.toFixed(0) }}
                </td>
                <td class="py-1 pl-2 text-right">
                  {{ tech.fixed.toFixed(0) }}
                </td>
                <td class="py-1 pl-2 text-right">
                  {{ tech.fuel.toFixed(0) }}
                </td>
                <td class="py-1 pl-2 text-right">
                  {{ tech.variable.toFixed(0) }}
                </td>
                <td class="py-1 pl-2 text-right">
                  {{ tech.environment.toFixed(0) }}
                </td>
                <td class="py-1 pl-2 text-right">
                  {{ tech.total.toFixed(0) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div
        v-if="commodityStackedData.length"
        class="mt-4 h-96 max-w-3xl mx-auto w-full"
      >
        <PlotlyDiagram
          :title="`${techCostCommodityLabel} technology annual cost stack`"
          :data="commodityStackedData"
          titleX="Technology"
          titleY="Annual cost [€]"
          :bargap="0.6"
          :bargroupgap="0.3"
          :margin="{ t: 80, b: 120, l: 80, r: 40 }"
        />
      </div>

      <div v-if="processCostList.length" class="mt-8">
        <h3 class="font-bold mb-2">Process annual cost breakdown (from optimizer)</h3>
        <table class="w-full text-xs md:text-sm border-collapse">
          <thead>
            <tr class="border-b">
              <th class="text-left py-1 pr-2">Process</th>
              <th class="text-right py-1 pl-2">Invest [€]</th>
              <th class="text-right py-1 pl-2">Fixed [€]</th>
              <th class="text-right py-1 pl-2">Fuel [€]</th>
              <th class="text-right py-1 pl-2">Variable [€]</th>
              <th class="text-right py-1 pl-2">CO2 / Env [€]</th>
              <th class="text-right py-1 pl-2">Total [€]</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in processCostList"
              :key="row.name"
              class="border-b last:border-0"
            >
              <td class="py-1 pr-2">{{ row.name }}</td>
              <td class="py-1 pl-2 text-right">
                {{ row.invest.toFixed(0) }}
              </td>
              <td class="py-1 pl-2 text-right">
                {{ row.fixed.toFixed(0) }}
              </td>
              <td class="py-1 pl-2 text-right">
                {{ row.fuel.toFixed(0) }}
              </td>
              <td class="py-1 pl-2 text-right">
                {{ row.variable.toFixed(0) }}
              </td>
              <td class="py-1 pl-2 text-right">
                {{ row.environment.toFixed(0) }}
              </td>
              <td class="py-1 pl-2 text-right">
                {{ row.total.toFixed(0) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="storageCostListForCommodity.length" class="mt-6">
        <h3 class="font-bold mb-2">
          {{ techCostCommodityLabel }} storage annual cost breakdown (from optimizer)
        </h3>
        <table class="w-full text-xs md:text-sm border-collapse">
          <thead>
            <tr class="border-b">
              <th class="text-left py-1 pr-2">Storage</th>
              <th class="text-right py-1 pl-2">Invest [€]</th>
              <th class="text-right py-1 pl-2">Fixed [€]</th>
              <th class="text-right py-1 pl-2">Fuel [€]</th>
              <th class="text-right py-1 pl-2">Variable [€]</th>
              <th class="text-right py-1 pl-2">CO2 / Env [€]</th>
              <th class="text-right py-1 pl-2">Total [€]</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in storageCostListForCommodity"
              :key="row.name"
              class="border-b last:border-0"
            >
              <td class="py-1 pr-2">{{ row.name }}</td>
              <td class="py-1 pl-2 text-right">
                {{ row.invest.toFixed(0) }}
              </td>
              <td class="py-1 pl-2 text-right">
                {{ row.fixed.toFixed(0) }}
              </td>
              <td class="py-1 pl-2 text-right">
                {{ row.fuel.toFixed(0) }}
              </td>
              <td class="py-1 pl-2 text-right">
                {{ row.variable.toFixed(0) }}
              </td>
              <td class="py-1 pl-2 text-right">
                {{ row.environment.toFixed(0) }}
              </td>
              <td class="py-1 pl-2 text-right">
                {{ row.total.toFixed(0) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSites } from '@/backend/sites'
import { useRoute } from 'vue-router'
import { ref, watch, computed } from 'vue'
import PlotlyDiagram from '@/plotly/PlotlyDiagram.vue'
import DataPoint from '@/pages/simulation/DataPoint.vue'
import { useGetSimulation, useGetSimulationConfig } from '@/backend/simulate'
import type { SimulationsResults } from '@/backend/interfaces'
import SiteResults from '@/pages/simulation/SiteResults.vue'
import Accordion from 'primevue/accordion';
import AccordionPanel from 'primevue/accordionpanel';
import AccordionHeader from 'primevue/accordionheader';
import AccordionContent from 'primevue/accordioncontent';
import { useTransmission } from '@/backend/transmission'
import { chunkAdd, groupOptions } from '@/helper/diagrams'
import {
  convertToDisplayEnergy,
  convertToDisplayMass,
  convertToDisplayPower,
  displayEnergyLabel,
  displayMassLabel,
  displayPowerLabel,
  findCarrierUnits,
  inferDisplayScale,
} from '@/helper/units'
import FloatLabel from 'primevue/floatlabel';
import Select from 'primevue/select';


const route = useRoute()
const { data: sites } = useSites(route)
const { data: simulation } = useGetSimulation(route)
const { data: config } = useGetSimulationConfig(route)
const { data: transmissions } = useTransmission(route)

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

// Per-technology energy (BASE UNIT: MWh) for electricity and heat
const techEnergyElec = ref<Record<string, number>>({})
const techEnergyHeat = ref<Record<string, number>>({})

// Flags indicating whether a technology should receive Fuel costs
// (only if it has at least one input commodity of type Stock or Buy)
const techFuelEligibleElec = ref<Record<string, boolean>>({})
const techFuelEligibleHeat = ref<Record<string, boolean>>({})
// Variable cost input (€/MWh) from project config — used when process_costs is absent
const techVarCostElec = ref<Record<string, number>>({})
const techVarCostHeat = ref<Record<string, number>>({})


// Dropdown selection for which commodity's results to show
const selectedCommodityType = ref('elec') // Default to Electricity

// Display Units dropdown — initialized from the electricity commodity unit
const selectedDisplayUnit = ref('MW')
const displayUnitInitialized = ref(false)

watch(
  config,
  () => {
    if (displayUnitInitialized.value || !config.value) return
    selectedDisplayUnit.value = inferDisplayScale(config.value)
    displayUnitInitialized.value = true
  },
  { immediate: true },
)

const nativeElecUnits = computed(() => findCarrierUnits(config.value, 'elec'))
const nativeHeatUnits = computed(() => findCarrierUnits(config.value, 'heat'))
const nativeCo2Units = computed(() => findCarrierUnits(config.value, 'co2'))
const nativeEnergyUnitC = computed(() =>
  selectedCommodityType.value === 'elec'
    ? nativeElecUnits.value.unitC
    : nativeHeatUnits.value.unitC,
)


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

    // Reset per-technology energy maps
    techEnergyElec.value = {}
    techEnergyHeat.value = {}
    techFuelEligibleElec.value = {}
    techFuelEligibleHeat.value = {}
    techVarCostElec.value = {}
    techVarCostHeat.value = {}


    for (const siteName in simulation.value.result.results) {
      const siteResults = simulation.value.result.results[siteName]
      const siteConfig = config.value['site'][siteName]

      for (const comName in siteResults) {
        // --- Electricity Tracking (base MWh) ---
        // Assuming your simulation data for ELEC created/demand is already in MWh.
        if (comName.toUpperCase().includes('ELEC')) {
          const comResults = siteResults[comName]
          // Technologies are only real processes (from process list)
          for (const procName in comResults.created) {
            // Skip solver-internal helpers that are not in the original process list
            if (!siteConfig.process || !siteConfig.process[procName]) continue
            const procCreated = comResults.created[procName].reduce(
              (a, b) => a + b,
              0,
            )
            const procConfig = siteConfig['process'][procName] || {
              commodity: {},
            }
            elecProduced.value += procCreated
            const techKey = `${siteName} - ${procName}`
            techEnergyElec.value[techKey] =
              (techEnergyElec.value[techKey] || 0) + procCreated

            // Determine if this process should receive Fuel costs
            if (!(techKey in techFuelEligibleElec.value)) {
              let eligible = false
              for (const comKey in procConfig.commodity) {
                const dir = procConfig.commodity[comKey]?.Direction
                if (dir !== 'In') continue
                const comCfg = siteConfig['commodity']?.[comKey]
                if (
                  comCfg &&
                  (comCfg.Type === 'Stock' || comCfg.Type === 'Buy')
                ) {
                  eligible = true
                  break
                }
              }
              techFuelEligibleElec.value[techKey] = eligible
            }
            techVarCostElec.value[techKey] = Number(
              procConfig['var-cost'] ?? procConfig.varcost ?? 0,
            )
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
          // Technologies are only real processes (from process list)
          for (const procName in comResults.created) {
            // Skip solver-internal helpers that are not in the original process list
            if (!siteConfig.process || !siteConfig.process[procName]) continue
            const procCreated = comResults.created[procName].reduce(
              (a, b) => a + b,
              0,
            )
            const procConfig = siteConfig['process'][procName] || {
              commodity: {},
            }
            heatProduced.value += procCreated
            const techKey = `${siteName} - ${procName}`
            techEnergyHeat.value[techKey] =
              (techEnergyHeat.value[techKey] || 0) + procCreated

            // Determine if this process should receive Fuel costs
            if (!(techKey in techFuelEligibleHeat.value)) {
              let eligible = false
              for (const comKey in procConfig.commodity) {
                const dir = procConfig.commodity[comKey]?.Direction
                if (dir !== 'In') continue
                const comCfg = siteConfig['commodity']?.[comKey]
                if (
                  comCfg &&
                  (comCfg.Type === 'Stock' || comCfg.Type === 'Buy')
                ) {
                  eligible = true
                  break
                }
              }
              techFuelEligibleHeat.value[techKey] = eligible
            }
            techVarCostHeat.value[techKey] = Number(
              procConfig['var-cost'] ?? procConfig.varcost ?? 0,
            )
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

// The optimizer reports this cost type as 'Environmental';
// accept the legacy 'Environment' key as fallback
const environmentalCost = computed(() => {
  if (!overview.value) return 0
  return Number(overview.value.Environmental ?? overview.value.Environment ?? 0)
})

// Computed property for Total Cost
const totalCost = computed(() => {
  if (!overview.value) return 0
  return (
    overview.value.Invest +
    overview.value.Fixed +
    overview.value.Fuel +
    overview.value.Variable +
    (overview.value.Purchase || 0) +
    environmentalCost.value
  )
})

// Split total system cost between electricity and heat based on produced energy
const totalElecEnergy = computed(() =>
  Object.values(techEnergyElec.value).reduce(
    (sum, energy) => sum + (energy > 0 ? energy : 0),
    0,
  ),
)

const totalHeatEnergy = computed(() =>
  Object.values(techEnergyHeat.value).reduce(
    (sum, energy) => sum + (energy > 0 ? energy : 0),
    0,
  ),
)

const totalEnergyAll = computed(
  () => totalElecEnergy.value + totalHeatEnergy.value,
)

const elecCostPool = computed(() => {
  if (!totalEnergyAll.value) return 0
  return (totalCost.value * totalElecEnergy.value) / totalEnergyAll.value
})

const heatCostPool = computed(() => {
  if (!totalEnergyAll.value) return 0
  return (totalCost.value * totalHeatEnergy.value) / totalEnergyAll.value
})

// Computed properties to get selected commodity's base data (MWh for energy, tonnes for CO2)
const currentProduced = computed(() => {
  return selectedCommodityType.value === 'elec' ? elecProduced.value : heatProduced.value;
});

const currentFossilProduced = computed(() => {
  return selectedCommodityType.value === 'elec' ? fossilElecProduced.value : fossilHeatProduced.value;
});

const currentConsumed = computed(() => {
  return selectedCommodityType.value === 'elec' ? elecConsumed.value : heatConsumed.value;
});

const currentSlackProduction = computed(() => {
  return selectedCommodityType.value === 'elec' ? slackElecProduction.value : slackHeatProduction.value;
});

// Computed properties for Energy/Mass DISPLAY values and Suffixes
const convertEnergyToDisplayUnit = (value: number) =>
  convertToDisplayEnergy(
    value,
    nativeEnergyUnitC.value,
    selectedDisplayUnit.value as 'kW' | 'MW',
  )

const convertCO2ToDisplayUnit = (value: number) =>
  convertToDisplayMass(
    value,
    nativeCo2Units.value.unitC,
    selectedDisplayUnit.value as 'kW' | 'MW',
  )

const currentProducedDisplay = computed(() => convertEnergyToDisplayUnit(currentProduced.value));
const currentConsumedDisplay = computed(() => convertEnergyToDisplayUnit(currentConsumed.value));
const currentLostDisplay = computed(() => convertEnergyToDisplayUnit(currentProduced.value - currentConsumed.value));

const energySuffix = computed(() =>
  displayEnergyLabel(nativeEnergyUnitC.value, selectedDisplayUnit.value as 'kW' | 'MW'),
)

const co2Suffix = computed(() =>
  displayMassLabel(nativeCo2Units.value.unitC, selectedDisplayUnit.value as 'kW' | 'MW'),
)

const co2SavedDisplay = computed(() => {
  // Baseline: 560 kg CO2 per MWh.
  // currentConsumed.value is now in MWh (base unit).
  const baselineCO2_kg = 560 * currentConsumed.value;

  // co2Produced.value is now in tonnes (base unit). Convert to kg for calculation.
  const actualCO2Produced_kg = co2Produced.value * 1000;

  const savedCO2_kg = baselineCO2_kg - actualCO2Produced_kg;

  // Convert the final saved CO2 to the display unit (kg or tonnes)
  return convertCO2ToDisplayUnit(savedCO2_kg / 1000); // Divide by 1000 to get tonnes, then use convertCO2ToDisplayUnit
});

// Computed property for CO2 Environment output display
const co2EnvironmentDisplay = computed(() => {
  // co2Produced.value is in tonnes (base unit)
  // Convert to display unit (kg or tonnes) based on selectedDisplayUnit
  return convertCO2ToDisplayUnit(co2Produced.value);
});

// --- LCOE / LCOH (Levelized Cost of Energy/Heat) ---
const lcoName = computed(() =>
  selectedCommodityType.value === 'elec' ? 'LCOE' : 'LCOH',
);

// LCO based on delivered/produced energy
const lcoDeliveredValue = computed(() => {
  if (!overview.value) return 0;

  const energy = currentProduced.value
  if (!energy) return 0

  const energyDisplay = convertEnergyToDisplayUnit(energy)
  if (!energyDisplay) return 0
  return totalCost.value / energyDisplay
});

// LCO based on consumed energy (demand)
const lcoConsumedValue = computed(() => {
  if (!overview.value) return 0;

  const energy = currentConsumed.value
  if (!energy) return 0

  const energyDisplay = convertEnergyToDisplayUnit(energy)
  if (!energyDisplay) return 0
  return totalCost.value / energyDisplay
});

const lcoSuffix = computed(() =>
  `€/${energySuffix.value}`,
);

type TechCostRow = {
  name: string
  energy: number
  invest: number
  fixed: number
  fuel: number
  variable: number
  environment: number
  total: number
}

function optimizerCostValue(
  costs: Record<string, number>,
  ...keys: string[]
): number {
  for (const key of keys) {
    if (costs[key] !== undefined && costs[key] !== null) {
      return Number(costs[key])
    }
  }
  return 0
}

/** Per-process costs from optimizer (process_costs), matched to energy carriers. */
function techCostsFromProcessCosts(
  processCostsBySite: Record<string, Record<string, Record<string, number>>>,
  energyByTech: Record<string, number>,
): TechCostRow[] {
  const rows: TechCostRow[] = []
  for (const site in processCostsBySite) {
    const siteObj = processCostsBySite[site] || {}
    for (const pro in siteObj) {
      const name = `${site} - ${pro}`
      const energy = energyByTech[name] ?? 0
      if (energy <= 0) continue
      const c = siteObj[pro] || {}
      const invest = optimizerCostValue(c, 'Invest', 'invest')
      const fixed = optimizerCostValue(c, 'Fixed', 'fixed')
      const fuel = optimizerCostValue(c, 'Fuel', 'fuel')
      const variable = optimizerCostValue(c, 'Variable', 'variable')
      const environment = optimizerCostValue(
        c,
        'Environmental',
        'Environment',
        'environment',
      )
      rows.push({
        name,
        energy,
        invest,
        fixed,
        fuel,
        variable,
        environment,
        total: invest + fixed + fuel + variable + environment,
      })
    }
  }
  return rows.sort((a, b) => b.total - a.total)
}

function allocateTechCostsByCarrierShare(
  energyMap: Record<string, number>,
  totalCarrierEnergy: number,
  carrierCostPool: number,
  fuelEligible: Record<string, boolean>,
  varCost: Record<string, number>,
): TechCostRow[] {
  if (!overview.value) return []

  const entries = Object.entries(energyMap).filter(([, energy]) => energy > 0)
  if (entries.length === 0) return []

  const totalEnergy = entries.reduce((sum, [, energy]) => sum + energy, 0)
  if (
    !totalEnergy ||
    !carrierCostPool ||
    !totalCarrierEnergy ||
    !totalEnergyAll.value
  )
    return []

  const carrierShare = totalCarrierEnergy / totalEnergyAll.value

  const catTotals: Record<
    'Invest' | 'Fixed' | 'Fuel' | 'Variable' | 'Environment',
    number
  > = {
    Invest: overview.value.Invest || 0,
    Fixed: overview.value.Fixed || 0,
    Fuel: overview.value.Fuel || 0,
    Variable: overview.value.Variable || 0,
    Environment: environmentalCost.value,
  }

  const fuelTotalCarrier = catTotals.Fuel * carrierShare
  const fuelDenom = entries.reduce(
    (sum, [name, energy]) =>
      fuelEligible[name] ? sum + energy : sum,
    0,
  )
  const variableTotalCarrier = catTotals.Variable * carrierShare
  const variableDenom = entries.reduce(
    (sum, [name, energy]) =>
      (varCost[name] ?? 0) > 0 ? sum + energy : sum,
    0,
  )

  return entries
    .map(([name, energy]) => {
      const shareInCarrier = energy / totalCarrierEnergy

      const invest = catTotals.Invest * carrierShare * (shareInCarrier || 0)
      const fixed = catTotals.Fixed * carrierShare * (shareInCarrier || 0)
      let fuel = 0
      if (fuelTotalCarrier > 0 && fuelDenom > 0 && fuelEligible[name]) {
        fuel = (fuelTotalCarrier * energy) / fuelDenom
      }
      let variable = 0
      if (
        variableTotalCarrier > 0 &&
        variableDenom > 0 &&
        (varCost[name] ?? 0) > 0
      ) {
        variable = (variableTotalCarrier * energy) / variableDenom
      }
      const environment =
        catTotals.Environment * carrierShare * (shareInCarrier || 0)

      const total = invest + fixed + fuel + variable + environment

      return {
        name,
        energy,
        invest,
        fixed,
        fuel,
        variable,
        environment,
        total,
      }
    })
    .sort((a, b) => b.total - a.total)
}

const processCostsForTech = computed(
  () =>
    (simulation.value?.result?.process_costs as Record<
      string,
      Record<string, Record<string, number>>
    >) || {},
)

// Per-technology costs: optimizer process_costs when available, else energy-share split
const techCostElecList = computed(() => {
  const fromOptimizer = techCostsFromProcessCosts(
    processCostsForTech.value,
    techEnergyElec.value,
  )
  if (fromOptimizer.length) return fromOptimizer

  return allocateTechCostsByCarrierShare(
    techEnergyElec.value,
    totalElecEnergy.value,
    elecCostPool.value,
    techFuelEligibleElec.value,
    techVarCostElec.value,
  )
})

const techCostHeatList = computed(() => {
  const fromOptimizer = techCostsFromProcessCosts(
    processCostsForTech.value,
    techEnergyHeat.value,
  )
  if (fromOptimizer.length) return fromOptimizer

  return allocateTechCostsByCarrierShare(
    techEnergyHeat.value,
    totalHeatEnergy.value,
    heatCostPool.value,
    techFuelEligibleHeat.value,
    techVarCostHeat.value,
  )
})

const techCostCommodityList = computed(() =>
  selectedCommodityType.value === 'heat'
    ? techCostHeatList.value
    : techCostElecList.value,
)

const techCostCommodityLabel = computed(() =>
  selectedCommodityType.value === 'heat' ? 'Heat' : 'Electricity',
)

const commodityStackedData = computed<Partial<Plotly.Data>[]>(() => {
  if (!techCostCommodityList.value.length) return []

  const techs = techCostCommodityList.value
  const names = techs.map(t => t.name)

  const categories: {
    label: string
    color: string
  }[] = [
    { label: 'Invest', color: 'rgb(31, 119, 180)' },
    { label: 'Fixed', color: 'rgb(255, 127, 14)' },
    { label: 'Fuel', color: 'rgb(44, 160, 44)' },
    { label: 'Variable', color: 'rgb(214, 39, 40)' },
    { label: 'CO2 / Environment', color: 'rgb(148, 103, 189)' },
  ]

  const traces: Partial<Plotly.Data>[] = []

  for (const cat of categories) {
    let key: keyof (typeof techs)[number]
    if (cat.label === 'Invest') key = 'invest'
    else if (cat.label === 'Fixed') key = 'fixed'
    else if (cat.label === 'Fuel') key = 'fuel'
    else if (cat.label === 'Variable') key = 'variable'
    else key = 'environment'

    traces.push({
      name: cat.label,
      type: 'bar',
      x: names,
      y: techs.map(t => t[key] as number),
      marker: { color: cat.color },
    })
  }

  return traces
})

// ----- Exact process & storage costs from optimizer (process_costs, storage_costs) -----

const processCosts = computed(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  () => (simulation.value?.result?.process_costs as any) || {},
)

const storageCosts = computed(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  () => (simulation.value?.result?.storage_costs as any) || {},
)

const processCostList = computed(() => {
  const list: {
    name: string
    invest: number
    fixed: number
    fuel: number
    variable: number
    environment: number
    total: number
  }[] = []

  const pc = processCosts.value as Record<
    string,
    Record<string, Record<string, number>>
  >

  for (const site in pc) {
    const siteObj = pc[site] || {}
    for (const pro in siteObj) {
      const c = siteObj[pro] || {}
      const invest = Number(c.Invest || 0)
      const fixed = Number(c.Fixed || 0)
      const fuel = Number(c.Fuel || 0)
      const variable = Number(c.Variable || 0)
      const environment = optimizerCostValue(
        c,
        'Environmental',
        'Environment',
        'environment',
      )
      const total = invest + fixed + fuel + variable + environment
      list.push({
        name: `${site} - ${pro}`,
        invest,
        fixed,
        fuel,
        variable,
        environment,
        total,
      })
    }
  }

  return list.sort((a, b) => b.total - a.total)
})

function storageMatchesCommodityType(
  rowName: string,
  commodityType: 'elec' | 'heat',
): boolean {
  const upper = rowName.toUpperCase()
  const match = upper.match(/\(([^)]+)\)\s*$/)
  const commodityPart = match ? match[1] : upper

  if (commodityType === 'elec') {
    return commodityPart.includes('ELEC')
  }
  return (
    commodityPart.includes('HEAT') ||
    commodityPart.includes('THERMAL') ||
    commodityPart.includes('MJ') ||
    commodityPart.includes('GJ') ||
    commodityPart.includes('KWH_TH')
  )
}

const storageCostList = computed(() => {
  const list: {
    name: string
    invest: number
    fixed: number
    fuel: number
    variable: number
    environment: number
    total: number
  }[] = []

  const sc = storageCosts.value as Record<
    string,
    Record<string, Record<string, number>>
  >

  for (const site in sc) {
    const siteObj = sc[site] || {}
    for (const sto in siteObj) {
      const c = siteObj[sto] || {}
      const invest = Number(c.Invest || 0)
      const fixed = Number(c.Fixed || 0)
      const fuel = Number(c.Fuel || 0)
      const variable = Number(c.Variable || 0)
      const environment = optimizerCostValue(
        c,
        'Environmental',
        'Environment',
        'environment',
      )
      const total = invest + fixed + fuel + variable + environment
      list.push({
        name: `${site} - ${sto}`,
        invest,
        fixed,
        fuel,
        variable,
        environment,
        total,
      })
    }
  }

  return list.sort((a, b) => b.total - a.total)
})

const storageCostListForCommodity = computed(() =>
  storageCostList.value.filter(row =>
    storageMatchesCommodityType(
      row.name,
      selectedCommodityType.value as 'elec' | 'heat',
    ),
  ),
)

// Transmission time resolution selection
const transmissionGroupOption = ref(groupOptions[0])

// Selected transmission (includes canonical flow direction A→B)
const selectedTransmission = ref<{
  key: string
  label: string
  siteA: string
  siteB: string
  commodity: string
} | null>(null)

// Transmission options for dropdown - combine bidirectional pairs
const transmissionOptions = computed(() => {
  if (!transmissions.value) return []
  
  // Group transmissions by site pair and commodity (regardless of direction)
  const transmissionMap = new Map<string, typeof transmissions.value>()
  
  for (const trans of transmissions.value) {
    // Create a key that's the same regardless of direction
    const sites = [trans.sitein, trans.siteout].sort().join(' ↔ ')
    const key = `${sites} (${trans.commodity})`
    
    if (!transmissionMap.has(key)) {
      transmissionMap.set(key, [])
    }
    transmissionMap.get(key)!.push(trans)
  }
  
  // Create options from unique pairs (A→B alphabetical; positive = A→B)
  return Array.from(transmissionMap.entries()).map(([key, transList]) => {
    const trans = transList[0]
    const [siteA, siteB] = [trans.sitein, trans.siteout].sort()
    return {
      key,
      label: `${siteA} → ${siteB} (${trans.commodity})`,
      siteA,
      siteB,
      commodity: trans.commodity,
    }
  })
})

// Auto-select first transmission when options are available
watch(transmissionOptions, (options) => {
  if (options.length > 0 && !selectedTransmission.value) {
    selectedTransmission.value = options[0]
  }
}, { immediate: true })

// Transmission charts - calculate import/export for each site combination
const transmissionCharts = computed(() => {
  if (!simulation.value || !config.value || !transmissions.value) return {}

  const results = simulation.value.result.results
  const charts: {
    [key: string]: {
      data: Partial<Plotly.Data>[]
      unit: string
    }
  } = {}

  const timeline = Array.from(
    { length: transmissionGroupOption.value.groups },
    (_, i) => i + 1,
  )

  // Group transmissions by site pair and commodity (regardless of direction)
  const transmissionMap = new Map<string, typeof transmissions.value>()
  
  for (const trans of transmissions.value) {
    const sites = [trans.sitein, trans.siteout].sort().join(' ↔ ')
    const key = `${sites} (${trans.commodity})`
    
    if (!transmissionMap.has(key)) {
      transmissionMap.set(key, [])
    }
    transmissionMap.get(key)!.push(trans)
  }

  // Process each transmission pair as one signed flow series (A→B positive, B→A negative)
  for (const [chartKey, transList] of transmissionMap.entries()) {
    if (transList.length === 0) continue

    const trans = transList[0]
    const [siteA, siteB] = [trans.sitein, trans.siteout].sort()
    const commodity = trans.commodity

    const rawFlow = extractSignedTransmissionFlow(
      results,
      siteA,
      siteB,
      commodity,
    )
    if (!rawFlow || !rawFlow.some(v => Math.abs(v) > 1e-9)) continue

    let unit = displayPowerLabel(
      undefined,
      selectedDisplayUnit.value as 'kW' | 'MW',
    )
    if (config.value.site?.[siteA]?.commodity?.[commodity]?.unitR) {
      const comConfig = config.value.site[siteA].commodity[commodity]
      unit = displayPowerLabel(
        comConfig.unitR,
        selectedDisplayUnit.value as 'kW' | 'MW',
      )
    }

    const scaledFlow = rawFlow.map(v =>
      convertToDisplayPower(
        v,
        config.value.site?.[siteA]?.commodity?.[commodity]?.unitR,
        selectedDisplayUnit.value as 'kW' | 'MW',
      ),
    )
    const groupedFlow = chunkAdd(
      scaledFlow,
      transmissionGroupOption.value.groupSize,
    )

    charts[chartKey] = {
      data: [
        {
          x: timeline,
          y: groupedFlow,
          type: 'bar',
          showlegend: false,
          marker: { color: 'rgb(44, 160, 44)' },
        },
      ],
      unit,
    }
  }

  return charts
})

function getDirectionalTransmissionFlow(
  results: SimulationsResults['results'],
  fromSite: string,
  toSite: string,
  commodity: string,
): number[] | null {
  const fromResults = results[fromSite]?.[commodity]
  const toResults = results[toSite]?.[commodity]

  const exported = fromResults?.exported?.[toSite]
  if (Array.isArray(exported) && exported.length > 0) {
    return exported
  }

  const imported = toResults?.imported?.[fromSite]
  if (Array.isArray(imported) && imported.length > 0) {
    return imported
  }

  return null
}

/** Signed flow: positive = siteA→siteB, negative = siteB→siteA. */
function extractSignedTransmissionFlow(
  results: SimulationsResults['results'],
  siteA: string,
  siteB: string,
  commodity: string,
): number[] | null {
  const flowAToB = getDirectionalTransmissionFlow(
    results,
    siteA,
    siteB,
    commodity,
  )
  const flowBToA = getDirectionalTransmissionFlow(
    results,
    siteB,
    siteA,
    commodity,
  )

  if (!flowAToB && !flowBToA) return null

  const len = Math.max(flowAToB?.length ?? 0, flowBToA?.length ?? 0)
  if (len === 0) return null

  const signed: number[] = []
  for (let i = 0; i < len; i++) {
    const ab = flowAToB?.[i] ?? 0
    const ba = flowBToA?.[i] ?? 0
    signed.push(ab - ba)
  }

  if (!signed.some(v => Math.abs(v) > 1e-9)) return null
  return signed
}

</script>

<style scoped></style>
