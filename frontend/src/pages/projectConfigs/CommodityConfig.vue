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
            @duplicateCommodity="
              commodity => {
                duplicateCommodity(commodity)
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
    :from_energy_diagram="route.query.from === 'energy-diagram'"
  />
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { ref, watch, computed } from 'vue'
import { useSites } from '@/backend/sites'
import {
  useProjectSiteCommodities,
  useDuplicateCommodity,
} from '@/backend/commodities'
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

// Duplicate commodity functionality
const duplicateCommodityMutation = useDuplicateCommodity(route)

const duplicateCommodity = async (commodity: Commodity) => {
  try {
    await duplicateCommodityMutation.mutateAsync({
      site_name: curSite.value,
      commodity_name: commodity.name,
    })
  } catch (error) {
    console.error('Failed to duplicate commodity:', error)
  }
}

// Get commodities data for the current site
const { data: commodities } = useProjectSiteCommodities(
  route,
  computed(() => curSite.value),
)

// Watch for site changes to reload commodities
watch(curSite, newSite => {
  console.log('Site changed to:', newSite)
  if (newSite && route.query.autoEdit === 'true' && route.query.edit) {
    console.log(
      'Site changed, checking for auto-edit commodity:',
      route.query.edit,
    )
  }
})

watch(
  sites,
  () => {
    if (!curSite.value && sites.value) {
      curSite.value = sites.value[0].name
    }
  },
  { immediate: true },
)

// Watch for query parameters to auto-open edit dialog or create dialog
watch(
  () => route.query,
  query => {
    console.log('Route query changed:', query)

    // Handle auto-edit for existing commodities
    if (query.autoEdit === 'true' && query.edit && query.site) {
      console.log(
        'Auto-edit triggered for commodity:',
        query.edit,
        'at site:',
        query.site,
      )
      curSite.value = query.site as string

      // Wait for commodities to load and then find the target commodity
      watch(
        commodities,
        comms => {
          console.log('Commodities data loaded:', comms?.length, 'items')
          if (comms) {
            const targetCommodity = comms.find(c => c.name === query.edit)
            console.log(
              'Looking for commodity:',
              query.edit,
              'Found:',
              targetCommodity,
            )
            if (targetCommodity) {
              clickedCommodity.value = targetCommodity
              editVisible.value = true
              console.log(
                '✅ Auto-opening edit dialog for commodity:',
                targetCommodity.name,
              )
            } else {
              console.warn(
                '❌ Commodity not found:',
                query.edit,
                'Available:',
                comms.map(c => c.name),
              )
            }
          }
        },
        { immediate: true },
      )
    }

    // Handle auto-create for new commodities
    if (
      query.create === 'true' &&
      query.site &&
      query.from === 'energy-diagram'
    ) {
      console.log('Auto-create triggered for commodity at site:', query.site)
      curSite.value = query.site as string

      // Wait for sites to load and then open create dialog
      watch(
        sites,
        sitesData => {
          if (sitesData && sitesData.length > 0) {
            createVisible.value = true
            console.log('✅ Auto-opening create dialog for commodity')
          }
        },
        { immediate: true },
      )
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
