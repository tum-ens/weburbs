<template>
  <divider />
  <div class="grid grid-cols-3">
    <div class="flex flex-col gap-3">
      <h1>{{ commodity.name }}</h1>
      <Button severity="secondary" @click="query">Query SupIm</Button>
    </div>

    <div v-if="supim?.data" class="col-span-2">
      <BarDiagramm :data title-x="Steps" title-y="kwH" />
    </div>
    <Skeleton v-else-if="pending" class="w-full" style="height: 10rem" />
  </div>
</template>

<script setup lang="ts">
import type { Commodity, Site } from '@/backend/interfaces'
import BarDiagramm from '@/plotly/BarDiagramm.vue'
import Plotly from 'plotly.js-dist'
import { computed, type Ref } from 'vue'
import { useGenerateSupIm, useGetSupIm } from '@/backend/supim'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'

const route = useRoute()
const toast = useToast()

const props = defineProps<{
  site: Site
  commodity: Commodity
}>()

const { data: supim, isPending: pending } = useGetSupIm(
  route,
  props.site,
  props.commodity,
)
const { mutate: generateSupim } = useGenerateSupIm(
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
    },
  ]
})

function query() {
  generateSupim(
    { type: 'Solar' },
    {
      onSuccess() {
        toast.add({
          summary: 'Success',
          detail: `SupIm for ${props.commodity.name} was generated`,
          severity: 'success',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
