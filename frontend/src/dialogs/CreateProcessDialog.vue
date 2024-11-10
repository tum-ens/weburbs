<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Default Processes"
    class="w-11/12 md:w-10/12 xl:w-1/2 min-h-96"
  >
    <ProcessForm
      submit-label="Create"
      :loading="loading"
      @submit="update"
      :site_name="site_name"
    />
  </Dialog>
</template>

<script setup lang="ts">
import ProcessForm from '@/forms/ProcessForm.vue'
import { ref } from 'vue'
import type { Process } from '@/backend/interfaces'

const visible = defineModel<boolean>('visible', { default: false })
defineProps<{
  site_name: string
}>()

const loading = ref(false)

function update(process: Process): void {}
</script>

<style scoped></style>
