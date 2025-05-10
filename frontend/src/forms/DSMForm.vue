<template>
  <div class="mt-2 flex flex-col gap-3">
    <FloatLabel variant="on">
      <Select
        optionLabel="name"
        :invalid="invalids.includes(Errors.commodity)"
        dataKey="name"
        v-model="commodity"
        display="chip"
        :options="commodities"
        fluid
        id="commodity"
      />
      <label for="commodity">Commodity</label>
    </FloatLabel>

    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.delay)"
          :max-fraction-digits="0"
          id="delay"
          fluid
          v-model="delay"
          v-tooltip.bottom="
            'How long may the load be shifted in upward or downward direction.'
          "
        />
        <label for="delay">Delay time (h)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.eff)"
          :max-fraction-digits="5"
          id="eff"
          fluid
          v-model="eff"
          v-tooltip.bottom="'Efficiency of DSM process. Range between 0 and 1.'"
        />
        <label for="eff">Efficiency</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.recov)"
          :max-fraction-digits="0"
          id="recov"
          fluid
          v-model="recov"
          v-tooltip.bottom="'Duration until next shift may take place.'"
        />
        <label for="recov">Recovery time (h)</label>
      </FloatLabel>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.capmaxdo)"
          :max-fraction-digits="2"
          id="capmaxdo"
          fluid
          v-model="capmaxdo"
          v-tooltip.bottom="'Maximum amount of downshift energy in one hour.'"
        />
        <label for="capmaxdo">Downshift capacity ({{ unitR }})</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.capmaxup)"
          :max-fraction-digits="2"
          id="capmaxup"
          fluid
          v-model="capmaxup"
          v-tooltip.bottom="'Maximum amount of upshift energy in one hour.'"
        />
        <label for="capmaxup">Upshift Capacity ({{ unitR }})</label>
      </FloatLabel>
    </div>

    <div class="flex flex-row gap-3">
      <Button
        v-if="props.delete"
        fluid
        :loading="loading"
        label="Delete"
        @click="deleteStorage"
        severity="danger"
      />
      <Button fluid :loading="loading" :label="submitLabel" @click="submit" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useRoute } from 'vue-router'
import { type DSM } from '@/backend/interfaces'
import { useProjectSiteCommodities } from '@/backend/commodities'

const toast = useToast()
const route = useRoute()

const props = defineProps<{
  submitLabel: string
  site_name: string
  dsm?: DSM
  loading: boolean
  delete?: boolean
}>()
const emit = defineEmits<{
  submit: [dsm: DSM]
  onDelete: []
}>()

const commodity = ref<ComTag | undefined>(
  props.dsm?.commodity
    ? {
        name: props.dsm?.commodity,
        unitR: 'kW',
        unitC: 'kWh',
      }
    : undefined,
)

interface ComTag {
  name: string
  unitR: string
  unitC: string
}

const { data: commodities } = useProjectSiteCommodities(route, props.site_name)

function defaultValue<T>(val: T | null | undefined, def: T) {
  if (val == null) return def
  return val
}

watch(
  commodities,
  () => {
    if (!commodities.value) return

    commodities.value.forEach(com => {
      if (com.name !== commodity.value?.name) return

      commodity.value.unitR = com.unitR
      commodity.value.unitC = com.unitC
    })
  },
  { immediate: true },
)
const unitR = computed(() => commodity.value?.unitR || 'kW')

const delay = ref(defaultValue(props.dsm?.delay, undefined))
const eff = ref(defaultValue(props.dsm?.eff, undefined))
const recov = ref(defaultValue(props.dsm?.recov, undefined))

const capmaxdo = ref(defaultValue(props.dsm?.capmaxdo, undefined))
const capmaxup = ref(defaultValue(props.dsm?.capmaxup, undefined))

enum Errors {
  commodity,
  delay,
  eff,
  recov,
  capmaxdo,
  capmaxup,
}

const invalids = ref<Errors[]>([])

function check() {
  invalids.value = []
  if (!commodity.value) invalids.value.push(Errors.commodity)

  if (delay.value === undefined || delay.value < 0)
    invalids.value.push(Errors.delay)
  if (eff.value === undefined || eff.value < 0 || eff.value > 1)
    invalids.value.push(Errors.eff)
  if (recov.value === undefined || recov.value < 0)
    invalids.value.push(Errors.recov)

  if (capmaxdo.value === undefined || capmaxdo.value < 0)
    invalids.value.push(Errors.capmaxdo)
  if (capmaxup.value === undefined || capmaxup.value < 0)
    invalids.value.push(Errors.capmaxup)

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
  if (!commodity.value) return

  emit('submit', {
    commodity: commodity.value.name,
    delay: delay.value || 0,
    eff: eff.value || 0,
    recov: recov.value || 0,
    capmaxdo: capmaxdo.value || 0,
    capmaxup: capmaxup.value || 0,
  })
}

function deleteStorage() {
  emit('onDelete')
}
</script>

<style scoped></style>
