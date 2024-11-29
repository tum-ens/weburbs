<template>
  <divider />
  <div class="grid grid-cols-8 gap-3">
    <div class="flex flex-col gap-3">
      <h1>{{ commodity.name }}</h1>
      <Button @click="query" :disabled="!!supim?.data">Query SupIm</Button>
      <Button @click="del" severity="danger" :disabled="!supim?.data">
        Delete SupIm
      </Button>
    </div>

    <div v-if="supim?.data" class="col-span-7">
      <BarDiagramm :data title-x="Steps" title-y="kWh" class="h-80" />
    </div>
    <Skeleton v-else-if="pending" class="col-span-7" style="height: 10rem" />
    <div v-else class="ml-5 italic">No SupIm configured</div>
  </div>
  <QuerySupImDialog :site :commodity v-model="queryVisible" />
</template>

<script setup lang="ts">
import type { Commodity, Site } from '@/backend/interfaces'
import Plotly from 'plotly.js-dist'
import { computed, ref, type Ref } from 'vue'
import { useDeleteSupIm, useGetSupIm } from '@/backend/supim'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import BarDiagramm from '@/plotly/BarDiagramm.vue'
import QuerySupImDialog from '@/dialogs/QuerySupImDialog.vue'

const route = useRoute()
const toast = useToast()

const queryVisible = ref(false)

const props = defineProps<{
  site: Site
  commodity: Commodity
}>()

const { data: supim, isPending: pending } = useGetSupIm(
  route,
  props.site,
  props.commodity,
)
const { mutate: deleteSupIm } = useDeleteSupIm(
  route,
  props.site,
  props.commodity,
)

const data: Ref<Partial<Plotly.Data>[]> = computed(() => {
  if (!supim.value?.data) return []
  return [
    {
      name: props.commodity.name,
      y: supim.value.data,
      type: 'bar',
      marker: {
        color: props.commodity.name.includes('Solar') ? 'gold' : undefined,
      },
    },
  ]
})

function del() {
  deleteSupIm(undefined, {
    onSuccess() {
      toast.add({
        summary: 'Success',
        detail: `SupIm for ${props.commodity.name} was deleted`,
        severity: 'success',
        life: 2000,
      })
    },
  })
}

function query() {
  queryVisible.value = true
}
</script>

<style scoped></style>
