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
            @duplicateStorage="
              sto => {
                duplicateStorage(sto)
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
    :from_energy_diagram="route.query.from === 'energy-diagram'"
  />
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { inject, ref, watch } from 'vue'
import DefaultStorageOverviewDialog from '@/dialogs/DefaultStorageOverviewDialog.vue'
import StorageOverviewComponent from '@/components/StorageOverviewComponent.vue'
import { useDuplicateStorage } from '@/backend/storage'
import { useQuery } from '@tanstack/vue-query'
import axios from 'axios'
import CreateStorageDialog from '@/dialogs/CreateStorageDialog.vue'
import EditStorageDialog from '@/dialogs/EditStorageDialog.vue'
import type { Storage } from '@/backend/interfaces'
import SiteOverviewComponent from '@/components/SiteOverviewComponent.vue'
import { useSites } from '@/backend/sites'

const route = useRoute()
const router = useRouter()

const advanced = inject('advanced')

const curSite = ref()
const defaultVisible = ref(false)
const createVisible = ref(false)
const editVisible = ref(false)

const clickedStorage = ref<Storage | null>(null)

const { data: sites } = useSites(route)

// Duplicate storage functionality
const duplicateStorageMutation = useDuplicateStorage(route)

const duplicateStorage = async (storage: Storage) => {
  try {
    await duplicateStorageMutation.mutateAsync({
      site_name: curSite.value,
      storage_name: storage.name,
    })
  } catch (error) {
    console.error('Failed to duplicate storage:', error)
  }
}
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
    // Handle auto-edit for existing storage
    if (query.autoEdit === 'true' && query.edit && query.site) {
      curSite.value = query.site as string

      // Get storage for the specified site
      const { data: storage } = useQuery({
        queryKey: ['storage', route.params.proj, query.site],
        queryFn: () => {
          return axios
            .get<
              Storage[]
            >(`/api/project/${route.params.proj}/site/${query.site}/storage/`)
            .then(response => response.data)
        },
        enabled: !!query.site,
      })

      watch(
        storage,
        storageItems => {
          if (storageItems) {
            const targetStorage = storageItems.find(s => s.name === query.edit)
            if (targetStorage) {
              clickedStorage.value = targetStorage
              editVisible.value = true
              console.log(
                'Auto-opening edit dialog for storage:',
                targetStorage.name,
              )
            }
          }
        },
        { immediate: true },
      )
    }

    // Handle auto-create for new storage
    if (
      query.create === 'true' &&
      query.site &&
      query.from === 'energy-diagram'
    ) {
      console.log('Auto-create triggered for storage at site:', query.site)
      curSite.value = query.site as string

      // Wait for sites to load and then open create dialog
      watch(
        sites,
        sitesData => {
          if (sitesData && sitesData.length > 0) {
            createVisible.value = true
            console.log('✅ Auto-opening create dialog for storage')
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
