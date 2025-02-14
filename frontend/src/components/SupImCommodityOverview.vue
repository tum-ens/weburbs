<template>
  <divider />
  <div class="grid grid-cols-8 gap-3">
    <div class="flex flex-col gap-3">
      <h1>{{ commodity.name }}</h1>
      <Button @click="query" :disabled="!!supim?.data" label="Query SupIm" />
      <FileUpload
        v-if="advanced"
        mode="basic"
        custom-upload
        class="w-full"
        choose-label="Upload"
        choose-icon="pi pi-upload"
        :choose-button-props="{
          loading: checkingUpload,
          disabled: !!supim?.data || checkingUpload,
        }"
        @select="upload"
      >
        <!-- hide label -->
        <template #filelabel><template /></template>
      </FileUpload>
      <Button @click="del" severity="danger" :disabled="!supim?.data">
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

    <div v-if="supim?.data" class="col-span-7">
      <BarDiagramm
        :data
        title-x="Steps"
        :title-y="commodity.unitC"
        class="h-80"
        :bargroupgap="0.1"
        :margin="{ t: 20 }"
      />
    </div>
    <Skeleton v-else-if="pending" class="col-span-7" style="height: 10rem" />
    <div v-else class="ml-5 italic col-span-7">No SupIm configured</div>
  </div>
  <QuerySupImDialog :site :commodity v-model="queryVisible" />
</template>

<script setup lang="ts">
import type { Commodity, Site } from '@/backend/interfaces'
import Plotly from 'plotly.js-dist'
import { computed, inject, ref, type Ref } from 'vue'
import { useDeleteSupIm, useGetSupIm, useUploadSupIm } from '@/backend/supim'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import BarDiagramm from '@/plotly/PlotlyDiagram.vue'
import QuerySupImDialog from '@/dialogs/QuerySupImDialog.vue'
import { chunkAdd, groupOptions } from '@/helper/diagrams'
import { FileUpload, type FileUploadSelectEvent } from 'primevue'
import { checkUploadFile } from '@/helper/upload'

const route = useRoute()
const toast = useToast()

const advanced = inject('advanced')

const queryVisible = ref(false)

const profileUpload = ref<InstanceType<typeof FileUpload>>()
const checkingUpload = ref(false)

const props = defineProps<{
  site: Site
  commodity: Commodity
}>()

const groupOption = ref(groupOptions[0])

const { data: supim, isPending: pending } = useGetSupIm(
  route,
  props.site,
  props.commodity,
)
const { mutate: deleteSupIm } = useDeleteSupIm(
  route,
  props.site,
  props.commodity,
)

const data: Ref<Partial<Plotly.Data>[]> = computed(() => {
  if (!supim.value?.data) return []
  return [
    {
      name: props.commodity.name,
      y: chunkAdd(supim.value.data, groupOption.value.groupSize),
      x: Array.from({ length: groupOption.value.groups }, (_, i) => i + 1),
      type: 'bar',
      marker: {
        color: props.commodity.name.includes('Solar') ? 'gold' : undefined,
      },
    },
  ]
})

function del() {
  deleteSupIm(undefined, {
    onSuccess() {
      toast.add({
        summary: 'Success',
        detail: `SupIm for ${props.commodity.name} was deleted`,
        severity: 'success',
        life: 2000,
      })
    },
  })
}

function query() {
  queryVisible.value = true
}

const { mutate: uploadSupIm } = useUploadSupIm(
  route,
  props.site,
  props.commodity,
)
async function upload(event: FileUploadSelectEvent) {
  checkingUpload.value = true
  const file = event.files[0]
  const reader = new FileReader()

  reader.onload = async e => {
    if (e.target) {
      if (checkUploadFile(toast, e.target.result)) {
        uploadSupIm(JSON.parse(<string>e.target.result))
      }
      // @ts-expect-error Wrong type description
      if (profileUpload.value) profileUpload.value.clear()
      checkingUpload.value = false
    } else {
      toast.add({
        summary: 'Upload error',
        detail: `Something went wrong when reading file ${file.name}`,
        severity: 'error',
        life: 2000,
      })
    }
    // setTimeout(() => checkingUpload.value = false, 4000)
  }
  reader.readAsText(file)
}
</script>

<style scoped></style>
