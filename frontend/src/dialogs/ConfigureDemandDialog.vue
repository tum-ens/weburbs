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
          option-label="name"
        />
        <Button label="Add" @click="addDefault" :disabled="!newDefault" />
      </div>
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
import { computed, ref, watch } from 'vue'
import type { Commodity, DemandConfig, Site } from '@/backend/interfaces'
import { useRoute } from 'vue-router'

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
    if (!exDemands.value) {
      demands.value = []
      return
    }
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

function addDefault() {
  demands.value.push({
    quantity: 1,
    ...newDefault.value,
  })
  newDefault.value = undefined
}

function remove(demand: DemandConfig) {
  demands.value = demands.value.filter(d => d.name != demand.name)
}

function save() {
  updateDemands(demands.value)
}
</script>

<style scoped></style>
