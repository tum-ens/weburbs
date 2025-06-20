<template>
  <Dialog v-model:visible="visible" :draggable="false" header="Config" modal>
    <template #header>
      <span class="p-dialog-title">Config</span>
      <Button
        icon="pi pi-clipboard"
        severity="secondary"
        @click="copyToClipbaord"
      />
      <Button
        icon="pi pi-download"
        severity="secondary"
        @click="downloadConfig"
      />
    </template>
    <p style="white-space: pre-wrap">
      {{ config }}
    </p>
  </Dialog>
</template>

<script setup lang="ts">
import { useGetSimulationConfig } from '@/backend/simulate'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'

const route = useRoute()
const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })

const { data: config } = useGetSimulationConfig(route)

async function copyToClipbaord() {
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
</script>

<style scoped></style>
