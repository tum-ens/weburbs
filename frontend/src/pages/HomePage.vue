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
              :show-actions="true"
              :download-loading="downloading === proj.name"
              component-type="project"
              @click="
                () =>
                  router.push({
                    name: 'ProjectSites',
                    params: {
                      proj: proj.name,
                    },
                  })
              "
              @duplicate="duplicate(proj.name)"
              @download="type => downloadProject(proj.name, type)"
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
import {
  downloadProjectConfig,
  downloadProjectExcel,
  triggerBlobDownload,
  useDuplicateProject,
  useProjectList,
} from '@/backend/projects'
import DefaultLayout from '@/layout/DefaultLayout.vue'
import CreateFromExcelDialog from '@/dialogs/CreateFromExcelDialog.vue'
import CreateFromConfigDialog from '@/dialogs/CreateFromConfigDialog.vue'
import DefaultProjectOverviewDialog from '@/dialogs/DefaultProjectOverviewDialog.vue'
import { useToast } from 'primevue/usetoast'
import type { AxiosError } from 'axios'

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
const toast = useToast()
const { mutateAsync: duplicateProject } = useDuplicateProject()
const downloading = ref<string | null>(null)

async function downloadProject(name: string, type: 'config' | 'excel') {
  if (downloading.value) return
  downloading.value = name
  const fallbackName = type === 'config' ? `${name}.urbs` : `${name}.xlsx`

  try {
    const response =
      type === 'config'
        ? await downloadProjectConfig(name)
        : await downloadProjectExcel(name)
    triggerBlobDownload(response, fallbackName)
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Download failed',
      detail:
        (<{ detail?: string }>(<AxiosError>err)?.response?.data)?.detail ||
        name,
      life: 4000,
    })
  } finally {
    downloading.value = null
  }
}

async function duplicate(name: string) {
  try {
    const res = await duplicateProject(name)
    toast.add({
      severity: 'success',
      summary: 'Project duplicated',
      detail: res.new_name,
      life: 3000,
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Duplicate failed',
      detail:
        (<{ detail?: string }>(<AxiosError>err)?.response?.data)?.detail ||
        name,
      life: 4000,
    })
  }
}

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
