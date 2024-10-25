<template>
  <div class="w-screen p-3">
    <Menubar :model="items" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const items = ref([
  {
    label: 'Home',
    icon: 'pi pi-home',
  },
])
</script>

<style scoped></style>
