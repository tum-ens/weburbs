<template>
  <divider />
  <div class="grid grid-cols-1 md:grid-cols-6 lg:grid-cols-8 gap-3">
    <div class="flex flex-col gap-3">
      <h1>{{ commodity.name }}</h1>
      <FileUpload
        mode="basic"
        custom-upload
        choose-icon="pi pi-upload"
        class="w-full"
        choose-label="Upload buy"
        @select="event => upload(event, true)"
      >
        <!-- hide label -->
        <template #filelabel>
          <template />
        </template>
      </FileUpload>
      <FileUpload
        mode="basic"
        custom-upload
        choose-icon="pi pi-upload"
        class="w-full"
        choose-label="Upload sell"
        @select="event => upload(event, false)"
      >
        <!-- hide label -->
        <template #filelabel>
          <template />
        </template>
      </FileUpload>
      <Button
        @click="del"
        severity="danger"
        :disabled="!steps?.buy && !steps?.sell"
      >
        Delete BuySellPrice
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

    <div v-if="steps" class="md:col-span-5 lg:col-span-7 flex flex-col gap-3">
      <BarDiagramm
        v-if="steps.buy"
        :data="dataBuy"
        title-x="Steps"
        :title-y="commodity.unitC"
        class="h-80"
        :bargroupgap="0.1"
        :margin="{ t: 20 }"
      />
      <Skeleton v-else-if="pending" class="col-span-7" style="height: 10rem" />
      <div v-else class="ml-5 italic col-span-7">
        BuySellPrice buy not configured
      </div>
      <BarDiagramm
        v-if="steps.sell"
        :data="dataSell"
        title-x="Steps"
        :title-y="commodity.unitC"
        class="h-80"
        :bargroupgap="0.1"
        :margin="{ t: 20 }"
      />
      <Skeleton v-else-if="pending" class="col-span-7" style="height: 10rem" />
      <div v-else class="ml-5 italic col-span-7">
        BuySellPrice sell not configured
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  BuySellPriceType,
  type Commodity,
  type Site,
} from '@/backend/interfaces'
import { computed, type Ref, ref } from 'vue'
import { useRoute } from 'vue-router'
import { chunkAdd, groupOptions } from '@/helper/diagrams'
import BarDiagramm from '@/plotly/PlotlyDiagram.vue'
import { FileUpload, type FileUploadSelectEvent } from 'primevue'
import { checkUploadFile } from '@/helper/upload'
import { useToast } from 'primevue/usetoast'
import {
  useDeleteBuySellPrice,
  useGetBuySellPrice,
  useUploadBuySellPrice,
} from '@/backend/buysellprice'

const route = useRoute()
const toast = useToast()

const props = defineProps<{
  site: Site
  commodity: Commodity
}>()
const profileUpload = ref<InstanceType<typeof FileUpload>>()
const checkingUpload = ref(false)

const groupOption = ref(groupOptions[0])

const { data: steps, isPending: pending } = useGetBuySellPrice(
  route,
  props.site,
  props.commodity,
)
const { mutate: uploadBuy } = useUploadBuySellPrice(
  route,
  props.site,
  props.commodity,
  BuySellPriceType.buy,
)
const { mutate: uploadSell } = useUploadBuySellPrice(
  route,
  props.site,
  props.commodity,
  BuySellPriceType.sell,
)
const { mutate: deleteBuySellPrice } = useDeleteBuySellPrice(
  route,
  props.site,
  props.commodity,
)

const dataBuy: Ref<Partial<Plotly.Data>[]> = computed(() => {
  if (!steps.value || !steps.value.buy) return []
  return [
    {
      name: props.commodity.name,
      y: chunkAdd(steps.value.buy, groupOption.value.groupSize, 1),
      x: Array.from({ length: groupOption.value.groups }, (_, i) => i + 1),
      type: 'bar',
    },
  ]
})
const dataSell: Ref<Partial<Plotly.Data>[]> = computed(() => {
  if (!steps.value || !steps.value.sell) return []
  return [
    {
      name: props.commodity.name,
      y: chunkAdd(steps.value.sell, groupOption.value.groupSize, 1),
      x: Array.from({ length: groupOption.value.groups }, (_, i) => i + 1),
      type: 'bar',
    },
  ]
})

async function upload(event: FileUploadSelectEvent, buy: boolean) {
  checkingUpload.value = true
  const file = event.files[0]

  checkUploadFile(toast, file)
    .then(res => {
      if (buy) uploadBuy(res)
      else uploadSell(res)
    })
    .catch(() => {})
    .finally(() => {
      // @ts-expect-error Wrong type description
      if (profileUpload.value) profileUpload.value.clear()
      checkingUpload.value = false
    })
}

function del() {
  deleteBuySellPrice(undefined, {
    onSuccess() {
      toast.add({
        summary: 'Success',
        detail: `BuySellPrice for ${props.commodity.name} was deleted`,
        severity: 'success',
        life: 2000,
      })
    },
  })
}
</script>

<style scoped></style>
