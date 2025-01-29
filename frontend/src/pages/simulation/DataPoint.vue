<template>
  <div class="flex flex-col gap-3 items-center">
    <span class="text-center">{{ props.name }}</span>
    <Chip
      :label="props.value.toFixed(2) + (props.suffix || '')"
      :class="props.classes"
    />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  name: string
  value: number
  suffix?: string
  classes?: string
}>()
</script>

<style scoped></style>
