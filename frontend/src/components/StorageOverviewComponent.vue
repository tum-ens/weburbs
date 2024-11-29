<template>
  <div
    v-if="storage?.length"
    class="grid grid-cols-[repeat(auto-fill,minmax(12rem,1fr))] md:grid-cols-[repeat(auto-fill,minmax(17rem,1fr))] gap-3"
  >
    <Transformer
      v-for="sto in storage"
      :key="sto.name"
      :title="sto.name"
      :description="sto.description"
      :in="[sto.commodity]"
      :out="[sto.commodity]"
      @click="
        () =>
          toast.add({
            severity: 'info',
            summary: 'TODO',
            detail: 'Not yet implemented',
            life: 3000,
          })
      "
    />
  </div>
  <div v-else>
    <span>No storage added</span>
  </div>
</template>

<script setup lang="ts">
import Transformer from '@/components/TransformerComponent.vue'
import { useRoute } from 'vue-router'
import type { Site } from '@/backend/interfaces'
import { useStorage } from '@/backend/storage'
import { useToast } from 'primevue/usetoast'

const route = useRoute()
const toast = useToast()

const props = defineProps<{
  site: Site
}>()

const { data: storage } = useStorage(route, props.site)
</script>

<style scoped></style>
