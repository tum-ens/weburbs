<template>
  <DefaultLayout>
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
  </DefaultLayout>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'
import { useUpdateProject } from '@/backend/projects'
import { useRoute, useRouter } from 'vue-router'
import ProjectForm from '@/forms/ProjectForm.vue'
import { defaultProject } from '@/backend/defaults'
import type { AxiosError } from 'axios'
import DefaultLayout from '@/layout/DefaultLayout.vue'

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
      onError(error) {
        toast.add({
          summary: 'Error',
          detail:
            (<AxiosError>error)?.response?.data ||
            `An error occurred when creating ${name}`,
          severity: 'error',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
