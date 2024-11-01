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
watch(
  route,
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
const { data: projects } = useProjectList()

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
                key: 'ProjectGlobal',
                label: 'Global',
                icon: 'pi pi-globe',
                command: () =>
                  router.push({
                    name: 'ProjectGlobal',
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
                key: 'ProjectCommoditySites',
                label: 'Commodities',
                icon: 'pi pi-bolt',
                command: () =>
                  router.push({
                    name: 'ProjectCommoditySites',
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
