<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    header="Configure Demand"
    modal
  >
    <div class="flex flex-col">
      <template v-for="defDemand in defDemands" :key="defDemand.name">
        <divider />
        <div class="grid grid-cols-3 gap-3 items-center">
          <span class="col-span-2">{{ defDemand.name }}</span>
          <InputNumber
            v-model="defDemand.quantity"
            inputId="horizontal-buttons"
            showButtons
            buttonLayout="horizontal"
            :step="1"
            input-class="text-center"
            :max-fraction-digits="0"
            fluid
            class="w-40"
            :allow-empty="false"
            :min="0"
          >
            <template #incrementicon>
              <span class="pi pi-plus" />
            </template>
            <template #decrementicon>
              <span class="pi pi-minus" />
            </template>
          </InputNumber>
        </div>
      </template>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const visible = defineModel<boolean>('visible', { default: false })

const defDemands = reactive([
  {
    name: 'Poor household',
    quantity: 0,
  },
  {
    name: 'Medium household',
    quantity: 0,
  },
  {
    name: 'Rich household',
    quantity: 0,
  },
  {
    name: 'School',
    quantity: 0,
  },
  {
    name: 'Public facility',
    quantity: 0,
  },
])
</script>

<style scoped></style>
