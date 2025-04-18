<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    header="Configure Demand"
    modal
    class="w-11/12 md:w-10/12 xl:w-1/2"
  >
    <div class="flex flex-col">
      <span v-if="demands.length === 0"> Add some consumer... </span>
      <div class="flex flex-col gap-3">
        <template v-for="demand in demands" :key="demand.name">
          <div class="grid grid-cols-12 gap-3 items-center">
            <span class="col-span-12 sm:col-span-6">{{ demand.name }}</span>
            <InputNumber
              v-model="demand.quantity"
              inputId="horizontal-buttons"
              showButtons
              buttonLayout="horizontal"
              :step="1"
              input-class="text-center"
              :max-fraction-digits="0"
              fluid
              class="col-span-10 sm:col-span-5"
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
              class="col-span-2 sm:col-span-1 w-full"
              icon="pi pi-trash"
              severity="danger"
              @click="() => remove(demand)"
              fluid
            />
          </div>
        </template>
      </div>
      <divider />
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 items-center">
        <FloatLabel variant="on">
          <Select
            fluid
            v-model="newDefault"
            :options="availDefDemands"
            filter
            option-label="name"
            id="selDefault"
          />
          <label for="selDefault">Select a default</label>
        </FloatLabel>
        <Button label="Add" @click="addDefault" :disabled="!newDefault" />
      </div>
      <template v-if="advanced">
        <divider />
        <div
          class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 items-center"
        >
          <div class="sm:col-span-2 md:col-span-1">
            <FileUpload
              :disabled="checkingUpload"
              ref="profileUpload"
              mode="basic"
              accept=".json, .xlsx"
              custom-upload
              choose-icon="pi pi-upload"
              choose-label="Upload"
              @select="onFileSelect"
              pt:root:class="justify-start"
            />
          </div>
          <FloatLabel variant="on">
            <InputText
              fluid
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
        <span class="mt-2"
          >You can create a custom demand profile
          <a
            class="link"
            target="_blank"
            href="https://nessi.iwi.uni-hannover.de/en/ramp/start/"
            >here</a
          >.</span
        >
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
  checkUploadFile(toast, file)
    .then(res => {
      uploadSteps.value = res
      uploadName.value = file.name.split('.').slice(0, -1).join('.')
    })
    .catch(() => {
      uploadSteps.value = null
      uploadName.value = ''
      // @ts-expect-error Wrong type description
      if (profileUpload.value) profileUpload.value.clear()
    })
    .finally(() => {
      checkingUpload.value = false
    })
}
</script>

<style scoped>
.link {
  color: blue;
  text-decoration: underline;
}
</style>
