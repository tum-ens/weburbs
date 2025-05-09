<template>
  <div
    v-if="DSMs?.length"
    class="grid grid-cols-[repeat(auto-fill,minmax(12rem,1fr))] md:grid-cols-[repeat(auto-fill,minmax(17rem,1fr))] gap-3"
  >
    <Transformer
      v-for="dsm in DSMs"
      :key="dsm.commodity"
      :title="dsm.commodity"
      description=""
      :in="[]"
      :out="[]"
      @click="emit('clickedDSM', dsm)"
    />
  </div>
  <div v-else>
    <span>No storage added</span>
  </div>
</template>

<script setup lang="ts">
import Transformer from '@/components/TransformerComponent.vue'
import { useRoute } from 'vue-router'
import type { DSM, Site } from '@/backend/interfaces'
import { useDSM } from '@/backend/dsm'

const route = useRoute()

const props = defineProps<{
  site: Site
}>()
const emit = defineEmits<{
  clickedDSM: [dsm: DSM]
}>()

const { data: DSMs } = useDSM(route, props.site)
</script>

<style scoped></style>
