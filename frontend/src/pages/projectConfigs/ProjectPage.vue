<template>
  <div>
    <Card v-if="project">
      <template #title>Project "{{ project.name }}"</template>
      <template #content> General project page </template>
    </Card>

    <!-- This renders the child routes like energy-diagram, sites, etc. -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { useProjectDetails } from '@/backend/projects'
import { useRoute } from 'vue-router'

const route = useRoute()

const { data: project } = useProjectDetails(route)
</script>

<style scoped></style>
