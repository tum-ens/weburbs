<template>
  <Card v-if="project">
    <template #title>Configure "{{ project.name }}"</template>
    <template #content>
      <ProjectForm
        submit-label="Update"
        :loading="pending"
        :project="project"
        @submit="update"
      />
    </template>
  </Card>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useProjectDetails, useUpdateProject } from '@/backend/projects'
import { useToast } from 'primevue/usetoast'
import ProjectForm from '@/forms/ProjectForm.vue'

const toast = useToast()
const route = useRoute()
const router = useRouter()

const { data: project } = useProjectDetails(route)
const { mutate: updateProject, isPending: pending } = useUpdateProject(route)

function update(
  name: string,
  description: string,
  co2limit: number,
  costlimit: number,
): void {
  updateProject(
    {
      name: name,
      description: description,
      co2limit: co2limit,
      costlimit: costlimit,
    },
    {
      onSuccess() {
        toast.add({
          summary: 'Success',
          detail: 'Project was saved',
          severity: 'success',
          life: 2000,
        })
        router.push({
          name: 'ProjectConfig',
          params: {
            proj: name,
          },
        })
      },
    },
  )
}
</script>

<style scoped></style>
