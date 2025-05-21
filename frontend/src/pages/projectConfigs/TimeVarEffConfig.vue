<template>
  <Card>
    <template #title>TimeVarEff</template>
    <template #content>
      <SiteOverviewComponent v-model:cur-site="curSite">
        <template #default="{ site }">
          <TimeVarEffOverview :site="site" />
        </template>
      </SiteOverviewComponent>

      <div class="mt-3 flex justify-end gap-3">
        <Button
          @click="
            router.push({
              name: 'ProjectSimulation',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Simulation >>
        </Button>
      </div></template
    >
  </Card>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import SiteOverviewComponent from '@/components/SiteOverviewComponent.vue'
import { ref } from 'vue'
import TimeVarEffOverview from '@/components/TimeVarEffOverview.vue'

const route = useRoute()
const router = useRouter()

const curSite = ref('')
</script>

<style scoped></style>
