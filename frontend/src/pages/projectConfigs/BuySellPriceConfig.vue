<template>
  <Card>
    <template #title>Buy-Sell-Price</template>
    <template #content>
      <SiteOverviewComponent>
        <template #default="{ site }">
          <BuySellPriceOverview :site="site" />
        </template>
      </SiteOverviewComponent>

      <div class="mt-3 flex justify-end gap-3">
        <Button
          @click="
            router.push({
              name: 'ProjectTimeVarEff',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          TimeVarEff >>
        </Button>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import SiteOverviewComponent from '@/components/SiteOverviewComponent.vue'
import BuySellPriceOverview from '@/components/BuySellPriceOverview.vue'

const route = useRoute()
const router = useRouter()
</script>

<style scoped></style>
