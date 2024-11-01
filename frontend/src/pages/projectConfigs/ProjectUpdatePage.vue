<template>
  <Card>
    <template #title>Update Project</template>
    <template #content>
      <div class="flex flex-col gap-3">
        <FloatLabel variant="on">
          <InputText class="w-full" id="name" v-model="name" />
          <label for="name">Name</label>
        </FloatLabel>
        <FloatLabel variant="on">
          <Textarea class="w-full" id="description" v-model="description" />
          <label for="description">Description</label>
        </FloatLabel>
        <Button @click="create">Update</Button>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useProjectDetails, useUpdateProject } from '@/backend/projects'
import { useRoute, useRouter } from 'vue-router'

const toast = useToast()
const route = useRoute()
const router = useRouter()

const { data: project } = useProjectDetails(route)
const { mutate: updateProject } = useUpdateProject(route)

const name = ref('')
const description = ref('')
watch(
  project,
  () => {
    if (project.value) {
      name.value = project.value.name
      description.value = project.value.description
    }
  },
  {
    immediate: true,
  },
)

function create() {
  updateProject(
    { name: name.value, description: description.value },
    {
      onSuccess() {
        toast.add({
          summary: 'Success',
          detail: 'Project was create',
          severity: 'success',
          life: 2000,
        })
        router.push({
          name: 'Project',
          params: {
            proj: name.value,
          },
        })
      },
    },
  )
}
</script>

<style scoped></style>
