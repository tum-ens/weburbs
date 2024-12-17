<template>
  <div class="flex flex-col">
    <Header v-model:sidebar="sidebar" />
    <div class="p-3 gap-3 flex flex-row">
      <SidebarComponent class="hidden lg:block" />
      <div class="flex-grow">
        <slot></slot>
      </div>
    </div>
  </div>
  <Drawer v-model:visible="sidebar" header="URBS">
    <SidebarContent />
  </Drawer>
</template>

<script setup lang="ts">
import Header from '@/components/HeaderComponent.vue'
import SidebarComponent from '@/layout/SidebarComponent.vue'
import { ref } from 'vue'
import SidebarContent from '@/layout/SidebarContent.vue'

const sidebar = ref(false)
</script>

<style scoped></style>
