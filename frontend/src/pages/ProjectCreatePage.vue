<template>
  <Card>
    <template #title>Create Project</template>
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
        <Button @click="create">Create</Button>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

const name = ref('')
const description = ref('')

function create() {
  toast.add({
    summary: 'Success',
    detail: 'Project was create',
    severity: 'success',
    life: 2000,
  })
}
</script>

<style scoped></style>
