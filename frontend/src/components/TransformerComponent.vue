<template>
  <div
    class="flex flex-col justify-between rounded-2xl border-2 border-primary p-2 gap-3 text-center max-w-xl bg-surface-100 dark:bg-surface-800 select-none hover:shadow-lg hover:cursor-pointer hover:bg-surface-200 dark:hover:bg-surface-700"
  >
    <div class="flex flex-col gap-3">
      <span>{{ title }}</span>
      <span>{{ description }}</span>
    </div>
    <div class="grid grid-cols-3">
      <div class="flex flex-col justify-center">
        <span v-for="i in props.in" :key="i">{{ i }}</span>
      </div>
      <div class="flex flex-col justify-center min-h-20">
        <span
          v-if="props.in.length > 0 || props.out.length > 0"
          class="pi pi-arrow-right"
        ></span>
      </div>
      <div class="flex flex-col justify-center">
        <span v-for="o in props.out" :key="o">{{ o }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string
  description: string
  in: string[]
  out: string[]
}>()
</script>

<style scoped></style>
