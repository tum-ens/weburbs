<template>
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
  <Button
    v-if="!!route.params.proj"
    class="mt-3"
    fluid
    severity="danger"
    label="Delete Project"
    @click="deleteProject()"
  />
  <div class="flex flex-row pt-3 pl-3 gap-3">
    <label for="advanced" class="select-none">Advanced mode</label>
    <ToggleSwitch inputId="advanced" v-model="advanced" />
  </div>

  <ConfirmDialog />
</template>

<script setup lang="ts">
import { computed, inject, type Ref, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDeleteProject, useProjectList } from '@/backend/projects'
import { useConfirm } from 'primevue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const route = useRoute()
const router = useRouter()

const advanced = inject<Ref<boolean>>('advanced')

const confirm = useConfirm()
const { mutate: deleteProjectCall } = useDeleteProject(route)

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
              name: 'ProjectConfig',
            }),
        },
        {
          key: 'ProjectSites',
          label: 'Sites',
          icon: 'pi pi-map-marker',
          command: () =>
            router.push({
              name: 'ProjectSites',
            }),
        },
        {
          key: 'ProjectCommodity',
          label: 'Commodities',
          advanced: true,
          icon: 'pi pi-bolt',
          command: () =>
            router.push({
              name: 'ProjectCommodity',
            }),
        },
        {
          key: 'ProjectDemand',
          label: 'Demand',
          icon: 'pi pi-gauge',
          command: () =>
            router.push({
              name: 'ProjectDemand',
            }),
        },
        {
          key: 'ProjectSupIm',
          label: 'SupIm',
          icon: 'pi pi-sun',
          advanced: true,
          command: () =>
            router.push({
              name: 'ProjectSupIm',
            }),
        },
        {
          key: 'ProjectProcess',
          label: 'Processes',
          icon: 'pi pi-hammer',
          command: () =>
            router.push({
              name: 'ProjectProcess',
            }),
        },
        {
          key: 'ProjectStorage',
          label: 'Storage',
          icon: 'pi pi-warehouse',
          command: () =>
            router.push({
              name: 'ProjectStorage',
            }),
        },
        {
          key: 'ProjectTransmission',
          label: 'Transmission',
          icon: 'pi pi-wifi',
          advanced: true,
          command: () =>
            router.push({
              name: 'ProjectTransmission',
            }),
        },
        {
          key: 'ProjectDSM',
          label: 'DSM',
          icon: 'pi pi-sliders-v',
          advanced: true,
          command: () =>
            router.push({
              name: 'ProjectDSM',
            }),
        },
        {
          key: 'ProjectBuySell',
          label: 'BuySellPrice',
          icon: 'pi pi-dollar',
          advanced: true,
          command: () =>
            router.push({
              name: 'ProjectBuySell',
            }),
        },
        {
          key: 'ProjectTimeVarEff',
          label: 'TimeVarEff',
          icon: 'pi pi-hourglass',
          advanced: true,
          command: () =>
            router.push({
              name: 'ProjectTimeVarEff',
            }),
        },
        {
          key: 'ProjectSimulation',
          label: 'Simulation',
          icon: 'pi pi-play-circle',
          command: () =>
            router.push({
              name: 'ProjectSimulation',
            }),
        },
      ].filter(
        item => (!item.advanced || advanced?.value) && route.params.proj,
      ),
    },
  ]
})

function deleteProject() {
  confirm.require({
    message: 'Are you sure you want to delete this project?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: {
      label: 'Cancel',
    },
    acceptProps: {
      label: 'Delete',
      outlined: true,
      severity: 'danger',
    },
    accept: () => {
      deleteProjectCall()
      toast.add({
        severity: 'error',
        summary: 'Deleted',
        detail: 'The project has been deleted',
        life: 2000,
      })
      router.push({
        name: 'Home',
      })
    },
  })
}
</script>

<style scoped></style>
