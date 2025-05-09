<template>
  <Card>
    <template #title>
      <div class="flex flex-row justify-between">
        <span>DSM</span>
        <Button label="Add DSM" @click="createVisible = true" /></div
    ></template>
    <template #content>
      <SiteOverviewComponent v-model:cur-site="curSite">
        <template #default="{ site }">
          <DSMOverviewComponent
            :site="site"
            @clickedDSM="
              dsm => {
                clickedDSM = dsm
                editVisible = true
              }
            "
          />
        </template>
      </SiteOverviewComponent>

      <div class="mt-3 flex justify-end gap-3">
        <Button
          @click="
            router.push({
              name: 'ProjectDSM',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Buy-Sell-Price >>
        </Button>
      </div>
    </template>
  </Card>
  {{ editVisible }}
  {{ createVisible }}
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { ref } from 'vue'
import SiteOverviewComponent from '@/components/SiteOverviewComponent.vue'
import DSMOverviewComponent from '@/components/DSMOverviewComponent.vue'
import type { DSM } from '@/backend/interfaces'

const route = useRoute()
const router = useRouter()

const curSite = ref()
const createVisible = ref(false)
const editVisible = ref(false)

const clickedDSM = ref<DSM | null>(null)
</script>

<style scoped></style>
