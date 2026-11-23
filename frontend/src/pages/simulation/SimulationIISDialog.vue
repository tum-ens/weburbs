<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    header="IIS – conflicting constraints (model.ilp)"
    modal
    :style="{ width: '60rem', maxWidth: '95vw' }"
  >
    <div class="flex flex-col gap-3">
      <p class="m-0 text-surface-600 dark:text-surface-300">
        These constraints and bounds together make the model infeasible.
        Relaxing any one of them is enough to make it feasible.
      </p>
      <pre
        class="m-0 max-h-[60vh] overflow-auto whitespace-pre rounded bg-surface-100 p-4 font-mono text-sm dark:bg-surface-800"
        >{{ content || 'No IIS content available.' }}</pre
      >
    </div>
    <template #footer>
      <Button
        severity="info"
        icon="pi pi-download"
        label="Download .ilp"
        @click="emit('download')"
      />
      <Button label="Close" text @click="visible = false" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
defineProps<{ content: string }>()
const emit = defineEmits<{ (e: 'download'): void }>()
const visible = defineModel<boolean>('visible', { default: false })
</script>

<style scoped></style>
