<template>
  <Card class="w-80">
    <template #content>
      <ScrollPanel>
        <PanelMenu :model="items" v-model:expanded-keys="expandedKey">
          <template #item="{ item }">
            <a class="flex items-center px-4 py-2 cursor-pointer group">
              <span
                v-if="item.items"
                class="pi text-primary mr-2"
                :class="{
                  'pi-angle-right': !expandedKey[<string>item.key],
                  'pi-angle-down': expandedKey[<string>item.key],
                }"
              />
              <span
                :class="[item.icon, 'text-primary group-hover:text-inherit']"
              />
              <span
                :class="[
                  'ml-2',
                  { 'font-semibold': expandedKey[<string>item.key] },
                ]"
                >{{ item.label }}</span
              >
            </a>
          </template>
        </PanelMenu>
      </ScrollPanel>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectList } from '@/backend/projects'

const route = useRoute()
const router = useRouter()

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
    if (route.params.proj)
      expandedKey.value['proj:' + <string>route.params.proj] = true
  },
  { immediate: true },
)

const items = computed(() => {
  return [
    {
      key: 'Home',
      label: 'Home',
      icon: 'pi pi-home',
      command: () => router.push({ name: 'Home' }),
    },
    {
      key: 'ProjectList',
      label: 'Projects',
      icon: 'pi pi-folder',
      command: () => router.push({ name: 'ProjectList' }),
      items: [
        {
          key: 'CreateProject',
          label: 'Create',
          icon: 'pi pi-pencil',
          command: () =>
            router.push({
              name: 'CreateProject',
            }),
        },
        ...(projects.value || []).map(p => {
          return {
            key: 'proj:' + p.name,
            label: p.name,
            icon: 'pi pi-receipt',
            command: () =>
              router.push({
                name: 'Project',
                params: {
                  proj: p.name,
                },
              }),
            items: [
              {
                key: 'ProjectConfig',
                label: 'Global',
                icon: 'pi pi-globe',
                command: () =>
                  router.push({
                    name: 'ProjectConfig',
                    params: {
                      proj: p.name,
                    },
                  }),
              },
              {
                key: 'ProjectSites',
                label: 'Sites',
                icon: 'pi pi-map-marker',
                command: () =>
                  router.push({
                    name: 'ProjectSites',
                    params: {
                      proj: p.name,
                    },
                  }),
              },
              {
                key: 'ProjectCommodity',
                label: 'Commodities',
                icon: 'pi pi-bolt',
                command: () =>
                  router.push({
                    name: 'ProjectCommodity',
                    params: {
                      proj: p.name,
                    },
                  }),
              },
              {
                key: 'ProjectProcess',
                label: 'Processes',
                icon: 'pi pi-hammer',
                command: () =>
                  router.push({
                    name: 'ProjectProcess',
                    params: {
                      proj: p.name,
                    },
                  }),
              },
              {
                key: 'ProjectStorage',
                label: 'Storage',
                icon: 'pi pi-warehouse',
                command: () =>
                  router.push({
                    name: 'ProjectStorage',
                    params: {
                      proj: p.name,
                    },
                  }),
              },
              {
                key: 'ProjectDemand',
                label: 'Demand',
                icon: 'pi pi-gauge',
                command: () =>
                  router.push({
                    name: 'ProjectDemand',
                    params: {
                      proj: p.name,
                    },
                  }),
              },
              {
                key: 'ProjectSuplm',
                label: 'Suplm',
                icon: 'pi pi-sun',
                command: () =>
                  router.push({
                    name: 'ProjectSuplm',
                    params: {
                      proj: p.name,
                    },
                  }),
              },
              {
                key: 'ProjectTransmission',
                label: 'Transmission',
                icon: 'pi pi-wifi',
                command: () =>
                  router.push({
                    name: 'ProjectTransmission',
                    params: {
                      proj: p.name,
                    },
                  }),
              },
              {
                key: 'ProjectDSM',
                label: 'DSM',
                icon: 'pi pi-sliders-v',
                command: () =>
                  router.push({
                    name: 'ProjectDSM',
                    params: {
                      proj: p.name,
                    },
                  }),
              },
              {
                key: 'ProjectBuySell',
                label: 'BuySellPrice',
                icon: 'pi pi-dollar',
                command: () =>
                  router.push({
                    name: 'ProjectBuySell',
                    params: {
                      proj: p.name,
                    },
                  }),
              },
              {
                key: 'ProjectTimeVarEff',
                label: 'TimeVarEff',
                icon: 'pi pi-hourglass',
                command: () =>
                  router.push({
                    name: 'ProjectTimeVarEff',
                    params: {
                      proj: p.name,
                    },
                  }),
              },
              {
                key: 'ProjectSimulation',
                label: 'Simulation',
                icon: 'pi pi-play-circle',
                command: () =>
                  router.push({
                    name: 'ProjectSimulation',
                    params: {
                      proj: p.name,
                    },
                  }),
              },
            ],
          }
        }),
      ],
    },
  ]
})
</script>

<style scoped></style>
