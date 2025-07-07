<template>
  <DefaultLayout>
    <Card>
      <template #title>
        <div class="flex flex-row justify-between">
          <span>Homepage</span>
          <SplitButton
            label="Create Project"
            @click="
              () =>
                router.push({
                  name: 'CreateProject',
                })
            "
            :model="items"
          />
        </div>
      </template>
      <template #content>
        <div
          v-if="projects?.length"
          class="grid grid-cols-[repeat(auto-fill,minmax(12rem,1fr))] md:grid-cols-[repeat(auto-fill,minmax(17rem,1fr))] gap-3"
        >
          <template v-for="proj in projects" :key="proj.name">
            <Transformer
              :title="proj.name"
              :description="proj.description"
              :in="[]"
              :out="[]"
              @click="
                () =>
                  router.push({
                    name: 'ProjectSites',
                    params: {
                      proj: proj.name,
                    },
                  })
              "
            />
          </template>
        </div>
      </template>
    </Card>
  </DefaultLayout>

  <CreateFromExcelDialog v-model:visible="createFExcelVisible" />
  <CreateFromConfigDialog v-model:visible="createFConfigVisible" />
  <DefaultProjectOverviewDialog v-model:visible="showDefaultsVisible" />
</template>

<script setup lang="ts">
import { useAuthenticated } from '@/backend/security'
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Transformer from '@/components/TransformerComponent.vue'
import { useProjectList } from '@/backend/projects'
import DefaultLayout from '@/layout/DefaultLayout.vue'
import CreateFromExcelDialog from '@/dialogs/CreateFromExcelDialog.vue'
import CreateFromConfigDialog from '@/dialogs/CreateFromConfigDialog.vue'
import DefaultProjectOverviewDialog from '@/dialogs/DefaultProjectOverviewDialog.vue'

const { data: authenticated } = useAuthenticated()
const router = useRouter()
const route = useRoute()
watch(
  authenticated,
  () => {
    if (!authenticated.value) {
      router.push({
        name: 'Login',
        query: {
          redirect: route.fullPath,
        },
      })
    }
  },
  { immediate: true },
)

const { data: projects } = useProjectList()

const items = [
  {
    label: 'Create from Excel',
    command: () => {
      createFExcelVisible.value = true
    },
  },
  {
    label: 'Create from Config',
    command: () => {
      createFConfigVisible.value = true
    },
  },
  {
    label: 'Load Default',
    command: () => {
      showDefaultsVisible.value = true
    },
  },
]

const createFExcelVisible = ref(false)
const createFConfigVisible = ref(false)
const showDefaultsVisible = ref(false)
</script>

<style scoped></style>
