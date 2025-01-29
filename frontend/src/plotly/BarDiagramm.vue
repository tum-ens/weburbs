<template>
  <div ref="plot" :id="plotId" class="overflow-hidden" />
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import Plotly from 'plotly.js-dist'
import { v4 as uuid } from 'uuid'

const plotId = uuid()
const plot = ref<HTMLDivElement>()

const props = defineProps<{
  data: Partial<Plotly.Data>[]
  title?: string
  titleX: string
  titleY: string
  bargap?: number
  bargroupgap?: number
}>()

function layout(): Partial<Plotly.Layout> {
  return {
    bargap: props.bargap || 0,
    bargroupgap: props.bargroupgap || 0,
    barmode: 'stack',
    title: props.title
      ? {
          text: props.title,
        }
      : undefined,
    margin: {
      t: props.title ? 50 : 10, // Adjust top margin dynamically
    },
    xaxis: {
      title: {
        text: props.titleX,
      },
    },
    yaxis: {
      title: {
        text: props.titleY,
      },
    },
  }
}

let replotTimeout: number | null = null
function replot() {
  if (replotTimeout) clearTimeout(replotTimeout)
  replotTimeout = setTimeout(
    () => Plotly.newPlot(plotId, props.data, layout()),
    200,
  )
}

const resizeObserver = new ResizeObserver(replot)
onMounted(() => {
  replot()
  if (plot.value) resizeObserver.observe(plot.value)
})
watch(props, replot, { immediate: true })
</script>

<style scoped></style>
