<template>
  <div class="flex flex-col">
    <template v-if="commodities">
      <DemandCommodityOverview
        v-for="com in commodities"
        :key="com.name"
        :site="site"
        :commodity="com"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import type { Site } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import { useProjectSiteCommodities } from '@/backend/commodities'
import DemandCommodityOverview from '@/components/DemandCommodityOverview.vue'

const route = useRoute()

const props = defineProps<{
  site: Site
}>()

const { data: commodities } = useProjectSiteCommodities(route, props.site.name)
</script>

<style scoped></style>
