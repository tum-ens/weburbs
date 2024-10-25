<template>
  <div class="bg-surface-50 dark:bg-surface-950">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { provide, ref } from 'vue'

const authenticated = ref(false)
provide('authenticated', authenticated)
</script>

<style></style>
