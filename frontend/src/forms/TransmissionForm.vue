<template>
  <div class="mt-2 flex flex-col gap-3">
    Transmission Form
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
import { type Transmission, TransmissionType } from '@/backend/interfaces'
import { useProjectSiteCommodities } from '@/backend/commodities'
import { useSites } from '@/backend/sites'

const toast = useToast()
const route = useRoute()

const props = defineProps<{
  submitLabel: string
  transmission?: Transmission
  loading: boolean
  delete?: boolean
}>()
const emit = defineEmits<{
  submit: [transmission: Transmission]
  onDelete: []
}>()

const sitein = ref<string | undefined>(
  defaultValue(props.transmission?.sitein, undefined),
)
const siteout = ref<string | undefined>(
  defaultValue(props.transmission?.siteout, undefined),
)
const commodity = ref<ComTag | undefined>(
  props.transmission?.commodity
    ? {
        name: props.transmission?.commodity,
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

const { data: sites } = useSites(route)
const { data: com_in } = useProjectSiteCommodities(route, sitein.value)
const { data: com_out } = useProjectSiteCommodities(route, sitein.value)
const commodities = computed<ComTag[]>(() => {
  if (!com_in.value || !com_out.value) return []

  return com_in.value.filter(cin =>
    com_out.value?.some(cout => cin.name === cout.name),
  )
})

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
const unitC = computed(() => commodity.value?.unitC || 'kWh')

const type = ref(defaultValue(props.transmission?.type, TransmissionType.hvac))

const eff = ref(defaultValue(props.transmission?.eff, undefined))

const invcost = ref(defaultValue(props.transmission?.invcost, undefined))
const fixcost = ref(defaultValue(props.transmission?.fixcost, undefined))
const varcost = ref(defaultValue(props.transmission?.varcost, undefined))

const instcap = ref(defaultValue(props.transmission?.instcap, undefined))
const caplo = ref(defaultValue(props.transmission?.caplo, undefined))
const capup = ref(defaultValue(props.transmission?.capup, undefined))

const wacc = ref(defaultValue(props.transmission?.wacc, undefined))
const depreciation = ref(
  defaultValue(props.transmission?.depreciation, undefined),
)
const reactance = ref(defaultValue(props.transmission?.reactance, undefined))
const difflimit = ref(defaultValue(props.transmission?.difflimit, undefined))
const basevoltage = ref(
  defaultValue(props.transmission?.basevoltage, undefined),
)

enum Errors {
  sitein,
  siteout,
  commodity,
  type,
  eff,
  invcost,
  fixcost,
  varcost,
  instcap,
  caplo,
  capup,
  wacc,
  depreciation,
  reactance,
  difflimit,
  basevoltage,
}

const invalids = ref<Errors[]>([])

function check() {
  invalids.value = []
  if (!sitein.value) invalids.value.push(Errors.sitein)
  if (!siteout.value) invalids.value.push(Errors.siteout)
  if (!commodity.value) invalids.value.push(Errors.commodity)

  if (!type.value) invalids.value.push(Errors.type)

  if (eff.value === undefined || eff.value < 0 || eff.value > 1)
    invalids.value.push(Errors.eff)

  if (invcost.value === undefined || invcost.value < 0)
    invalids.value.push(Errors.invcost)
  if (fixcost.value === undefined || fixcost.value < 0)
    invalids.value.push(Errors.fixcost)
  if (varcost.value === undefined || varcost.value < 0)
    invalids.value.push(Errors.varcost)

  if (instcap.value === undefined || instcap.value < 0)
    invalids.value.push(Errors.instcap)
  if (caplo.value === undefined || caplo.value < 0)
    invalids.value.push(Errors.caplo)
  if (capup.value === undefined || capup.value < 0)
    invalids.value.push(Errors.capup)
  if (
    capup.value !== undefined &&
    caplo.value !== undefined &&
    capup.value < caplo.value
  )
    invalids.value.push(Errors.capup, Errors.caplo)

  if (wacc.value === undefined || wacc.value < 0)
    invalids.value.push(Errors.wacc)
  if (depreciation.value === undefined || depreciation.value < 0)
    invalids.value.push(Errors.depreciation)

  if (reactance.value === undefined || reactance.value < 0)
    invalids.value.push(Errors.reactance)
  if (
    difflimit.value === undefined ||
    difflimit.value < -90 ||
    difflimit.value > 90
  )
    invalids.value.push(Errors.difflimit)
  if (basevoltage.value === undefined || basevoltage.value < 0)
    invalids.value.push(Errors.basevoltage)

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
    sitein: sitein.value || '',
    siteout: siteout.value || '',
    commodity: commodity.value.name,
    type: type.value,
    eff: eff.value || 0,
    invcost: invcost.value || 0,
    fixcost: fixcost.value || 0,
    varcost: varcost.value || 0,
    instcap: instcap.value || 0,
    caplo: caplo.value || 0,
    capup: capup.value || 0,
    wacc: wacc.value || 0,
    depreciation: depreciation.value || 0,
    reactance: reactance.value === undefined ? null : reactance.value,
    difflimit: difflimit.value === undefined ? null : difflimit.value,
    basevoltage: basevoltage.value === undefined ? null : basevoltage.value,
  })
}

function deleteStorage() {
  emit('onDelete')
}
</script>

<style scoped></style>
