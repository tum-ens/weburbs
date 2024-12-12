<template>
  <Card>
    <template #title>
      <div class="flex flex-row justify-between">
        <span>Simulations</span>
        <div class="flex flex-row gap-3">
          <Select
            v-model="selSimulation"
            :options="simulations"
            placeholder="Select a simulation"
            empty-message="No simulation found yet"
          >
            <template #option="{ option }">
              <div
                class="w-full flex flex-row justify-between items-center gap-3"
              >
                <span>{{ option.timestamp.toLocaleString() }}</span>
                <ResultIcon
                  :completed="option.completed"
                  :status="option.status"
                />
              </div>
            </template>
            <template #value="{ value, placeholder }">
              <div
                v-if="value"
                class="w-full flex flex-row justify-between items-center gap-3"
              >
                <span>{{ value.timestamp.toLocaleString() }}</span>
                <ResultIcon
                  :completed="value.completed"
                  :status="value.status"
                />
              </div>
              <span v-else>{{ placeholder }}</span>
            </template>
          </Select>
          <Button
            icon="pi pi-caret-right"
            label="Simulate"
            :loading="simulating"
            @click="trigger"
          />
        </div>
      </div>
    </template>
    <template #content>
      <template
        v-if="
          resultsExist &&
          simulation &&
          simulation.status === SimulationResultStatus.Optimal
        "
      >
        <div class="flex flex-col gap-3">
          <div class="grid grid-cols-4 gap-3">
            <Fieldset legend="Overview">
              <ul>
                <li>Environmental: {{ overview.Environmental }}</li>
                <li>Fixed: {{ overview.Invest }}</li>
                <li>Fuel: {{ overview.Fuel }}</li>
                <li>Invest: {{ overview.Invest }}</li>
                <li>Variable: {{ overview.Variable }}</li>
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
            <AccordionPanel
              v-for="site in sites"
              :key="site.name"
              :value="site.name"
            >
              <AccordionHeader>{{ site.name }}</AccordionHeader>
              <AccordionContent>
                <SiteResults
                  v-if="site.name in demand && site.name in created"
                  :site="site"
                  :demand="demand[site.name]"
                  :created="created[site.name]"
                  :storageLevel="
                    site.name in storageLevel
                      ? storageLevel[site.name]
                      : undefined
                  "
                />
              </AccordionContent>
            </AccordionPanel>
          </Accordion>
        </div>
      </template>
      <div v-else-if="!selSimulation">Select a simulation</div>
      <div
        v-else-if="simulation"
        class="flex flex-col gap-3 items-center justify-start"
      >
        <template v-if="simulation.status === SimulationResultStatus.Optimal">
          <ProgressSpinner />
          <span>Waiting for results...</span>
        </template>
        <template v-else> The simulation run into an error. </template>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import {
  useGetSimulation,
  useListSimulations,
  useTriggerSimulation,
} from '@/backend/simulate'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import type { AxiosError } from 'axios'
import { ref, watch } from 'vue'
import { useSites } from '@/backend/sites'
import Plotly from 'plotly.js-dist'
import SiteResults from '@/pages/simulation/SiteResults.vue'
import { chunkAdd, chunkAvg, groupOptions } from '@/helper/diagrams'
import ResultIcon from '@/pages/simulation/ResultIcon.vue'
import {
  type SimulationResult,
  SimulationResultStatus,
} from '@/backend/interfaces'

const route = useRoute()
const toast = useToast()

const selSimulation = ref<SimulationResult>()
const resultsExist = ref(false)

const { data: sites } = useSites(route)
const { mutate: triggerSimulation, isPending: simulating } =
  useTriggerSimulation(route)
const { data: simulations } = useListSimulations(route)
const { data: simulation } = useGetSimulation(route, selSimulation)

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

function trigger() {
  triggerSimulation(undefined, {
    onSuccess(data) {
      selSimulation.value = data
      toast.add({
        summary: 'Success',
        detail: 'Simulation started',
        severity: 'success',
        life: 2000,
      })
    },
    onError(error) {
      console.log(error)
      toast.add({
        summary: 'Simulation could not be started',
        detail: (<AxiosError>error)?.response?.data,
        severity: 'error',
        life: 2000,
      })
    },
  })
}

watch(
  simulations,
  () => {
    if (selSimulation.value || !simulations.value) return

    selSimulation.value = simulations.value[0]
  },
  { immediate: true },
)

watch(simulation, () => {
  if (!simulation.value) {
    resultsExist.value = false
    return
  }
  console.log(simulation.value.status)
  if (selSimulation.value) {
    selSimulation.value = {
      ...selSimulation.value,
      completed: true,
      status: simulation.value.status,
    }
  }
  resultsExist.value = true

  procs.value = []
  overview.value = simulation.value.result.costs
  for (const site in simulation.value.result.process) {
    for (const proc in simulation.value.result.process[site]) {
      procs.value.push({
        site,
        proc,
        total: simulation.value.result.process[site][proc].Total,
        new: simulation.value.result.process[site][proc].New,
      })
    }
  }

  demand.value = {}
  created.value = {}
  storageLevel.value = {}
  for (const site in simulation.value.result.results) {
    demand.value[site] = {}
    created.value[site] = {}
    storageLevel.value[site] = {}
    for (const com in simulation.value.result.results[site]) {
      demand.value[site][com] = [
        {
          name: com,
          y: chunkAdd(
            simulation.value.result.results[site][com].demand,
            groupOptions[0].groupSize,
          ),
          x: Array.from({ length: groupOptions[0].groupSize }, (_, i) => i + 1),
          type: 'bar',
        },
      ]
      created.value[site][com] = []
      for (const proc in simulation.value.result.results[site][com].created) {
        created.value[site][com].push({
          name: proc,
          y: chunkAdd(
            simulation.value.result.results[site][com].created[proc],
            groupOptions[0].groupSize,
          ),
          x: Array.from({ length: groupOptions[0].groupSize }, (_, i) => i + 1),
          type: 'bar',
        })
      }
      if (simulation.value.result.results[site][com].storage) {
        storageLevel.value[site][com] = [
          {
            name: com,
            y: chunkAvg(
              simulation.value.result.results[site][com].storage.Level,
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
})
</script>

<style scoped></style>
