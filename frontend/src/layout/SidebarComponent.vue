<template>
  <Card class="w-80">
    <template #content>
      <ScrollPanel>
        <SidebarContent />
      </ScrollPanel>
    </template>
  </Card>
</template>

<script setup lang="ts">
import SidebarContent from '@/layout/SidebarContent.vue'
</script>

<style scoped></style>
