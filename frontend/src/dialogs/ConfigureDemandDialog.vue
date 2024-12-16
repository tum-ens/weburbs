<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    header="Configure Demand"
    modal
  >
    <div class="flex flex-col min-w-96">
      <span v-if="demands.length === 0">
        Add some consumer...
      </span>
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
                <span class="pi pi-plus"/>
              </template>
              <template #decrementicon>
                <span class="pi pi-minus"/>
              </template>
            </InputNumber>
            <Button class="col-span-1 w-full" icon="pi pi-trash" severity="danger" @click="() => remove(demand)" fluid/>
          </div>
        </template>
      </div>
      <divider/>
      <div class="grid grid-cols-2 gap-3 items-center">
        <Select v-model="newDefault" :options="availDefDemands" option-label="name"/>
        <Button label="Add" @click="addDefault" :disabled="!newDefault"/>
      </div>
      <divider/>
      <div class="grid grid-cols-2 gap-3 items-center">
        <Button class="col-start-2" label="Save" @click="save"/>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import {useGetDefDemand} from "@/backend/demand";
import {computed, ref} from "vue";
import type {DemandConfig} from "@/backend/interfaces";

const visible = defineModel<boolean>('visible', {default: false})

const {data: defDemands} = useGetDefDemand()
const availDefDemands = computed(() => {
  if (!defDemands.value)
    return []
  return defDemands.value
    .filter(defDemand => !demands.value.some(demand => demand.name === defDemand.name))
})

const demands = ref<DemandConfig[]>([])

const newDefault = ref()

function addDefault() {
  demands.value.push({
    quantity: 1,
    ...newDefault.value
  })
  newDefault.value = undefined
}

function remove(demand: DemandConfig) {
  demands.value =
    demands.value.filter(d => d.name != demand.name)
}
</script>

<style scoped></style>
