<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    header="Config"
    modal
    class="w-11/12 md:w-10/12 xl:w-1/2"
  >
    <template #header>
      <span class="p-dialog-title">Config</span>
      <Button
        icon="pi pi-clipboard"
        severity="secondary"
        @click="copyToClipboard"
      />
      <Button
        icon="pi pi-download"
        severity="secondary"
        @click="downloadConfig"
      />
    </template>
    <p style="white-space: pre" class="overflow-y-scroll">
      {{ text }}
    </p>
  </Dialog>
</template>

<script setup lang="ts">
import { useGetSimulationConfig } from '@/backend/simulate'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { ref, watch } from 'vue'

const route = useRoute()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })

const { data: config } = useGetSimulationConfig(route)

async function copyToClipboard() {
  await navigator.clipboard.writeText(JSON.stringify(config.value))
  toast.add({
    summary: 'Success',
    detail: `Copied to clipboard`,
    severity: 'success',
    life: 2000,
  })
}

async function downloadConfig() {
  const fileContent = JSON.stringify(config.value)
  const fileName = route.params.proj + '.urbs'
  const blob = new Blob([fileContent], { type: 'text/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = fileName
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const text = ref('Loading config...')

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function stringifyJSON(value: any, level = 0): string {
  const space = ' '.repeat(level)

  if (Array.isArray(value)) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const arr = value as any[]
    if (arr.some(x => typeof x === 'number')) {
      return `[${arr.slice(0, 30).join(', ')}, ... ${arr.length - 30} more items]`
    } else {
      const items = arr.map(item => stringifyJSON(item, level + 1))
      return `[\n${items.map(item => space + ' ' + item).join(',\n')}\n]`
    }
  } else if (value !== null && typeof value === 'object') {
    const entries = Object.entries(value).map(([key, val]) => {
      return `${space} "${key}": ${stringifyJSON(val, level + 1)}`
    })
    return `{\n${entries.join(',\n')}\n${space}}`
  } else {
    return JSON.stringify(value)
  }
}

watch(
  config,
  () => {
    setTimeout(() => {
      text.value = stringifyJSON(config.value)
    }, 100)
  },
  { immediate: true },
)
</script>

<style scoped></style>
