<template>
  <div class="mt-2 flex flex-col gap-3">
    <FloatLabel variant="on">
      <InputText
        :invalid="invalids.includes('name')"
        fluid
        id="name"
        v-model="name"
      />
      <label for="name">Name</label>
    </FloatLabel>
    <div class="grid grid-cols-2 gap-3">
      <FloatLabel variant="on">
        <Select
          v-model="type"
          display="chip"
          :invalid="invalids.includes('type')"
          :options="typeOpt"
          optionLabel="name"
          fluid
          id="type"
        />
        <label for="type">Type</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('price')"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'Cost for purchasing one unit (MWh) of a stock or buy commodity. Revenue for selling one unit (MWh) of a sell commodity. Cost for creating one unit of environmental commodity.\n' +
            'Multiplier for sheet \'Buy-Sell-Price\' for commodity types \'Buy\' and \'Sell\'.'
          "
          id="price"
          fluid
          v-model="price"
        />
        <label for="price">Price (€/kWh)</label>
      </FloatLabel>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('max')"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'For stock commodities, this value limits annual use (kWh) of this commodity. For CO2, this value limits the amount of emissions (t_CO2). If simulation timespan does not cover a full year, the sums are multiplied accordingly before (cf. \'weight\' in urbs). ' +
            'Set negative for infinity.'
          "
          id="max"
          fluid
          v-model="max"
        />
        <label for="max">Maximum commodity use</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('maxperhour')"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'For stock commodities, this value limits the energy use per hour (kW). ' +
            'Set negative for infinity.'
          "
          id="maxperhour"
          fluid
          v-model="maxperhour"
        />
        <label for="maxperhour">Maximum commodity use per hour</label>
      </FloatLabel>
    </div>

    <div class="flex flex-row gap-3">
      <Button
        v-if="props.delete"
        fluid
        :loading="loading"
        label="Delete"
        @click="deleteProc"
        severity="danger"
      />
      <Button fluid :loading="loading" :label="submitLabel" @click="submit" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import { type Commodity, CommodityTypes } from '@/backend/interfaces'

const toast = useToast()

const props = defineProps<{
  submitLabel: string
  commodity?: Commodity
  loading: boolean
  site_name: string
  delete?: boolean
}>()
const emit = defineEmits<{
  submit: [commodity: Commodity]
  onDelete: []
}>()

function defaultValue<T>(val: T | null | undefined, def: T) {
  if (val == null) return def
  return val
}

const typeOpt = CommodityTypes.map((t, i) => {
  return {
    name: t,
    value: i + 1,
  }
})

const name = ref(defaultValue(props.commodity?.name, ''))

const type = ref(typeOpt[props.commodity ? props.commodity.type - 1 : 0])
const price = ref(defaultValue(props.commodity?.price, undefined))

const max = ref(defaultValue(props.commodity?.max, undefined))
const maxperhour = ref(defaultValue(props.commodity?.maxperhour, undefined))

const invalids = ref<string[]>([])

function check() {
  invalids.value = []
  if (!name.value) invalids.value.push('name')

  if (type.value === undefined) invalids.value.push('type')
  if (price.value !== undefined && price.value < 0) invalids.value.push('price')

  return invalids.value.length === 0
}

function submit() {
  if (!check()) {
    toast.add({
      summary: 'Error',
      detail: 'Not all fields have been filled properly',
      severity: 'error',
      life: 2000,
    })
    return
  }

  emit('submit', {
    site: props.site_name,
    name: name.value,
    type: type.value.value,
    price: price.value,
    max: max.value,
    maxperhour: maxperhour.value,
  })
}

function deleteProc() {
  emit('onDelete')
}
</script>

<style scoped></style>
