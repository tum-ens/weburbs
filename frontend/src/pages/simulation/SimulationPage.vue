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
    </template>
  </Card>
</template>

<script setup lang="ts">
import { useTriggerSimulation } from '@/backend/simulate'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import type { AxiosError } from 'axios'
import { ref } from 'vue'
import { useSites } from '@/backend/sites'
import Plotly from 'plotly.js-dist'
import SiteResults from '@/pages/simulation/SiteResults.vue'
import { chunkAdd, chunkAvg, groupOptions } from '@/helper/diagrams'

const route = useRoute()
const toast = useToast()

const { data: sites } = useSites(route)
const { mutate: triggerSimulation, isPending: simulating } =
  useTriggerSimulation(route)

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
      procs.value = []
      overview.value = data.costs
      for (const site in data.process) {
        for (const proc in data.process[site]) {
          procs.value.push({
            site,
            proc,
            total: data.process[site][proc].Total,
            new: data.process[site][proc].New,
          })
        }
      }

      demand.value = {}
      created.value = {}
      storageLevel.value = {}
      for (const site in data.results) {
        demand.value[site] = {}
        created.value[site] = {}
        storageLevel.value[site] = {}
        for (const com in data.results[site]) {
          demand.value[site][com] = [
            {
              name: com,
              y: chunkAdd(
                data.results[site][com].demand,
                groupOptions[0].groupSize,
              ),
              x: Array.from(
                { length: groupOptions[0].groupSize },
                (_, i) => i + 1,
              ),
              type: 'bar',
            },
          ]
          created.value[site][com] = []
          for (const proc in data.results[site][com].created) {
            created.value[site][com].push({
              name: proc,
              y: chunkAdd(
                data.results[site][com].created[proc],
                groupOptions[0].groupSize,
              ),
              x: Array.from(
                { length: groupOptions[0].groupSize },
                (_, i) => i + 1,
              ),
              type: 'bar',
            })
          }
          if (data.results[site][com].storage) {
            storageLevel.value[site][com] = [
              {
                name: com,
                y: chunkAvg(
                  data.results[site][com].storage.Level,
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

      toast.add({
        summary: 'Success',
        detail: 'Simulation completed',
        severity: 'success',
        life: 2000,
      })
    },
    onError(error) {
      console.log(error)
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
