<template>
  <Card>
    <template #title>Create Project</template>
    <template #content>
      <ProjectForm
        submit-label="Create"
        :loading="pending"
        :project="defaultProject"
        @submit="create"
      />
    </template>
  </Card>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'
import { useUpdateProject } from '@/backend/projects'
import { useRoute, useRouter } from 'vue-router'
import ProjectForm from '@/forms/ProjectForm.vue'
import { defaultProject } from '@/backend/defaults'

const toast = useToast()
const route = useRoute()
const router = useRouter()

const { mutate: createProject, isPending: pending } = useUpdateProject(route)

function create(
  name: string,
  description: string,
  co2limit: number,
  costlimit: number,
) {
  createProject(
    { name, description, co2limit, costlimit },
    {
      onSuccess() {
        toast.add({
          summary: 'Success',
          detail: 'Project was create',
          severity: 'success',
          life: 2000,
        })
        router.push({
          name: 'ProjectSites',
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
