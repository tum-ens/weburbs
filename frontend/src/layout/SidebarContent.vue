<template>
  <Accordion>
    <AccordionPanel value="0">
      <AccordionHeader>Versions</AccordionHeader>
      <AccordionContent>
        <div class="flex flex-col gap-3">
          <Select
            fluid
            class="col-span-2 mb-3"
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
            label="Rename"
          />
          <Button
            label="Duplicate"
            />
        </div>
      </AccordionContent>
    </AccordionPanel>
  </Accordion>
  <PanelMenu :model="items" :expanded-keys="expandedKey">
    <template #item="{ item }">
      <a class="flex items-center px-4 py-2 cursor-pointer group">
        <span
          :class="[
            item.icon,
            item.advanced ? 'text-orange-400' : 'text-primary',
          ]"
        />
        <span
          :class="['ml-2', { 'font-semibold': expandedKey[<string>item.key] }]"
          class="select-none"
        >
          {{ item.label }}
        </span>
      </a>
    </template>
  </PanelMenu>
  <div class="flex flex-row pt-3 pl-3 gap-3">
    <label for="advanced" class="select-none">Advanced mode</label>
    <ToggleSwitch inputId="advanced" v-model="advanced" />
  </div>
</template>

<script setup lang="ts">
import { computed, inject, type Ref, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectList } from '@/backend/projects'
import { type SimulationInfo, SimulationResultStatus } from '@/backend/interfaces'
import ResultIcon from '@/pages/simulation/ResultIcon.vue'
import { useGetSimulation, useListSimulations } from '@/backend/simulate'
import type { SelectChangeEvent } from 'primevue'

const route = useRoute()
const router = useRouter()

const advanced = inject<Ref<boolean>>('advanced')

const selSimulation = ref<SimulationInfo>()
const { data: simulation } = useGetSimulation(route)
const { data: simulations } = useListSimulations(route)

function changeSimulation(event: SelectChangeEvent) {
  router.push({
    name: 'SimulationResult',
    params: {
      simId: event.value.id
    }
  })
}

const expandedKey = ref<{ [key: string]: boolean }>({})
const { data: projects } = useProjectList()
watch(
  [route, projects],
  () => {
    expandedKey.value = {}
    if (route.name) expandedKey.value[<string>route.name] = true
    if (route.meta.parents)
      for (const parent of <string[]>route.meta.parents) {
        expandedKey.value[parent] = true
      }
    if (route.params.proj) expandedKey.value['project'] = true
  },
  { immediate: true }
)
// update select if simulation in route
watch(
  [simulation, simulations],
  () => {
    if (simulation.value) {
      selSimulation.value = {
        id: simulation.value.id,
        timestamp: simulation.value.timestamp,
        completed: true,
        status: simulation.value.status,
      }
      return
    }
    if (simulations.value && route.params.simId)
      selSimulation.value = simulations.value.find(
        sim => sim.id === route.params.simId,
      )
    else selSimulation.value = undefined
  },
  { immediate: true },
)

const items = computed(() => {
  return [
    {
      key: 'Home',
      label: 'Home',
      icon: 'pi pi-home',
      command: () => router.push({ name: 'Home' })
    },
    {
      key: 'project',
      label: <string>route.params.proj || 'Project',
      disabled: !route.params.proj,
      icon: 'pi pi-receipt',
      items: [
        {
          key: 'ProjectConfig',
          label: 'Global',
          icon: 'pi pi-globe',
          command: () =>
            router.push({
              name: 'ProjectConfig'
            })
        },
        {
          key: 'ProjectSites',
          label: 'Sites',
          icon: 'pi pi-map-marker',
          command: () =>
            router.push({
              name: 'ProjectSites'
            })
        },
        {
          key: 'ProjectCommodity',
          label: 'Commodities',
          advanced: true,
          icon: 'pi pi-bolt',
          command: () =>
            router.push({
              name: 'ProjectCommodity'
            })
        },
        {
          key: 'ProjectDemand',
          label: 'Demand',
          icon: 'pi pi-gauge',
          command: () =>
            router.push({
              name: 'ProjectDemand'
            })
        },
        {
          key: 'ProjectSupIm',
          label: 'SupIm',
          icon: 'pi pi-sun',
          advanced: true,
          command: () =>
            router.push({
              name: 'ProjectSupIm'
            })
        },
        {
          key: 'ProjectProcess',
          label: 'Processes',
          icon: 'pi pi-hammer',
          command: () =>
            router.push({
              name: 'ProjectProcess'
            })
        },
        {
          key: 'ProjectStorage',
          label: 'Storage',
          icon: 'pi pi-warehouse',
          command: () =>
            router.push({
              name: 'ProjectStorage'
            })
        },
        {
          key: 'ProjectSimulation',
          label: 'Simulation',
          icon: 'pi pi-play-circle',
          command: () =>
            router.push({
              name: 'ProjectSimulation'
            })
        }
        /*{
          key: 'advanced',
          label: 'Advanced',
          advanced: true,
          icon: 'pi pi-sparkles',
          command: () => {
            const newKeys = { ...expandedKey.value }
            if (newKeys['advanced']) {
              delete newKeys['advanced']
            } else {
              newKeys['advanced'] = true
            }
            expandedKey.value = newKeys
          },
          items: [
            {
              key: 'ProjectTransmission',
              label: 'Transmission',
              icon: 'pi pi-wifi',
              command: () =>
                router.push({
                  name: 'ProjectTransmission',
                }),
            },
            {
              key: 'ProjectDSM',
              label: 'DSM',
              icon: 'pi pi-sliders-v',
              command: () =>
                router.push({
                  name: 'ProjectDSM',
                }),
            },
            {
              key: 'ProjectBuySell',
              label: 'BuySellPrice',
              icon: 'pi pi-dollar',
              command: () =>
                router.push({
                  name: 'ProjectBuySell',
                }),
            },
            {
              key: 'ProjectTimeVarEff',
              label: 'TimeVarEff',
              icon: 'pi pi-hourglass',
              command: () =>
                router.push({
                  name: 'ProjectTimeVarEff',
                }),
            },
          ],
        },*/
      ].filter(
        item => (!item.advanced || advanced?.value) && route.params.proj
      )
    }
  ]
})
</script>

<style scoped></style>
