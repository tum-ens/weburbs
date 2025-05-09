<template>
  <Card>
    <template #title>
      <div class="flex flex-row justify-between">
        <span>Commodities</span>
        <SplitButton
          :disabled="!curSite"
          label="Add Preset"
          @click="() => (defaultVisible = true)"
          :model="items"
        />
      </div>
    </template>
    <template #content>
      <SiteOverviewComponent v-model:cur-site="curSite">
        <template #default="{ site }">
          <CommodityOverviewComponent
            :site="site"
            @clickCommodity="
              commodity => {
                clickedCommodity = commodity
                editVisible = true
              }
            "
          />
        </template>
      </SiteOverviewComponent>

      <div class="mt-3 flex justify-end">
        <Button
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
  <DefaultCommodityOverviewDialog
    v-if="curSite != null"
    v-model:visible="defaultVisible"
    :site_name="curSite"
  />
  <CreateCommodityDialog
    v-if="curSite != null"
    v-model:visible="createVisible"
    :site_name="curSite"
  />
  <EditCommodityDialog
    v-if="curSite != null && clickedCommodity"
    :commodity="clickedCommodity"
    v-model:visible="editVisible"
    :site_name="curSite"
  />
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { ref, watch } from 'vue'
import { useSites } from '@/backend/sites'
import CommodityOverviewComponent from '@/components/CommodityOverviewComponent.vue'
import type { Commodity } from '@/backend/interfaces'
import DefaultCommodityOverviewDialog from '@/dialogs/DefaultCommodityOverviewDialog.vue'
import CreateCommodityDialog from '@/dialogs/CreateCommodityDialog.vue'
import EditCommodityDialog from '@/dialogs/EditCommodityDialog.vue'
import SiteOverviewComponent from '@/components/SiteOverviewComponent.vue'

const route = useRoute()
const router = useRouter()

const curSite = ref()
const defaultVisible = ref(false)
const createVisible = ref(false)
const editVisible = ref(false)

const clickedCommodity = ref<Commodity | null>(null)

const { data: sites } = useSites(route)
watch(
  sites,
  () => {
    if (!curSite.value && sites.value) {
      curSite.value = sites.value[0].name
    }
  },
  { immediate: true },
)

const items = [
  {
    label: 'Add Custom',
    command: () => {
      createVisible.value = true
    },
  },
]
</script>

<style scoped></style>
