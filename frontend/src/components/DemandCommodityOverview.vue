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

    <div v-if="demands && demands?.length > 0" class="col-span-7">
      <BarDiagramm
        :data="data"
        title-x="Steps"
        :title-y="commodity.unitC"
        class="h-80"
        :bargroupgap="0.1"
        :margin="{ t: 20 }"
      />
    </div>
    <Skeleton v-else-if="pending" class="col-span-7" style="height: 10rem" />
    <div v-else class="ml-5 italic col-span-7">No Demand configured</div>
  </div>

  <ConfigureDemandDialog
    v-model:visible="configureVisible"
    :site="site"
    :commodity="commodity"
  />
</template>

<script setup lang="ts">
import type { Commodity, Site } from '@/backend/interfaces'
import { computed, type Ref, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useGetDemand } from '@/backend/demand'
import { chunkAdd, groupOptions } from '@/helper/diagrams'
import ConfigureDemandDialog from '@/dialogs/ConfigureDemandDialog.vue'
import BarDiagramm from '@/plotly/PlotlyDiagram.vue'

const route = useRoute()

const configureVisible = ref(false)
const props = defineProps<{
  site: Site
  commodity: Commodity
}>()

const groupOption = ref(groupOptions[0])

const { data: demands, isPending: pending } = useGetDemand(
  route,
  props.site,
  props.commodity,
)

const data: Ref<Partial<Plotly.Data>[]> = computed(() => {
  if (!demands.value) return []
  return demands.value.map(demand => {
    return {
      name: demand.name,
      y: chunkAdd(demand.steps, groupOption.value.groupSize, demand.quantity),
      x: Array.from({ length: groupOption.value.groups }, (_, i) => i + 1),
      type: 'bar',
      marker: {
        color: props.commodity.name.includes('Solar') ? 'gold' : undefined,
      },
    }
  })
})
</script>

<style scoped></style>
