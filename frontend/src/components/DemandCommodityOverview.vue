<template>
  <divider />
  <div class="grid grid-cols-8 gap-3">
    <div class="flex flex-col gap-3">
      <h1>{{ commodity.name }}</h1>
      <Button
        @click="() => (configureVisible = true)"
        severity="info"
        label="Configure"
      />
      <FloatLabel variant="on">
        <Select
          fluid
          id="groupoptions"
          :options="groupOptions"
          optionLabel="name"
          v-model="groupOption"
        />
        <label for="groupoptions">Group values</label>
      </FloatLabel>
    </div>

    <div v-if="demand?.data" class="col-span-7">
      <BarDiagramm
        :data
        title-x="Steps"
        title-y="kwH"
        class="h-80"
        :bargroupgap="0.1"
      />
    </div>
    <Skeleton v-else-if="pending" class="col-span-7" style="height: 10rem" />
    <div v-else class="ml-5 italic col-span-7">No Demand configured</div>
  </div>

  <ConfigureDemandDialog v-model:visible="configureVisible" />
</template>

<script setup lang="ts">
import type { Commodity, Site } from '@/backend/interfaces'
import Plotly from 'plotly.js-dist'
import { computed, ref, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import BarDiagramm from '@/plotly/BarDiagramm.vue'
import {
  useDeleteDemand,
  useGenerateDemand,
  useGetDemand,
} from '@/backend/demand'
import { groupOptions, chunkAdd } from '@/helper/diagrams'
import ConfigureDemandDialog from '@/dialogs/ConfigureDemandDialog.vue'

const route = useRoute()
const toast = useToast()

const configureVisible = ref(false)
const props = defineProps<{
  site: Site
  commodity: Commodity
}>()

const groupOption = ref(groupOptions[0])

const { data: demand, isPending: pending } = useGetDemand(
  route,
  props.site,
  props.commodity,
)
const { mutate: deleteDemand } = useDeleteDemand(
  route,
  props.site,
  props.commodity,
)

const data: Ref<Partial<Plotly.Data>[]> = computed(() => {
  if (!demand.value?.data) return []
  return [
    {
      name: props.commodity.name,
      y: chunkAdd(demand.value.data, groupOption.value.groupSize),
      x: Array.from({ length: groupOption.value.groups }, (_, i) => i + 1),
      type: 'bar',
      marker: {
        color: props.commodity.name.includes('Solar') ? 'gold' : undefined,
      },
    },
  ]
})

function del() {
  deleteDemand(undefined, {
    onSuccess() {
      toast.add({
        summary: 'Success',
        detail: `Demand for ${props.commodity.name} was deleted`,
        severity: 'success',
        life: 2000,
      })
    },
  })
}

const { mutate: generateDemand } = useGenerateDemand(
  route,
  props.site,
  props.commodity,
)

function query() {
  generateDemand(undefined, {
    onSuccess() {
      toast.add({
        summary: 'Success',
        detail: `Demand for ${props.commodity.name} was generated`,
        severity: 'success',
        life: 2000,
      })
    },
  })
}
</script>

<style scoped></style>
