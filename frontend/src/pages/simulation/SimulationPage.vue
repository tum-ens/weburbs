<template>
  <Card>
    <template #title>
      <div class="flex flex-col xl:flex-row justify-between gap-3">
        <span>Simulations</span>
        <div class="grid grid-cols-2 md:flex md:flex-row gap-3">
          <Button
            v-if="simulation && simulation.xlsx"
            severity="info"
            icon="pi pi-download"
            label="XLSX"
            @click="download('xlsx')"
          />
          <Button
            v-if="simulation && simulation.h5"
            severity="info"
            icon="pi pi-download"
            label="h5"
            @click="download('h5')"
          />
          <Button
            v-if="advanced && selSimulation"
            severity="info"
            label="Configuration"
            @click="configVisible = true"
          />
          <Button
            v-if="advanced && selSimulation"
            severity="info"
            label="Logs"
            @click="logsVisible = true"
          />
          <Inplace
            v-if="selSimulation"
            :displayProps="{ class: 'border-box-sizing flex h-full p-0' }"
            :pt="{ content: { class: 'border-box-sizing flex h-full p-0' } }"
          >
            <template #display>
              <Button label="Change name" />
            </template>
            <template #content="{ closeCallback }">
              <InputGroup fluid>
                <InputText
                  fluid
                  v-model="simName"
                  @keyup.enter="updateName(closeCallback)"
                />
                <Button
                  fluid
                  label="Update"
                  @click="updateName(closeCallback)"
                />
              </InputGroup>
            </template>
          </Inplace>
          <Select
            class="col-span-2"
            v-model="selSimulation"
            :options="simulations"
            placeholder="Select a simulation"
            empty-message="No simulation found yet"
            @change="changeSimulation"
          >
            <template #option="{ option }">
              <div
                class="w-full flex flex-row justify-between items-center gap-3"
              >
                <span>{{
                  option.name || option.timestamp.toLocaleString()
                }}</span>
                <ResultIcon
                  :completed="option.completed"
                  :status="option.status || SimulationResultStatus.Optimal"
                />
              </div>
            </template>
            <template #value="{ value, placeholder }">
              <div
                v-if="value"
                class="w-full flex flex-row justify-between items-center gap-3"
              >
                <span>{{
                  value.name || value.timestamp.toLocaleString()
                }}</span>
                <ResultIcon
                  :completed="value.completed"
                  :status="value.status || SimulationResultStatus.Optimal"
                />
              </div>
              <span v-else>{{ placeholder }}</span>
            </template>
          </Select>
          <Button
            v-if="advanced"
            class="col-span-2"
            icon="pi pi-caret-right"
            label="Configure simulation"
            :loading="simulating"
            @click="configSimulation"
          />
          <Button
            v-else
            class="col-span-2"
            icon="pi pi-caret-right"
            label="Simulate"
            :loading="simulating"
            @click="trigger"
          />
          <Popover ref="simulatePop">
            <div class="flex flex-col gap-3">
              <SelectButton
                fluid
                v-model="generate_report"
                :allow-empty="false"
                optionLabel="label"
                optionValue="value"
                :options="[
                  { label: 'No report', value: undefined },
                  { label: 'Report', value: GenerateReport.SUMMARY },
                  { label: 'With timeseries', value: GenerateReport.FULL },
                ]"
              />
              <SelectButton
                :pt="{ root: 'w-full', pcToggleButton: { root: 'flex-1' } }"
                v-model="generate_h5"
                :allow-empty="false"
                optionLabel="label"
                optionValue="value"
                :options="[
                  { label: 'No h5', value: undefined },
                  { label: 'Generate h5', value: true },
                ]"
              />
              <div class="flex flex-row justify-end">
                <Button
                  label="Simulate"
                  :loading="simulating"
                  @click="
                    () => {
                      trigger()
                      simulatePop?.hide()
                    }
                  "
                />
              </div>
            </div>
          </Popover>
        </div>
      </div>
    </template>
    <template #content>
      <template v-if="route.params.simId">
        <div
          v-if="!simulation"
          class="flex flex-col gap-3 items-center justify-start"
        >
          <ProgressSpinner />
          <span>Waiting for results...</span>
        </div>
        <div v-else-if="simulation.status !== SimulationResultStatus.Optimal">
          The simulation ran into an error.
        </div>
        <SimulationContent v-if="simulation" :simulation="simulation" />
      </template>
      <div v-else-if="!selSimulation">Select a simulation</div>
    </template>
  </Card>

  <SimulationLogsDialog
    v-if="logsVisible && selSimulation"
    v-model:visible="logsVisible"
  />
  <SimulationConfigDialog
    v-if="configVisible && selSimulation"
    v-model:visible="configVisible"
  />
</template>

<script setup lang="ts">
import {
  GenerateReport,
  useGetSimulation,
  useListSimulations,
  useTriggerSimulation,
  useUpdateSimulationName,
} from '@/backend/simulate'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import axios, { type AxiosError } from 'axios'
import { inject, type Ref, ref, watch } from 'vue'
import ResultIcon from '@/pages/simulation/ResultIcon.vue'
import {
  type SimulationInfoFull,
  SimulationResultStatus,
} from '@/backend/interfaces'
import SimulationLogsDialog from '@/pages/simulation/SimulationLogsDialog.vue'
import SimulationConfigDialog from '@/pages/simulation/SimulationConfigDialog.vue'
import SimulationContent from '@/pages/simulation/SimulationContent.vue'
import { Popover, type SelectChangeEvent } from 'primevue'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const selSimulation = ref<SimulationInfoFull>()
const simName = ref('')

const advanced = inject<Ref<boolean>>('advanced')
const logsVisible = ref(false)
const configVisible = ref(false)

const { mutate: triggerSimulation, isPending: simulating } =
  useTriggerSimulation(route)
const { data: simulations } = useListSimulations(route)
const { data: simulation } = useGetSimulation(route)
const { mutate: updateSimulationName } = useUpdateSimulationName(route)

function changeSimulation(event: SelectChangeEvent) {
  router.push({
    name: 'SimulationResult',
    params: {
      simId: event.value.id,
    },
  })
}

// update select if simulation in route
watch(
  [simulation, simulations, route],
  () => {
    if (simulation.value) {
      selSimulation.value = {
        id: simulation.value.id,
        timestamp: simulation.value.timestamp,
        name: simulation.value.name || '',
        completed: true,
        status: simulation.value.status,
        xlsx: simulation.value.xlsx,
        h5: simulation.value.h5,
      }
      simName.value = simulation.value.name || ''
      return
    } else if (simulations.value && route.params.simId) {
      const foundSim = simulations.value.find(
        sim => sim.id === route.params.simId,
      )
      if (foundSim) {
        selSimulation.value = {
          ...foundSim,
          xlsx: false,
          h5: false,
        }
      } else {
        selSimulation.value = undefined
      }
      simName.value = selSimulation.value?.name || ''
    } else {
      selSimulation.value = undefined
    }
  },
  { immediate: true },
)

// set route if none exists
watch(
  [simulations, route],
  () => {
    if (!simulations.value || !!route.params.simId) return
    if (simulations.value.length === 0) return
    router.push({
      name: 'SimulationResult',
      params: {
        simId: simulations.value[0].id,
      },
    })
  },
  { immediate: true },
)

const simulatePop = ref<InstanceType<typeof Popover>>()
const generate_report = ref<GenerateReport | undefined>(undefined)
const generate_h5 = ref<boolean | undefined>(undefined)

function configSimulation(event: Event) {
  if (!advanced || !advanced.value) {
    trigger()
    return
  }
  if (!simulatePop.value) return

  simulatePop.value.toggle(event)
}

function trigger() {
  triggerSimulation(
    {
      generate_report: generate_report.value,
      generate_h5: generate_h5.value,
    },
    {
      onSuccess(data) {
        selSimulation.value = data
        router.push({
          name: 'SimulationResult',
          params: {
            simId: data.id,
          },
        })
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
    },
  )
}

function updateName(callback: () => void) {
  if (!selSimulation.value) return
  updateSimulationName(simName.value)
  callback()
}

function download(file: string) {
  const url = `${axios.defaults.baseURL || ''}/api/project/${route.params.proj}/simulate/result/${route.params.simId}/download/${file}/`
  window.open(url, '_blank')
}
</script>

<style scoped></style>
