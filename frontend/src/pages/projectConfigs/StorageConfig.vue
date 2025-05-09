<template>
  <Card>
    <template #title>
      <div class="flex flex-row justify-between">
        <span>Storage</span>
        <SplitButton
          v-if="advanced"
          :disabled="!curSite"
          label="Add Preset"
          @click="() => (defaultVisible = true)"
          :model="items"
        />
        <Button
          v-else
          :disabled="!curSite"
          label="Add Preset"
          @click="() => (defaultVisible = true)"
        />
      </div>
    </template>
    <template #content>
      <SiteOverviewComponent v-model:cur-site="curSite">
        <template #default="{ site }">
          <StorageOverviewComponent
            :site="site"
            @clickStorage="
              sto => {
                clickedStorage = sto
                editVisible = true
              }
            "
          />
        </template>
      </SiteOverviewComponent>

      <div class="mt-3 flex justify-end gap-3">
        <Button
          v-if="advanced"
          severity="info"
          @click="
            router.push({
              name: 'ProjectTransmission',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Transmission >>
        </Button>
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
      </div>
    </template>
  </Card>
  <DefaultStorageOverviewDialog
    v-if="curSite != null"
    v-model:visible="defaultVisible"
    :site_name="curSite"
  />
  <CreateStorageDialog
    v-if="advanced && curSite != null"
    v-model:visible="createVisible"
    :site_name="curSite"
  />
  <EditStorageDialog
    v-if="curSite != null && clickedStorage"
    :storage="clickedStorage"
    v-model:visible="editVisible"
    :site_name="curSite"
  />
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { inject, ref } from 'vue'
import DefaultStorageOverviewDialog from '@/dialogs/DefaultStorageOverviewDialog.vue'
import StorageOverviewComponent from '@/components/StorageOverviewComponent.vue'
import CreateStorageDialog from '@/dialogs/CreateStorageDialog.vue'
import EditStorageDialog from '@/dialogs/EditStorageDialog.vue'
import type { Storage } from '@/backend/interfaces'
import SiteOverviewComponent from '@/components/SiteOverviewComponent.vue'

const route = useRoute()
const router = useRouter()

const advanced = inject('advanced')

const curSite = ref()
const defaultVisible = ref(false)
const createVisible = ref(false)
const editVisible = ref(false)

const clickedStorage = ref<Storage | null>(null)

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
