<template>
  <Card>
    <template #title>
      <div class="flex flex-row justify-between">
        <span>Processes</span>
        <SplitButton
          v-if="advanced"
          :disabled="!curSite"
          label="Add Preset"
          @click="() => (defaultVisible = true)"
          :model="items"
        />
        <Button
          v-else
          :disabled="!curSite"
          label="Add Preset"
          @click="() => (defaultVisible = true)"
        />
      </div>
    </template>
    <template #content>
      <SiteOverviewComponent v-model:cur-site="curSite">
        <template #default="{ site }">
          <ProcessOverviewComponent
            :site="site"
            @clickProcess="
              proc => {
                clickedProcess = proc
                editVisible = true
              }
            "
            @duplicateProcess="
              proc => {
                duplicateProcess(proc)
              }
            "
          />
        </template>
      </SiteOverviewComponent>

      <div class="mt-3 flex justify-end">
        <Button
          @click="
            router.push({
              name: 'ProjectStorage',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Storage >>
        </Button>
      </div>
    </template>
  </Card>
  <DefaultProcessOverviewDialog
    v-if="curSite != null"
    v-model:visible="defaultVisible"
    :site_name="curSite"
  />
  <CreateProcessDialog
    v-if="advanced && curSite != null"
    v-model:visible="createVisible"
    :site_name="curSite"
  />
  <EditProcessDialog
    v-if="curSite != null && clickedProcess"
    :process="clickedProcess"
    v-model:visible="editVisible"
    :site_name="curSite"
    :from_energy_diagram="route.query.from === 'energy-diagram'"
  />
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import ProcessOverviewComponent from '@/components/ProcessOverviewComponent.vue'
import { inject, ref, watch } from 'vue'
import DefaultProcessOverviewDialog from '@/dialogs/DefaultProcessOverviewDialog.vue'
import { useSites } from '@/backend/sites'
import { useProcesses, useDuplicateProcess } from '@/backend/processes'
import CreateProcessDialog from '@/dialogs/CreateProcessDialog.vue'
import EditProcessDialog from '@/dialogs/EditProcessDialog.vue'
import type { Process } from '@/backend/interfaces'
import SiteOverviewComponent from '@/components/SiteOverviewComponent.vue'

const route = useRoute()
const router = useRouter()

const advanced = inject('advanced')

const curSite = ref()
const defaultVisible = ref(false)
const createVisible = ref(false)
const editVisible = ref(false)

const clickedProcess = ref<Process | null>(null)

const { data: sites } = useSites(route)

// Duplicate process functionality
const duplicateProcessMutation = useDuplicateProcess(route)

const duplicateProcess = async (process: Process) => {
  try {
    await duplicateProcessMutation.mutateAsync({
      site_name: curSite.value,
      process_name: process.name,
    })
  } catch (error) {
    console.error('Failed to duplicate process:', error)
  }
}
watch(
  sites,
  () => {
    if (!curSite.value && sites.value) {
      curSite.value = sites.value[0].name
    }
  },
  { immediate: true },
)

// Watch for query parameters to auto-open edit dialog or create dialog
watch(
  () => route.query,
  query => {
    // Handle auto-edit for existing processes
    if (query.autoEdit === 'true' && query.edit && query.site) {
      curSite.value = query.site as string

      // Get processes for the specified site
      const { data: processes } = useProcesses(route, {
        name: query.site as string,
      })

      watch(
        processes,
        procs => {
          if (procs) {
            const targetProcess = procs.find(p => p.name === query.edit)
            if (targetProcess) {
              clickedProcess.value = targetProcess
              editVisible.value = true
              console.log(
                'Auto-opening edit dialog for process:',
                targetProcess.name,
              )
            }
          }
        },
        { immediate: true },
      )
    }

    // Handle auto-create for new processes
    if (
      query.create === 'true' &&
      query.site &&
      query.from === 'energy-diagram'
    ) {
      console.log('Auto-create triggered for process at site:', query.site)
      curSite.value = query.site as string

      // Wait for sites to load and then open create dialog
      watch(
        sites,
        sitesData => {
          if (sitesData && sitesData.length > 0) {
            createVisible.value = true
            console.log('✅ Auto-opening create dialog for process')
          }
        },
        { immediate: true },
      )
    }
  },
  { immediate: true },
)

const items = [
  {
    label: 'Add Custom',
    command: () => {
      createVisible.value = true
    },
  },
]
</script>

<style scoped></style>
