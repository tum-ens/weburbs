<template>
  <div class="w-screen min-h-screen bg-surface-100 dark:bg-surface-950">
    <router-view />
  </div>
  <Toast />
</template>

<script setup lang="ts">
import { provide, type Ref, ref } from 'vue'

const advanced = ref(false)
provide<Ref<boolean>>('advanced', advanced)
</script>

<style></style>
