<template>
  <Card>
    <template #title>
      <div class="flex flex-row justify-between">
        <span>Processes</span>
        <SplitButton
          :disabled="!curSite"
          label="Add Preset"
          @click="() => (defaultVisible = true)"
          :model="items"
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
            <ProcessOverviewComponent :site="site" />
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
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import ProcessOverviewComponent from '@/components/ProcessOverviewComponent.vue'
import { ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import DefaultProcessOverviewDialog from '@/dialogs/DefaultProcessOverviewDialog.vue'
import { useSites } from '@/backend/sites'

const toast = useToast()
const route = useRoute()
const router = useRouter()

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
