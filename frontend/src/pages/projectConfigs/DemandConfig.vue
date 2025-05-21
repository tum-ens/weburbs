<template>
  <Card>
    <template #title>Demand</template>
    <template #content>
      <SiteOverviewComponent v-model:cur-site="curSite">
        <template #default="{ site }">
          <DemandOverview :site="site" />
        </template>
      </SiteOverviewComponent>

      <div class="mt-3 flex justify-end">
        <Button
          v-if="advanced"
          @click="
            router.push({
              name: 'ProjectProcess',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Processes >>
        </Button>
        <Button
          v-else
          @click="
            router.push({
              name: 'ProjectProcess',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Processes >>
        </Button>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import DemandOverview from '@/components/DemandOverview.vue'
import { inject, ref } from 'vue'
import SiteOverviewComponent from '@/components/SiteOverviewComponent.vue'

const route = useRoute()
const router = useRouter()

const advanced = inject('advanced')

const curSite = ref('')
</script>

<style scoped></style>
