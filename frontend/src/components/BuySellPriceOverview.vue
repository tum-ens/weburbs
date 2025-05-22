<template>
  <divider />
  <div class="grid grid-cols-1 md:grid-cols-6 lg:grid-cols-8 gap-3">
    <div class="flex flex-col gap-3">
      <h1>{{ props.bsp.name }} - {{ BuySellPriceType[props.bsp.type] }}</h1>
      <FileUpload
        :disabled="!checkUploadFile"
        mode="basic"
        custom-upload
        choose-icon="pi pi-upload"
        class="w-full"
        choose-label="Upload"
        @select="event => upload(event)"
      >
        <!-- hide label -->
        <template #filelabel>
          <template />
        </template>
      </FileUpload>
      <Button :disabled="!checkUploadFile" @click="del" severity="danger">
        Delete
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

    <div class="md:col-span-5 lg:col-span-7 flex flex-col gap-3">
      <BarDiagramm
        :data="data"
        title-x="Steps"
        class="h-80"
        :bargroupgap="0.1"
        :margin="{ t: 20 }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { type BuySellPrice, BuySellPriceType } from '@/backend/interfaces'
import { computed, type Ref, ref } from 'vue'
import { useRoute } from 'vue-router'
import { chunkAdd, groupOptions } from '@/helper/diagrams'
import BarDiagramm from '@/plotly/PlotlyDiagram.vue'
import { FileUpload, type FileUploadSelectEvent } from 'primevue'
import { checkUploadFile } from '@/helper/upload'
import { useToast } from 'primevue/usetoast'
import {
  useDeleteBuySellPrice,
  useUploadBuySellPrice,
} from '@/backend/buysellprice'

const route = useRoute()
const toast = useToast()

const props = defineProps<{
  bsp: BuySellPrice
}>()
const profileUpload = ref<InstanceType<typeof FileUpload>>()
const checkingUpload = ref(false)

const groupOption = ref(groupOptions[0])

const { mutate: uploadBSP } = useUploadBuySellPrice(route, props.bsp)
const { mutate: deleteBSP } = useDeleteBuySellPrice(route, props.bsp)

const data: Ref<Partial<Plotly.Data>[]> = computed(() => {
  return [
    {
      name: props.bsp.name,
      y: chunkAdd(props.bsp.steps, groupOption.value.groupSize, 1),
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
      uploadBSP(res)
    })
    .catch(() => {})
    .finally(() => {
      // @ts-expect-error Wrong type description
      if (profileUpload.value) profileUpload.value.clear()
      checkingUpload.value = false
    })
}

function del() {
  checkingUpload.value = true
  deleteBSP(undefined, {
    onSuccess() {
      toast.add({
        summary: 'Success',
        detail: `BuySellPrice for ${props.bsp.name} was deleted`,
        severity: 'success',
        life: 2000,
      })
    },
    onSettled() {
      checkingUpload.value = false
    },
  })
}
</script>

<style scoped></style>
