<template>
  <div class="flex flex-col">
    <template v-if="commodities">
      <template v-for="com in commodities" :key="com.name">
        <DemandCommodityOverview
          :site="site"
          :commodity="com"
          v-if="com.type == 2"
        />
      </template>
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
