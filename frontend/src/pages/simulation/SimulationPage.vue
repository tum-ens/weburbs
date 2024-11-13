<template>
  <Card>
    <template #title>Simulations</template>
    <template #content>
      <Button
        icon="pi pi-caret-right"
        label="Simulate"
        :loading="simulating"
        @click="trigger"
      />

      <template v-if="overview">
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
      </template>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { useTriggerSimulation } from '@/backend/simulate'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import type { AxiosError } from 'axios'
import { ref } from 'vue'

const route = useRoute()
const toast = useToast()

const { mutate: triggerSimulation, isPending: simulating } =
  useTriggerSimulation(route)

const overview = ref()
const procs = ref<{ site: string; proc: string; total: number; new: number }[]>(
  [],
)

function trigger() {
  triggerSimulation(undefined, {
    onSuccess(data) {
      overview.value = data.data.costs
      for (const site in data.data.process) {
        for (const proc in data.data.process[site]) {
          procs.value.push({
            site,
            proc,
            total: data.data.process[site][proc].Total,
            new: data.data.process[site][proc].New,
          })
        }
      }

      toast.add({
        summary: 'Success',
        detail: 'Simulation completed',
        severity: 'success',
        life: 2000,
      })
    },
    onError(error) {
      toast.add({
        summary: 'Simulation error',
        detail: (<AxiosError>error)?.response?.data,
        severity: 'error',
        life: 2000,
      })
    },
  })
}
</script>

<style scoped></style>
