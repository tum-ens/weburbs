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
        titleX="kW"
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
        suffix="kW"
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
        :value="
          storRetrieved / newStor.map(s => s.value).reduce((a, b) => a + b, 0)
        "
        suffix=""
      />
    </div>
    <div>
      <PlotlyDiagram
        v-if="storCapPow"
        title="Storage"
        :data="storCapPow"
        :bargap="0.6"
        :titleX="storUnitC?.join(' / ') || 'kWh'"
        :titleX2="storUnitR?.join(' / ') || 'kW'"
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
        :bargroupgap="0.2"
        :margin="{
          t: 150,
        }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Site } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import { inject, type Ref, ref, watch } from 'vue'
import { useGetSimulation, useGetSimulationConfig } from '@/backend/simulate'
import PlotlyDiagram from '@/plotly/PlotlyDiagram.vue'
import DataPoint from '@/pages/simulation/DataPoint.vue'
import { chunkAdd, groupOptions } from '@/helper/diagrams'

const route = useRoute()

const props = defineProps<{
  site: Site
}>()

const advanced = inject<Ref<boolean>>('advanced')

const { data: simulation } = useGetSimulation(route)
const { data: config } = useGetSimulationConfig(route)

const procCapacity = ref<Partial<Plotly.Data>[]>()
const newProcs = ref<{ name: string; value: number }[]>([])

const storCapPow = ref<Partial<Plotly.Data>[]>()
const storUnitR = ref<string[]>()
const storUnitC = ref<string[]>()
const newStor = ref<{ name: string; value: number; suffix: string }[]>([])
const storRetrieved = ref(0)

const commodityDetails = ref<{
  [key: string]: { unitR: string; unitC: string; data: Partial<Plotly.Data>[] }
}>({})

const groupOption = ref(groupOptions[0])

watch(
  [simulation, advanced, groupOption],
  () => {
    newProcs.value = []
    procCapacity.value = []
    newStor.value = []
    storCapPow.value = []
    storUnitR.value = []
    storUnitC.value = []
    if (!simulation.value || !config.value) return

    // Init processes
    {
      const procsNew = []
      const procsInstalled = []
      const procsNames = []
      for (const procName in simulation.value.result.process[props.site.name]) {
        const procConf =
          config.value['site'][props.site.name]['process'][procName]
        let allIn = true
        let allOut = true
        for (const procConfName in procConf['commodity']) {
          const dir = procConf['commodity'][procConfName].Direction
          allIn &&= dir === 'In'
          allOut &&= dir === 'Out'
        }
        if (!advanced?.value && (allIn || allOut)) continue

        const proc = simulation.value.result.process[props.site.name][procName]
        procsNew.push(proc.New)
        procsInstalled.push(proc.Total - proc.New)
        procsNames.push(procName)

        newProcs.value.push({ name: procName, value: proc.New })
      }
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

    // Init storage
    {
      const storCNew = []
      const storCInstalled = []
      const storPNew = []
      const storPInstalled = []
      const storNames = []
      for (const comName in simulation.value.result.storage[props.site.name]) {
        const storCom =
          simulation.value.result.storage[props.site.name][comName]
        for (const storName in storCom) {
          const stor = storCom[storName]

          storCNew.push(stor.CNew)
          storCInstalled.push(stor.CTotal - stor.CNew)
          storPNew.push(stor.PNew)
          storPInstalled.push(stor.PTotal - stor.PNew)
          storNames.push(storName)

          const com = config.value.site[props.site.name].commodity[comName]
          newStor.value.push({
            name: storName,
            value: stor.CNew,
            suffix: com.unitC,
          })
          storUnitR.value.push(com.unitR)
          storUnitC.value.push(com.unitC)
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

    const results = simulation.value.result.results[props.site.name]
    const timeline = Array.from(
      { length: groupOption.value.groups },
      (_, i) => i + 1,
    )
    for (const comName in results) {
      const com = config.value.site[props.site.name].commodity[comName]
      if (com.Type !== 'Demand') continue

      const comResults = results[comName]
      commodityDetails.value[comName] = {
        unitR: com.unitR,
        unitC: com.unitC,
        data: [
          {
            name: 'Demand',
            x: timeline,
            y: chunkAdd(comResults.demand, groupOption.value.groupSize),
            type: 'scatter',
            yaxis: 'y1',
          },
        ],
      }
      if (groupOption.value.groupSize === 1)
        commodityDetails.value[comName].data.push({
          name: 'Storage',
          x: timeline,
          y: chunkAdd(comResults.storage.Level, groupOption.value.groupSize),
          type: 'scatter',
          yaxis: 'y2',
        })
      storRetrieved.value = comResults.storage.Retrieved.reduce(
        (acc, num) => acc + num,
        0,
      )
      for (const procName in comResults.created) {
        commodityDetails.value[comName].data.push({
          name: procName,
          x: timeline,
          y: chunkAdd(
            comResults.created[procName],
            groupOption.value.groupSize,
          ),
          type: 'bar',
          yaxis: 'y1',
        })
      }
    }
  },
  {
    immediate: true,
  },
)
</script>

<style scoped></style>
