<template>
  <div
    v-if="processes?.length"
    class="grid grid-cols-[repeat(auto-fill,minmax(12rem,1fr))] md:grid-cols-[repeat(auto-fill,minmax(17rem,1fr))] gap-3"
  >
    <template v-for="proc in processes" :key="proc.name">
      <Transformer
        v-if="(proc.in.length !== 0 && proc.out.length !== 0) || advanced"
        :title="proc.name"
        :description="proc.description"
        :in="proc.in.map(proccom => proccom.name)"
        :out="proc.out.map(proccom => proccom.name)"
        @click="emit('clickProcess', proc)"
      />
    </template>
  </div>
  <div v-else>
    <span>No processes added</span>
  </div>
</template>

<script setup lang="ts">
import { useProcesses } from '@/backend/processes'
import Transformer from '@/components/TransformerComponent.vue'
import { useRoute } from 'vue-router'
import type { Process, Site } from '@/backend/interfaces'
import { inject } from 'vue'

const route = useRoute()

const advanced = inject('advanced')

const props = defineProps<{
  site: Site
}>()
const emit = defineEmits<{
  clickProcess: [process: Process]
}>()

const { data: processes } = useProcesses(route, props.site)
</script>

<style scoped></style>
