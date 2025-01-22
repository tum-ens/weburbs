<template>
  <div
    v-if="commodities?.length"
    class="grid grid-cols-[repeat(auto-fill,minmax(12rem,1fr))] md:grid-cols-[repeat(auto-fill,minmax(17rem,1fr))] gap-3"
  >
    <template v-for="com in commodities" :key="com.name">
      <Transformer
        :title="com.name"
        :description="commodityTypeToName(com.type)"
        :in="[]"
        :out="[]"
        @click="emit('clickCommodity', com)"
      />
    </template>
  </div>
  <div v-else>
    <span>No commodities added</span>
  </div>
</template>

<script setup lang="ts">
import Transformer from '@/components/TransformerComponent.vue'
import { useRoute } from 'vue-router'
import {
  type Commodity,
  commodityTypeToName,
  type Site,
} from '@/backend/interfaces'
import { useCommodities } from '@/backend/commodities'

const route = useRoute()

const props = defineProps<{
  site: Site
}>()
const emit = defineEmits<{
  clickCommodity: [commodity: Commodity]
}>()

const { data: commodities } = useCommodities(route, props.site)
</script>

<style scoped></style>
