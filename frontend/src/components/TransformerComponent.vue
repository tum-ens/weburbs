<template>
  <div
    class="flex flex-col justify-between rounded-2xl border-2 border-primary p-2 gap-3 text-center bg-surface-100 select-none hover:shadow-lg hover:cursor-pointer hover:bg-surface-200"
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
        <span class="pi pi-arrow-right"></span>
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
