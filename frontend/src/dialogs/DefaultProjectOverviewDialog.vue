<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Default Projects"
    class="w-11/12 md:w-10/12 xl:w-1/2 min-h-96"
  >
    <div
      v-if="def_projects?.length"
      class="grid grid-cols-[repeat(auto-fit,minmax(16rem,1fr))] gap-3"
    >
      <template v-for="def_proj in def_projects" :key="def_proj.name">
        <Transformer
          :title="def_proj.name"
          description=""
          :in="[]"
          :out="[]"
          @click="() => add(def_proj.name)"
        />
      </template>
    </div>
    <div v-else>
      <span>No default processes defined</span>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import Transformer from '@/components/TransformerComponent.vue'
import { useToast } from 'primevue/usetoast'
import type { AxiosError } from 'axios'
import { useDefProjects, useLoadDefProject } from '@/backend/projects'

const toast = useToast()

const visible = defineModel<boolean>('visible', { default: false })

const { data: def_projects } = useDefProjects()
const { mutate: loadDefProject } = useLoadDefProject()

function add(project_name: string) {
  visible.value = false
  loadDefProject(project_name, {
    onSuccess() {
      toast.add({
        summary: 'Added',
        detail: `Project ${project_name} has been loaded`,
        severity: 'success',
        life: 2000,
      })
    },
    onError(error) {
      toast.add({
        summary: 'Error adding',
        detail:
          (<AxiosError>error)?.response?.data ||
          `An error occurred when loading ${project_name}`,
        severity: 'error',
        life: 2000,
      })
    },
  })
}
</script>

<style scoped></style>
