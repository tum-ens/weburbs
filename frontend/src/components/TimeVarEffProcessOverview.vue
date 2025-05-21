<template>
  <divider />
  <div class="grid grid-cols-1 md:grid-cols-6 lg:grid-cols-8 gap-3">
    <div class="flex flex-col gap-3">
      <h1>{{ process.name }}</h1>
      <FileUpload
        mode="basic"
        custom-upload
        choose-icon="pi pi-upload"
        class="w-full"
        choose-label="Upload"
        @select="upload"
      >
        <!-- hide label -->
        <template #filelabel><template /></template>
      </FileUpload>
      <Button @click="del" severity="danger" :disabled="!steps?.data">
        Delete SupIm
      </Button>
      <FloatLabel variant="on">
        <Select
          fluid
          id="groupoptions"
          :options="groupOptions"
          optionLabel="name"
          v-model="groupOption"
        />
        <label for="groupoptions">Group values</label>
      </FloatLabel>
    </div>

    <div
      v-if="steps && steps.data && steps.data.length > 0"
      class="md:col-span-5 lg:col-span-7"
    >
      <BarDiagramm
        :data="data"
        title-x="Steps"
        class="h-80"
        :bargroupgap="0.1"
        :margin="{ t: 20 }"
      />
    </div>
    <Skeleton v-else-if="pending" class="col-span-7" style="height: 10rem" />
    <div v-else class="ml-5 italic col-span-7">TimeVarEff not configured</div>
  </div>
</template>

<script setup lang="ts">
import type { Process, Site } from '@/backend/interfaces'
import { computed, type Ref, ref } from 'vue'
import { useRoute } from 'vue-router'
import { chunkAdd, groupOptions } from '@/helper/diagrams'
import BarDiagramm from '@/plotly/PlotlyDiagram.vue'
import {
  useDeleteTimeVarEff,
  useGetTimeVarEff,
  useUploadTimeVarEff,
} from '@/backend/timevareff'
import { FileUpload, type FileUploadSelectEvent } from 'primevue'
import { checkUploadFile } from '@/helper/upload'
import { useToast } from 'primevue/usetoast'

const route = useRoute()
const toast = useToast()

const props = defineProps<{
  site: Site
  process: Process
}>()
const profileUpload = ref<InstanceType<typeof FileUpload>>()
const checkingUpload = ref(false)

const groupOption = ref(groupOptions[0])

const { data: steps, isPending: pending } = useGetTimeVarEff(
  route,
  props.site,
  props.process,
)
const { mutate: uploadTimeVarEff } = useUploadTimeVarEff(
  route,
  props.site,
  props.process,
)
const { mutate: deleteTimeVarEff } = useDeleteTimeVarEff(
  route,
  props.site,
  props.process,
)

const data: Ref<Partial<Plotly.Data>[]> = computed(() => {
  if (!steps.value || !steps.value.data) return []
  return [
    {
      name: props.process.name,
      y: chunkAdd(steps.value.data, groupOption.value.groupSize, 1),
      x: Array.from({ length: groupOption.value.groups }, (_, i) => i + 1),
      type: 'bar',
    },
  ]
})

async function upload(event: FileUploadSelectEvent) {
  checkingUpload.value = true
  const file = event.files[0]

  checkUploadFile(toast, file)
    .then(res => {
      uploadTimeVarEff(res)
    })
    .catch(() => {})
    .finally(() => {
      // @ts-expect-error Wrong type description
      if (profileUpload.value) profileUpload.value.clear()
      checkingUpload.value = false
    })
}
function del() {
  deleteTimeVarEff(undefined, {
    onSuccess() {
      toast.add({
        summary: 'Success',
        detail: `TimeVarEff for ${props.process.name} was deleted`,
        severity: 'success',
        life: 2000,
      })
    },
  })
}
</script>

<style scoped></style>
