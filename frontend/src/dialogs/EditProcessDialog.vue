<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Default Processes"
    class="w-1/2 min-h-96"
  >
    <ProcessForm
      :process="process"
      submit-label="Update"
      :loading="loading"
      @submit="update"
      :site_name="site_name"
    />
  </Dialog>
</template>

<script setup lang="ts">
import ProcessForm from '@/forms/ProcessForm.vue'
import type { Process } from '@/backend/interfaces'
import { ref } from 'vue'

const visible = defineModel<boolean>('visible', { default: false })
defineProps<{
  site_name: string
  process: Process
}>()

const loading = ref(false)

function update(process: Process): void {}
</script>

<style scoped></style>
