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
      <Accordion v-model:value="curSite">
        <AccordionPanel
          v-for="site in sites"
          :key="site.name"
          :value="site.name"
        >
          <AccordionHeader>{{ site.name }}</AccordionHeader>
          <AccordionContent>
            <ProcessOverviewComponent
              :site="site"
              @clickProcess="
                proc => {
                  clickedProcess = proc
                  editVisible = true
                }
              "
            />
          </AccordionContent>
        </AccordionPanel>
      </Accordion>

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
  />
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import ProcessOverviewComponent from '@/components/ProcessOverviewComponent.vue'
import { inject, ref, watch } from 'vue'
import DefaultProcessOverviewDialog from '@/dialogs/DefaultProcessOverviewDialog.vue'
import { useSites } from '@/backend/sites'
import CreateProcessDialog from '@/dialogs/CreateProcessDialog.vue'
import EditProcessDialog from '@/dialogs/EditProcessDialog.vue'
import type { Process } from '@/backend/interfaces'

const route = useRoute()
const router = useRouter()

const advanced = inject('advanced')

const curSite = ref()
const defaultVisible = ref(false)
const createVisible = ref(false)
const editVisible = ref(false)

const clickedProcess = ref<Process | null>(null)

const { data: sites } = useSites(route)
watch(
  sites,
  () => {
    if (!curSite.value && sites.value) {
      curSite.value = sites.value[0].name
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
