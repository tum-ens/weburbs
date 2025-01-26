<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    header="Configure Demand"
    modal
  >
    <div class="flex flex-col min-w-96">
      <span v-if="demands.length === 0"> Add some consumer... </span>
      <div class="flex flex-col gap-3">
        <template v-for="demand in demands" :key="demand.name">
          <div class="grid grid-cols-12 gap-3 items-center">
            <span class="col-span-6">{{ demand.name }}</span>
            <InputNumber
              v-model="demand.quantity"
              inputId="horizontal-buttons"
              showButtons
              buttonLayout="horizontal"
              :step="1"
              input-class="text-center"
              :max-fraction-digits="0"
              fluid
              class="col-span-5"
              :allow-empty="false"
              :min="1"
            >
              <template #incrementicon>
                <span class="pi pi-plus" />
              </template>
              <template #decrementicon>
                <span class="pi pi-minus" />
              </template>
            </InputNumber>
            <Button
              class="col-span-1 w-full"
              icon="pi pi-trash"
              severity="danger"
              @click="() => remove(demand)"
              fluid
            />
          </div>
        </template>
      </div>
      <divider />
      <div class="grid grid-cols-2 gap-3 items-center">
        <Select
          v-model="newDefault"
          :options="availDefDemands"
          filter
          option-label="name"
        />
        <Button label="Add" @click="addDefault" :disabled="!newDefault" />
      </div>
      <template v-if="advanced">
        <divider />
        <div class="grid grid-cols-3 gap-3 items-center">
          <FileUpload
            :disabled="checkingUpload"
            ref="profileUpload"
            mode="basic"
            custom-upload
            choose-icon="pi pi-upload"
            choose-label="Upload"
            @select="onFileSelect"
            pt:root:class="justify-start"
          />
          <FloatLabel variant="on">
            <InputText
              id="uploadName"
              :disabled="!uploadSteps"
              v-model="uploadName"
            />
            <label for="uploadName">Name of Demand</label>
          </FloatLabel>
          <Button
            :disabled="!uploadSteps || !uploadName"
            :loading="checkingUpload"
            label="Add"
            @click="uploadProfile"
          />
        </div>
      </template>
      <divider />
      <div class="grid grid-cols-2 gap-3 items-center">
        <Button class="col-start-2" label="Save" @click="save" />
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import {
  useGetDefDemand,
  useGetDemand,
  useUpdateDemand,
} from '@/backend/demand'
import { computed, inject, ref, watch } from 'vue'
import type { Commodity, DemandConfig, Site } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import { FileUpload, type FileUploadSelectEvent } from 'primevue'
import { useToast } from 'primevue/usetoast'
import { checkUploadFile } from '@/helper/upload'

const advanced = inject('advanced')

const toast = useToast()
const route = useRoute()

const props = defineProps<{
  site: Site
  commodity: Commodity
}>()

const visible = defineModel<boolean>('visible', { default: false })

const { mutate: updateDemands } = useUpdateDemand(
  route,
  props.site,
  props.commodity,
)
const { data: defDemands } = useGetDefDemand()
const { data: exDemands } = useGetDemand(route, props.site, props.commodity)

const demands = ref<DemandConfig[]>([])
const newDefault = ref()

const availDefDemands = computed(() => {
  if (!defDemands.value) return []
  return defDemands.value.filter(
    defDemand => !demands.value.some(demand => demand.name === defDemand.name),
  )
})

watch(
  exDemands,
  () => {
    demands.value = []
    if (!exDemands.value) return
    demands.value = exDemands.value.map(dem => {
      return {
        name: dem.name,
        description: dem.description,
        quantity: dem.quantity,
      }
    })
  },
  { immediate: true },
)

function nameAlreadyExists(name: string) {
  if (demands.value.some(demand => demand.name === name)) {
    toast.add({
      summary: 'Conflict',
      detail: `A profile with this name already exists`,
      severity: 'error',
      life: 2000,
    })
    return true
  }
  return false
}

function addDefault() {
  if (nameAlreadyExists(newDefault.value.name)) return

  demands.value.push({
    quantity: 1,
    default: true,
    ...newDefault.value,
  })
  newDefault.value = undefined
}

function uploadProfile() {
  if (!uploadSteps.value) return
  if (nameAlreadyExists(uploadName.value)) return

  demands.value.push({
    quantity: 1,
    steps: uploadSteps.value,
    name: uploadName.value,
    description: '',
  })
  uploadSteps.value = null
  uploadName.value = ''
  // @ts-expect-error Wrong type description
  if (profileUpload.value) profileUpload.value.clear()
}

function remove(demand: DemandConfig) {
  demands.value = demands.value.filter(d => d.name != demand.name)
}

function save() {
  updateDemands(demands.value)
  visible.value = false
}

const profileUpload = ref<InstanceType<typeof FileUpload>>()
const uploadSteps = ref<number[] | null>(null)
const uploadName = ref('')
const checkingUpload = ref(false)

function onFileSelect(event: FileUploadSelectEvent) {
  checkingUpload.value = true
  const file = event.files[0]
  const reader = new FileReader()

  reader.onload = async e => {
    if (e.target) {
      if (checkUploadFile(toast, e.target.result)) {
        uploadSteps.value = JSON.parse(<string>e.target.result)
        uploadName.value = file.name.split('.').slice(0, -1).join('.')
      } else {
        uploadSteps.value = null
        uploadName.value = ''
        // @ts-expect-error Wrong type description
        if (profileUpload.value) profileUpload.value.clear()
      }
    } else {
      toast.add({
        summary: 'Upload error',
        detail: `Something went wrong when reading file ${file.name}`,
        severity: 'error',
        life: 2000,
      })
    }
    checkingUpload.value = false
  }
  reader.readAsText(file)
}
</script>

<style scoped></style>
