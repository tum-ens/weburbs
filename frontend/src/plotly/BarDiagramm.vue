<template>
  <div :id="plotId" />
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import Plotly from 'plotly.js-dist'
import { v4 as uuid } from 'uuid'

const plotId = uuid()

const props = defineProps<{
  data: Partial<Plotly.Data>[]
  title?: string
  titleX: string
  titleY: string
}>()

function layout(): Partial<Plotly.Layout> {
  return {
    bargap: 0,
    bargroupgap: 0,
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

onMounted(() => {
  Plotly.newPlot(plotId, props.data, layout())
})

watch(props, () => {
  Plotly.newPlot(plotId, props.data, layout())
})
</script>

<style scoped></style>
