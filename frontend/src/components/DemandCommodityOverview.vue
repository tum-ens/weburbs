<template>
  <divider />
  <div class="grid grid-cols-8">
    <div class="flex flex-col gap-3">
      <h1>{{ commodity.name }}</h1>
      <Button @click="query" :disabled="!!demand?.data">Generate Demand</Button>
      <Button @click="del" severity="danger" :disabled="!demand?.data">
        Delete Demand
      </Button>
    </div>

    <div v-if="demand?.data" class="col-span-7">
      <BarDiagramm :data title-x="Steps" title-y="kwH" class="h-80" />
    </div>
    <Skeleton v-else-if="pending" class="w-full" style="height: 10rem" />
    <div v-else class="ml-5 italic">No SupIm configured</div>
  </div>
</template>

<script setup lang="ts">
import type { Commodity, Site } from '@/backend/interfaces'
import Plotly from 'plotly.js-dist'
import { computed, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import BarDiagramm from '@/plotly/BarDiagramm.vue'
import {
  useDeleteDemand,
  useGenerateDemand,
  useGetDemand,
} from '@/backend/demand'

const route = useRoute()
const toast = useToast()

const props = defineProps<{
  site: Site
  commodity: Commodity
}>()

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
      y: demand.value.data,
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
