<template>
  <Card>
    <template #title>
      <div class="flex flex-row justify-between">
        <span>Storage</span>
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
            <StorageOverviewComponent :site="site" />
          </AccordionContent>
        </AccordionPanel>
      </Accordion>

      <div class="mt-3 flex justify-end gap-3">
        <Button
          v-if="advanced"
          severity="info"
          @click="
            router.push({
              name: 'ProjectTransmission',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Transmission >>
        </Button>
        <Button
          @click="
            router.push({
              name: 'ProjectSimulation',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Simulation >>
        </Button>
      </div>
    </template>
  </Card>
  <DefaultStorageOverviewDialog
    v-if="curSite != null"
    v-model:visible="defaultVisible"
    :site_name="curSite"
  />
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { inject, ref, watch } from 'vue'
import { useSites } from '@/backend/sites'
import DefaultStorageOverviewDialog from '@/dialogs/DefaultStorageOverviewDialog.vue'
import StorageOverviewComponent from '@/components/StorageOverviewComponent.vue'

const toast = useToast()
const route = useRoute()
const router = useRouter()

const advanced = inject('advanced')

const curSite = ref()
const defaultVisible = ref(false)

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
      toast.add({
        severity: 'info',
        summary: 'TODO',
        detail: 'Not yet implemented',
        life: 3000,
      })
    },
  },
]
</script>

<style scoped></style>
