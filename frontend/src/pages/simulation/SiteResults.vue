<template>
  <div
    class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 items-center"
  >
    <div>
      <PlotlyDiagram
        v-if="procCapacity"
        title="Processes"
        :data="procCapacity"
        :bargap="0.6"
        :titleX="procUnitR || 'MW'"
        :margin="{
          t: 150,
          l: 100,
        }"
      />
    </div>
    <div class="grid grid-cols-2 xl:grid-cols-3 gap-3 justify-items-center">
      <DataPoint
        v-for="proc in newProcs"
        :key="proc.name"
        :name="proc.name"
        :value="proc.value"
        :suffix="proc.suffix"
      />
      <DataPoint
        v-for="stor in newStor"
        :key="stor.name"
        :name="stor.name"
        :value="stor.value"
        :suffix="stor.suffix"
      />
      <DataPoint
        name="Storage cycles per year"
        :value="storCapNative ? storRetrieved / storCapNative : 0"
        suffix=""
      />
    </div>
    <div>
      <PlotlyDiagram
        v-if="storCapPow"
        title="Storage"
        :data="storCapPow"
        :bargap="0.6"
        :titleX="storUnitC?.join(' / ') || 'MWh'"
        :titleX2="storUnitR?.join(' / ') || 'MW'"
        :margin="{
          t: 150,
          l: 150,
        }"
      />
    </div>
    <FloatLabel variant="on" class="col-span-1">
      <Select
        fluid
        id="groupoptions"
        :options="groupOptions"
        optionLabel="name"
        v-model="groupOption"
      />
      <label for="groupoptions">Group values</label>
    </FloatLabel>
    <div v-if="commodityDetails" class="md:col-span-2 xl:col-span-3">
      <PlotlyDiagram
        v-for="(data, comName) in commodityDetails"
        :key="comName"
        :title="<string>comName"
        :data="data.data"
        :titleY="data.unitC"
        barmode="relative"
        :bargroupgap="0.2"
        :margin="{
          t: 150,
        }"
      />
    </div>

    <div class="md:col-span-2 xl:grid-cols-3 grid grid-cols-1 gap-3">
      <FloatLabel variant="on" class="w-full md:w-1/2 xl:w-1/3">
        <Select
          fluid
          id="commodityoptions"
          :options="demandCommodityOptions"
          v-model="selectedCommodity"
        />
        <label for="commodityoptions"
          >Select Commodity for Production View</label
        >
      </FloatLabel>
      <div v-if="selectedCommodity" class="w-full md:col-span-2">
        <PlotlyDiagram
          v-if="annualProductionData && annualProductionData.length > 0"
          :title="productionChartTitle"
          :data="annualProductionData"
          :titleX="annualProductionUnit"
          :bargap="0.5"
          :xaxis-range="annualProductionXRange"
          :margin="{
            t: 150,
            l: 150,
            r: 50,
            b: 50,
          }"
        />
        <div v-else class="flex items-center justify-center p-8 text-gray-500">
          <p>No production data available for {{ selectedCommodity }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Site } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import { inject, type Ref, ref, watch, computed } from 'vue'
import { useGetSimulation, useGetSimulationConfig } from '@/backend/simulate'
import PlotlyDiagram from '@/plotly/PlotlyDiagram.vue'
import DataPoint from '@/pages/simulation/DataPoint.vue'
import { chunkAdd, groupOptions } from '@/helper/diagrams'
import {
  convertToDisplayEnergy,
  convertToDisplayPower,
  displayEnergyLabel,
  displayPowerLabel,
  processOutputUnit,
  siteDemandPowerUnit,
  type DisplayScale,
} from '@/helper/units'

const route = useRoute()

const props = defineProps<{
  site: Site
  selectedDisplayUnit?: string
}>()

const advanced = inject<Ref<boolean>>('advanced')

const { data: simulation } = useGetSimulation(route)
const { data: config } = useGetSimulationConfig(route)

const displayScale = computed<DisplayScale | undefined>(() =>
  props.selectedDisplayUnit === 'kW' || props.selectedDisplayUnit === 'MW'
    ? props.selectedDisplayUnit
    : undefined,
)

const procCapacity = ref<Partial<Plotly.Data>[]>()
const procUnitR = ref('MW')
const newProcs = ref<{ name: string; value: number; suffix: string }[]>([])
const storCapNative = ref(0)
const annualProductionUnit = ref('MWh')

const storCapPow = ref<Partial<Plotly.Data>[]>()
const storUnitR = ref<string[]>()
const storUnitC = ref<string[]>()
const newStor = ref<{ name: string; value: number; suffix: string }[]>([])
const storRetrieved = ref(0)

const commodityDetails = ref<{
  [key: string]: { unitR: string; unitC: string; data: Partial<Plotly.Data>[] }
}>({})

const groupOption = ref(groupOptions[0])

// Refs for the annual production chart
const demandCommodityOptions = ref<string[]>([])
const selectedCommodity = ref<string>()
const annualProductionData = ref<Partial<Plotly.Data>[]>()
const annualProductionXRange = ref<[number, number] | undefined>()

const productionChartTitle = computed(() => {
  const com = selectedCommodity.value || 'commodity'
  const rc = config.value?.run_config
  if (rc && (rc.timestep_from !== undefined || rc.timestep_to !== undefined)) {
    const from = rc.timestep_from ?? 0
    const to = rc.timestep_to ?? (config.value?.c_timesteps ?? 1) - 1
    return `Production for ${com} (timesteps ${from}–${to})`
  }
  return `Annual Production for ${com}`
})

const timeseriesCommodityTypes = computed(() => {
  const types = config.value?.run_config?.timeseries_commodity_types
  if (Array.isArray(types)) return types as string[]
  return ['Demand']
})

watch(
  [
    simulation,
    config,
    advanced,
    groupOption,
    selectedCommodity,
    () => props.selectedDisplayUnit,
  ],
  () => {
    // Resetting values on each change
    newProcs.value = []
    procCapacity.value = []
    procUnitR.value = 'MW'
    newStor.value = []
    storCapPow.value = []
    storUnitR.value = []
    storUnitC.value = []
    commodityDetails.value = {}
    annualProductionData.value = undefined
    demandCommodityOptions.value = []
    storRetrieved.value = 0
    storCapNative.value = 0
    annualProductionUnit.value = 'MWh'

    if (!simulation.value || !config.value) return

    const siteConfig = config.value.site[props.site.name]
    const siteResults = simulation.value.result
    const commodities = siteConfig.commodity || {}
    const scale = displayScale.value
    const fallbackPower = siteDemandPowerUnit(commodities) || 'MW'

    // Init processes — every process at this site, independent of the
    // electricity / heat KPI dropdown at the top of the results page.
    {
      const procsNew = []
      const procsInstalled = []
      const procsNames = []
      const procUnits = new Set<string>()
      const shown = Object.keys(siteResults.process?.[props.site.name] || {})
      for (const procName of shown) {
        const procConf = siteConfig.process?.[procName]
        if (!procConf) continue
        let allIn = true
        let allOut = true
        for (const procConfName in procConf['commodity']) {
          const dir = procConf['commodity'][procConfName].Direction
          allIn &&= dir === 'In'
          allOut &&= dir === 'Out'
        }
        if (!advanced?.value && (allIn || allOut)) continue

        const proc = siteResults.process[props.site.name][procName]
        const nativeUnit =
          processOutputUnit(procConf, commodities).unitR || fallbackPower
        const suffix = displayPowerLabel(nativeUnit, scale)
        procUnits.add(suffix)
        procsNew.push(convertToDisplayPower(proc.New, nativeUnit, scale))
        procsInstalled.push(
          convertToDisplayPower(proc.Total - proc.New, nativeUnit, scale),
        )
        procsNames.push(procName)

        newProcs.value.push({
          name: procName,
          value: convertToDisplayPower(proc.Total, nativeUnit, scale),
          suffix,
        })
      }
      procUnitR.value =
        procUnits.size === 1
          ? [...procUnits][0]
          : [...procUnits].join(' / ') ||
            displayPowerLabel(fallbackPower, scale)
      procCapacity.value = [
        {
          name: 'Installed Capacity',
          x: procsInstalled,
          y: procsNames,
          type: 'bar',
          orientation: 'h',
        },
        {
          name: 'New Capacity',
          x: procsNew,
          y: procsNames,
          type: 'bar',
          orientation: 'h',
        },
      ]
    }

    // Init storage — every storage at this site (electricity and heat).
    {
      const storCNew = []
      const storCInstalled = []
      const storPNew = []
      const storPInstalled = []
      const storNames = []
      const storageByCom = siteResults.storage?.[props.site.name] || {}
      const qualifyStor = Object.keys(storageByCom).length > 1
      for (const comName in storageByCom) {
        const storCom = storageByCom[comName]
        for (const storName in storCom) {
          const stor = storCom[storName]

          const com = siteConfig.commodity[comName]
          storCNew.push(convertToDisplayEnergy(stor.CNew, com.unitC, scale))
          storCInstalled.push(
            convertToDisplayEnergy(stor.CTotal - stor.CNew, com.unitC, scale),
          )
          storPNew.push(convertToDisplayPower(stor.PNew, com.unitR, scale))
          storPInstalled.push(
            convertToDisplayPower(stor.PTotal - stor.PNew, com.unitR, scale),
          )
          const label = qualifyStor ? `${storName} (${comName})` : storName
          storNames.push(label)

          storCapNative.value += stor.CTotal
          newStor.value.push({
            name: label,
            value: convertToDisplayEnergy(stor.CTotal, com.unitC, scale),
            suffix: displayEnergyLabel(com.unitC, scale),
          })
          storUnitR.value.push(displayPowerLabel(com.unitR, scale))
          storUnitC.value.push(displayEnergyLabel(com.unitC, scale))
        }
      }
      storCapPow.value = [
        {
          name: 'Installed Capacity',
          x: storCInstalled,
          y: storNames,
          type: 'bar',
          xaxis: 'x1',
          orientation: 'h',
        },
        {
          name: 'New Capacity',
          x: storCNew,
          y: storNames,
          type: 'bar',
          xaxis: 'x1',
          orientation: 'h',
        },
        {
          name: 'Installed Power',
          x: storPInstalled,
          y: storNames,
          type: 'scatter',
          mode: 'markers',
          marker: {
            symbol: 25,
            size: 15,
          },
          xaxis: 'x2',
          orientation: 'h',
        },
        {
          name: 'New Power',
          x: storPNew,
          y: storNames,
          type: 'scatter',
          mode: 'markers',
          marker: {
            symbol: 25,
            size: 15,
          },
          xaxis: 'x2',
          orientation: 'h',
        },
      ]
    }

    // Init commodity details (timeseries)
    const results = siteResults.results[props.site.name]
    const timeline = Array.from(
      { length: groupOption.value.groups },
      (_, i) => i + 1,
    )
    const hasFlow = (series?: number[]) =>
      Array.isArray(series) && series.some(v => Math.abs(v) > 1e-9)

    // Iterate the site's configured commodities and chart those whose type
    // was selected when the simulation was started.
    for (const comName in siteConfig.commodity) {
      const com = siteConfig.commodity[comName]
      const comType = String(com.Type || com.type || '')
      const selectedTypes = timeseriesCommodityTypes.value.map(t =>
        String(t).toLowerCase(),
      )
      if (!selectedTypes.includes(comType.toLowerCase())) continue

      // Annual production view stays demand-only.
      if (comType === 'Demand') {
        demandCommodityOptions.value.push(comName)
      }

      // Result data may be missing entirely when nothing was simulated for it.
      const comResults = results?.[comName]

      // Track total retrieved energy for the "Storage cycles per year" metric.
      storRetrieved.value += (comResults?.storage?.Retrieved ?? []).reduce(
        (acc, num) => acc + num,
        0,
      )

      const scaleEnergy = (arr: number[]) =>
        arr.map(v => convertToDisplayEnergy(v, com.unitC, scale))

      const traces: Partial<Plotly.Data>[] = []

      // Production per process (positive bars); skip all-zero series.
      for (const procName in comResults?.created ?? {}) {
        const series = scaleEnergy(
          chunkAdd(comResults!.created[procName], groupOption.value.groupSize),
        )
        if (!hasFlow(series)) continue
        traces.push({
          name: procName,
          x: timeline,
          y: series,
          type: 'bar',
          yaxis: 'y1',
        })
      }

      // Process consumption (Grid Sell, curtailment, …) as negative bars,
      // matching storage charging / export.
      for (const procName in comResults?.consumed ?? {}) {
        const series = scaleEnergy(
          chunkAdd(
            comResults!.consumed![procName],
            groupOption.value.groupSize,
            -1,
          ),
        )
        if (!hasFlow(series)) continue
        traces.push({
          name: procName,
          x: timeline,
          y: series,
          type: 'bar',
          yaxis: 'y1',
        })
      }

      // Storage retrieved (positive) and stored (negative); no Level.
      const retrieved = scaleEnergy(
        chunkAdd(
          comResults?.storage?.Retrieved ?? [],
          groupOption.value.groupSize,
        ),
      )
      if (hasFlow(retrieved)) {
        traces.push({
          name: 'Storage retrieved',
          x: timeline,
          y: retrieved,
          type: 'bar',
          yaxis: 'y1',
        })
      }
      const stored = scaleEnergy(
        chunkAdd(
          comResults?.storage?.Stored ?? [],
          groupOption.value.groupSize,
          -1,
        ),
      )
      if (hasFlow(stored)) {
        traces.push({
          name: 'Storage stored',
          x: timeline,
          y: stored,
          type: 'bar',
          yaxis: 'y1',
        })
      }

      // Import from neighbouring sites (positive bars); skip all-zero series.
      for (const sourceSite in comResults?.imported ?? {}) {
        const series = scaleEnergy(
          chunkAdd(
            comResults!.imported![sourceSite],
            groupOption.value.groupSize,
          ),
        )
        if (!hasFlow(series)) continue
        traces.push({
          name: `Import from ${sourceSite}`,
          x: timeline,
          y: series,
          type: 'bar',
          yaxis: 'y1',
        })
      }

      // Export to neighbouring sites (negative bars); skip all-zero series.
      for (const destSite in comResults?.exported ?? {}) {
        const series = scaleEnergy(
          chunkAdd(
            comResults!.exported![destSite],
            groupOption.value.groupSize,
            -1,
          ),
        )
        if (!hasFlow(series)) continue
        traces.push({
          name: `Export to ${destSite}`,
          x: timeline,
          y: series,
          type: 'bar',
          yaxis: 'y1',
        })
      }

      // Demand line: always for Demand commodities; otherwise only if present.
      const demandRaw = comResults?.demand ?? []
      const demand = scaleEnergy(
        demandRaw.length
          ? chunkAdd(demandRaw, groupOption.value.groupSize)
          : new Array(groupOption.value.groups).fill(0),
      )
      if (comType === 'Demand' || hasFlow(demand)) {
        traces.push({
          name: comType === 'Demand' ? 'Demand' : comType,
          x: timeline,
          y: demand,
          type: 'scatter',
          yaxis: 'y1',
        })
      }

      if (!traces.length) continue

      const chartName =
        timeseriesCommodityTypes.value.length === 1 &&
        timeseriesCommodityTypes.value[0] === 'Demand'
          ? comName
          : `${comName} (${comType})`
      commodityDetails.value[chartName] = {
        unitR: displayPowerLabel(com.unitR, scale),
        unitC: displayEnergyLabel(com.unitC, scale),
        data: traces,
      }
    }

    // Logic for Annual Production Chart
    {
      // Validate and set selected commodity
      if (demandCommodityOptions.value.length > 0) {
        // If no commodity is selected, or the selected one is no longer valid, set to first available
        if (
          !selectedCommodity.value ||
          !demandCommodityOptions.value.includes(selectedCommodity.value)
        ) {
          selectedCommodity.value = demandCommodityOptions.value[0]
        }
      } else {
        // No demand commodities available, clear selection
        selectedCommodity.value = undefined
      }

      // Reset annual production data first
      annualProductionData.value = undefined
      annualProductionXRange.value = undefined

      if (
        selectedCommodity.value &&
        results &&
        results[selectedCommodity.value]
      ) {
        const commodityResult = results[selectedCommodity.value]
        annualProductionUnit.value = displayEnergyLabel(
          siteConfig.commodity[selectedCommodity.value]?.unitC,
          scale,
        )

        // Check if created property exists
        if (commodityResult && commodityResult.created) {
          const productionByProcess = commodityResult.created

          // Check if created data exists and is not empty
          if (
            productionByProcess &&
            typeof productionByProcess === 'object' &&
            !Array.isArray(productionByProcess)
          ) {
            const processNames: string[] = []
            const productionTotals: number[] = []

            for (const procName in productionByProcess) {
              if (productionByProcess.hasOwnProperty(procName)) {
                const processProduction = productionByProcess[procName]
                // Ensure it's an array and has values
                if (
                  Array.isArray(processProduction) &&
                  processProduction.length > 0
                ) {
                  const yearlyProduction = processProduction.reduce(
                    (sum, current) => sum + (current || 0),
                    0,
                  )
                  const nativeUnitC =
                    siteConfig.commodity[selectedCommodity.value]?.unitC
                  const displayProduction = convertToDisplayEnergy(
                    yearlyProduction,
                    nativeUnitC,
                    scale,
                  )

                  // Only add processes with non-zero production
                  if (displayProduction > 0) {
                    processNames.push(procName)
                    productionTotals.push(displayProduction)
                  }
                }
              }
            }

            if (processNames.length > 0) {
              // Calculate x-axis range to make bars clearly visible
              const maxValue = Math.max(...productionTotals)
              const minValue = 0

              // Ensure bars take up a significant portion of the chart
              // Use a multiplier that ensures bars are clearly visible
              // If maxValue is very small, scale it up more aggressively
              let multiplier = 1.5 // Default: bars take up ~67% of chart

              if (maxValue < 0.1) {
                multiplier = 3.0 // For very small values, scale up more
              } else if (maxValue < 1) {
                multiplier = 2.0 // For small values, scale up
              }

              const rangeMax = maxValue * multiplier

              annualProductionXRange.value = [minValue, rangeMax]

              console.log('Annual Production Data:', {
                processNames,
                productionTotals,
                selectedCommodity: selectedCommodity.value,
                xRange: annualProductionXRange.value,
              })

              annualProductionData.value = [
                {
                  name: 'Annual Production',
                  x: productionTotals,
                  y: processNames,
                  type: 'bar',
                  orientation: 'h',
                },
              ]
            } else {
              annualProductionXRange.value = undefined
              console.log(
                'No processes found with production for:',
                selectedCommodity.value,
                {
                  productionByProcess,
                  commodityResult,
                },
              )
            }
          }
        }
      }
    }
  },
  {
    immediate: true,
  },
)
</script>

<style scoped></style>
