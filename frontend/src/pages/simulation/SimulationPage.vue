<template>
  <Card>
    <template #title>
      <div class="flex flex-row justify-between">
        <span>Simulations</span>
        <div class="flex flex-row gap-3">
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
                  :status="option.status || SimulationResultStatus.Optimal"
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
                  :status="value.status || SimulationResultStatus.Optimal"
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
      <template v-if="selSimulation">
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
    :result="selSimulation"
  />
  <SimulationConfigDialog
    v-if="configVisible && selSimulation"
    v-model:visible="configVisible"
    :result="selSimulation"
  />
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
import { inject, ref, watch } from 'vue'
import ResultIcon from '@/pages/simulation/ResultIcon.vue'
import {
  type SimulationResult,
  SimulationResultStatus,
} from '@/backend/interfaces'
import SimulationLogsDialog from '@/pages/simulation/SimulationLogsDialog.vue'
import SimulationConfigDialog from '@/pages/simulation/SimulationConfigDialog.vue'
import SimulationContent from '@/pages/simulation/SimulationContent.vue'

const route = useRoute()
const toast = useToast()

const selSimulation = ref<SimulationResult>()

const advanced = inject('advanced')
const logsVisible = ref(false)
const configVisible = ref(false)

const { mutate: triggerSimulation, isPending: simulating } =
  useTriggerSimulation(route)
const { data: simulations } = useListSimulations(route)
const { data: simulation } = useGetSimulation(route, selSimulation)

watch(simulation, () => {
  if (!simulation.value) return

  if (selSimulation.value) {
    selSimulation.value = {
      ...selSimulation.value,
      completed: true,
      status: simulation.value.status,
    }
  }
})

watch(
  simulations,
  () => {
    if (selSimulation.value || !simulations.value) return

    selSimulation.value = simulations.value[0]
  },
  { immediate: true },
)

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
</script>

<style scoped></style>
