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
            v-if="simulationIsInfeasible"
            severity="warn"
            icon="pi pi-file"
            label="Show ILP file"
            v-tooltip.bottom="
              'Compute the conflicting constraints (IIS) and show the model.ilp file'
            "
            :loading="computingIIS"
            @click="computeAndShowIIS"
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
            v-if="canStopSimulation"
            severity="danger"
            icon="pi pi-stop-circle"
            label="Stop"
            :loading="stopping"
            @click="stopSimulation"
          />
          <Button
            v-if="advanced"
            class="col-span-2"
            icon="pi pi-caret-right"
            label="Configure simulation"
            :loading="simulating"
            :disabled="stopping"
            @click="configSimulation"
          />
          <Button
            v-else
            class="col-span-2"
            icon="pi pi-caret-right"
            label="Simulate"
            :loading="simulating"
            :disabled="stopping"
            @click="trigger"
          />
          <Popover ref="simulatePop">
            <div class="flex flex-col gap-3">
              <SelectButton
                :pt="{ root: 'w-full', pcToggleButton: { root: 'flex-1' } }"
                v-model="solver"
                :allow-empty="false"
                optionLabel="label"
                optionValue="value"
                :options="[
                  { label: 'Gurobi', value: Solver.GUROBI },
                  { label: 'GLPK', value: Solver.GLPK },
                ]"
              />
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
              <FloatLabel
                v-if="generate_report === GenerateReport.FULL"
                variant="on"
                class="w-full"
              >
                <MultiSelect
                  inputId="timeseries-commodity-types"
                  fluid
                  display="chip"
                  :options="timeseriesTypeOptions"
                  optionLabel="label"
                  optionValue="value"
                  v-model="timeseriesCommodityTypes"
                />
                <label for="timeseries-commodity-types">
                  Timeseries commodity types
                </label>
              </FloatLabel>
              <div class="flex flex-col gap-2">
                <div class="flex items-center gap-2">
                  <Checkbox
                    v-model="custom_timestep_range"
                    inputId="custom-timesteps"
                    binary
                  />
                  <label for="custom-timesteps" class="cursor-pointer">
                    Limited timestep range (test run)
                  </label>
                </div>
                <div
                  v-if="custom_timestep_range"
                  class="flex flex-col gap-2"
                >
                  <div class="flex items-center gap-2">
                    <InputNumber
                      v-model="timestep_from"
                      :min="0"
                      :max="maxTimestep"
                      placeholder="From"
                      class="flex-1"
                    />
                    <span class="text-surface-500">to</span>
                    <InputNumber
                      v-model="timestep_to"
                      :min="timestep_from ?? 0"
                      :max="maxTimestep"
                      placeholder="To"
                      class="flex-1"
                    />
                  </div>
                  <small
                    v-if="simulationInfo"
                    class="text-surface-500"
                  >
                    Timesteps are 0-based (0 … {{ maxTimestep }})
                  </small>
                </div>
              </div>
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
          v-if="!simulation && !simulationFailed && !simulationStopped"
          class="flex flex-col gap-3 items-center justify-start"
        >
          <SimulationProgress :progress="simulationProgress" />
        </div>
        <div
          v-else-if="simulationStopped || simulationFailed"
          class="flex flex-col gap-4 items-center justify-start"
        >
          <SimulationProgress :progress="simulationProgress" />
          <div
            v-if="simulationFailed && !simulationStopped"
            class="text-surface-600 dark:text-surface-300"
          >
            The simulation ran into an error.
          </div>
        </div>
        <SimulationContent
          v-if="simulation && !simulationFailed && !simulationStopped"
          :simulation="simulation"
        />
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
  <SimulationIISDialog
    v-if="iisVisible"
    v-model:visible="iisVisible"
    :content="iisContent"
    @download="download('ilp')"
  />
</template>

<script setup lang="ts">
import {
  GenerateReport,
  Solver,
  useComputeIIS,
  useGetSimulation,
  useGetSimulationInfo,
  useGetSimulationProgress,
  useListSimulations,
  useStopSimulation,
  useTriggerSimulation,
  useUpdateSimulationName,
} from '@/backend/simulate'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import axios, { type AxiosError } from 'axios'
import { computed, inject, type Ref, ref, watch } from 'vue'
import ResultIcon from '@/pages/simulation/ResultIcon.vue'
import {
  type SimulationInfoFull,
  SimulationResultStatus,
} from '@/backend/interfaces'
import SimulationLogsDialog from '@/pages/simulation/SimulationLogsDialog.vue'
import SimulationConfigDialog from '@/pages/simulation/SimulationConfigDialog.vue'
import SimulationIISDialog from '@/pages/simulation/SimulationIISDialog.vue'
import SimulationContent from '@/pages/simulation/SimulationContent.vue'
import SimulationProgress from '@/pages/simulation/SimulationProgress.vue'
import { Popover, type SelectChangeEvent } from 'primevue'
import { getNameValidationError } from '@/helper/nameValidation'

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
const { mutate: stopSimulationMutate, isPending: stopping } =
  useStopSimulation(route)
const { data: simulations } = useListSimulations(route)
const { data: simulation } = useGetSimulation(route)
const { data: simulationInfo } = useGetSimulationInfo(route)

const maxTimestep = computed(() =>
  simulationInfo.value ? simulationInfo.value.c_timesteps - 1 : undefined,
)

const pollSimulationProgress = computed(() => {
  if (!route.params.simId) return false
  if (simulationProgress.value?.cancelled) return false
  if (
    selSimulation.value?.completed &&
    selSimulation.value?.status === SimulationResultStatus.Cancelled
  ) {
    return false
  }
  if (simulation.value?.status === SimulationResultStatus.Cancelled) return false
  if (!simulation.value) return true
  return simulation.value.status !== SimulationResultStatus.Optimal
})

const simulationStopped = computed(
  () =>
    simulationProgress.value?.cancelled === true ||
    selSimulation.value?.status === SimulationResultStatus.Cancelled ||
    simulation.value?.status === SimulationResultStatus.Cancelled,
)

const { data: simulationProgress } = useGetSimulationProgress(
  route,
  pollSimulationProgress,
)

const simulationFailed = computed(() => {
  if (!simulation.value) return false
  return simulation.value.status !== SimulationResultStatus.Optimal
})

const { mutate: updateSimulationName } = useUpdateSimulationName(route)

const { mutate: computeIIS, isPending: computingIIS } = useComputeIIS(route)
const iisVisible = ref(false)
const iisContent = ref('')

const simulationIsInfeasible = computed(
  () =>
    simulation.value?.status === SimulationResultStatus.Infeasible ||
    selSimulation.value?.status === SimulationResultStatus.Infeasible,
)

const canStopSimulation = computed(() => {
  if (!selSimulation.value) return false
  return !selSimulation.value.completed
})

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
const solver = ref<Solver>(Solver.GUROBI)
const custom_timestep_range = ref(false)
const timestep_from = ref<number | null>(0)
const timestep_to = ref<number | null>(null)
const timeseriesTypeOptions = [
  { label: 'Demand', value: 'Demand' },
  { label: 'Buy', value: 'Buy' },
  { label: 'Sell', value: 'Sell' },
  { label: 'Env', value: 'Env' },
]
const timeseriesCommodityTypes = ref<string[]>(['Demand'])

function configSimulation(event: Event) {
  if (!advanced || !advanced.value) {
    trigger()
    return
  }
  if (!simulatePop.value) return

  simulatePop.value.toggle(event)
}

function trigger() {
  const timestepParams =
    custom_timestep_range.value && maxTimestep.value !== undefined
      ? {
          timestep_from: timestep_from.value ?? 0,
          timestep_to: timestep_to.value ?? maxTimestep.value,
        }
      : {}

  triggerSimulation(
    {
      generate_report: generate_report.value,
      generate_h5: generate_h5.value,
      solver: solver.value,
      ...(generate_report.value === GenerateReport.FULL
        ? {
            timeseries_commodity_types: [...timeseriesCommodityTypes.value],
          }
        : {}),
      ...timestepParams,
    },
    {
      onSuccess(data) {
        selSimulation.value = {
          ...data,
          xlsx: false,
          h5: false,
        }
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

function stopSimulation() {
  const simId = selSimulation.value?.id || <string>route.params.simId
  if (!simId) return

  stopSimulationMutate(simId, {
    onSuccess() {
      if (selSimulation.value) {
        selSimulation.value = {
          ...selSimulation.value,
          completed: true,
          status: SimulationResultStatus.Cancelled,
        }
      }
      toast.add({
        summary: 'Stopped',
        detail: 'Simulation stop requested',
        severity: 'warn',
        life: 2500,
      })
    },
    onError(error) {
      toast.add({
        summary: 'Stop failed',
        detail:
          (<{ detail?: string }>(<AxiosError>error)?.response?.data)?.detail ||
          'Could not stop simulation',
        severity: 'error',
        life: 3000,
      })
    },
  })
}

function updateName(callback: () => void) {
  if (!selSimulation.value) return
  const nameError = getNameValidationError(simName.value)
  if (nameError) {
    toast.add({
      summary: 'Error',
      detail: nameError,
      severity: 'error',
      life: 2000,
    })
    return
  }
  updateSimulationName(simName.value)
  callback()
}

function download(file: string) {
  const url = `${axios.defaults.baseURL || ''}/api/project/${route.params.proj}/simulate/result/${route.params.simId}/download/${file}/`
  window.open(url, '_blank')
}

function computeAndShowIIS() {
  const simId = selSimulation.value?.id || <string>route.params.simId
  if (!simId) return

  computeIIS(simId, {
    onSuccess(data: { content?: string }) {
      iisContent.value = data?.content || ''
      iisVisible.value = true
    },
    onError(error) {
      toast.add({
        summary: 'IIS computation failed',
        detail:
          (<{ detail?: string }>(<AxiosError>error)?.response?.data)?.detail ||
          'Could not compute the IIS',
        severity: 'error',
        life: 4000,
      })
    },
  })
}
</script>

<style scoped></style>
