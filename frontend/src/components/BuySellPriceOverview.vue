<template>
  <div class="flex flex-col">
    <template v-if="commodities">
      <template v-for="com in commodities" :key="com.name">
        <BuySellPriceCommodityOverview :site="site" :commodity="com" />
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { Site } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import BuySellPriceCommodityOverview from '@/components/BuySellPriceCommodityOverview.vue'
import { useCommodities } from '@/backend/commodities'

const route = useRoute()

const props = defineProps<{
  site: Site
}>()

const { data: commodities } = useCommodities(route, props.site)
</script>

<style scoped></style>
