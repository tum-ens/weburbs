<template>
  <div v-if="true" ref="plot" :id="plotId" class="overflow-hidden"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import Plotly from 'plotly.js-dist'
import { v4 as uuid } from 'uuid'

const plotId = uuid()
const plot = ref<HTMLDivElement>()

const props = defineProps<{
  data: Partial<Plotly.Data>[]
  title?: string
  titleX?: string
  titleX2?: string
  titleY?: string
  titleY2?: string
  bargap?: number
  bargroupgap?: number
  margin?: { t?: number; b?: number; l?: number; r?: number }
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
    xaxis: {
      title: {
        text: props.titleX,
      },
      side: 'bottom',
      rangemode: 'nonnegative',
    },
    xaxis2: {
      title: {
        text: props.titleX2,
      },
      side: 'top',
      overlaying: 'x',
      rangemode: 'nonnegative',
    },
    margin: props.margin,
    yaxis: {
      title: {
        text: props.titleY,
      },
      side: 'left',
      rangemode: 'nonnegative',
    },
    yaxis2: {
      title: {
        text: props.titleY2,
      },
      side: 'right',
      rangemode: 'nonnegative',
      overlaying: 'y',
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
  watch(props, replot)
})

onUnmounted(() => {
  if (replotTimeout) clearTimeout(replotTimeout)
  resizeObserver.disconnect()
})
</script>

<style scoped></style>
