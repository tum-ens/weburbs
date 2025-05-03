<template>
  <div class="mt-2 flex flex-col gap-3">
    <div class="grid grid-cols-2 gap-3">
      <FloatLabel variant="on">
        <Select
          v-model="sitein"
          :invalid="invalids.includes(Errors.sitein)"
          display="chip"
          :options="site_names"
          fluid
          id="sitein"
        />
        <label for="sitein">From</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <Select
          v-model="siteout"
          :invalid="invalids.includes(Errors.siteout)"
          display="chip"
          :options="site_names"
          fluid
          id="siteout"
        />
        <label for="siteout">To</label>
      </FloatLabel>
    </div>
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
      <label for="commodity">Type</label>
    </FloatLabel>

    <div class="grid grid-cols-2 gap-3">
      <FloatLabel variant="on">
        <Select
          optionLabel="name"
          option-value="val"
          data-key="val"
          v-model="type"
          display="chip"
          :options="
            Object.keys(TransmissionType)
              .filter(key => isNaN(Number(key)))
              .map(name => ({
                name,
                val: TransmissionType[name as keyof typeof TransmissionType],
              }))
          "
          fluid
          id="type"
        />
        <label for="type">Type</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.eff)"
          :max-fraction-digits="2"
          id="eff"
          fluid
          v-model="eff"
          v-tooltip.bottom="
            'Energy efficiency (E_out/E_in) of transmission process.'
          "
        />
        <label for="eff">Efficiency</label>
      </FloatLabel>
    </div>

    <div class="grid grid-cols-3 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.invcost)"
          :max-fraction-digits="2"
          id="invcost"
          fluid
          v-model="invcost"
          v-tooltip.bottom="
            'Total investement cost for adding transmission capacity. Is annualized in the model using the annuity factor derived from columns \'wacc\' and \'depreciation\'.'
          "
        />
        <label for="invcost">Investment cost (€/{{ unitR }})</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.fixcost)"
          :max-fraction-digits="2"
          id="fixcost"
          fluid
          v-model="fixcost"
          v-tooltip.bottom="
            `Operation independent costs for existing and new capacities per ${unitR} throughput power.`
          "
        />
        <label for="fixcost">Annual fixed cost (€/{{ unitR }}/a)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.fixcost)"
          :max-fraction-digits="2"
          id="fixcost"
          fluid
          v-model="varcost"
          v-tooltip.bottom="
            `Variable costs per throughput energy unit (${unitC}) transmitted.`
          "
        />
        <label for="varcost">Variable costs (€/{{ unitC }})</label>
      </FloatLabel>
    </div>

    <div class="grid grid-cols-3 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.instcap)"
          :max-fraction-digits="2"
          id="instcap"
          fluid
          v-model="instcap"
          v-tooltip.bottom="
            'Existing transmission capacity (by throughput power)'
          "
        />
        <label for="instcap">Installed capacity ({{ unitR }})</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.caplo)"
          :max-fraction-digits="2"
          id="caplo"
          fluid
          v-model="caplo"
          v-tooltip.bottom="
            `Minimum required power throughput capacity that is allowed per transmission process. Must be smaller or equal to 'cap-up', but can be bigger than 'inst-cap' to force investment.`
          "
        />
        <label for="caplo">Minimum capacity ({{ unitR }})</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.capup)"
          :max-fraction-digits="2"
          id="capup"
          fluid
          v-model="capup"
          v-tooltip.bottom="
            `Maximum allowed power throughput capacity per process. Must be bigger than or equal to max('cap-lo', 'inst-cap'). Negative for infinity.`
          "
        />
        <label for="capup">Maximum capacity ({{ unitR }})</label>
      </FloatLabel>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.wacc)"
          :max-fraction-digits="2"
          id="wacc"
          fluid
          v-model="wacc"
          v-tooltip.bottom="
            `Percentage (%) of costs for capital after taxes. Used to calculate annuity factor for investment costs.`
          "
        />
        <label for="wacc">Weighted average cost of capital</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.depreciation)"
          :max-fraction-digits="2"
          id="depreciation"
          fluid
          v-model="depreciation"
          v-tooltip.bottom="
            `Economic lifetime (more conservative than technical lifetime) of a transmission process investment in years (a). Used to calculate annuity factor for investment costs.`
          "
        />
        <label for="depreciation">Depreciation periods (a)</label>
      </FloatLabel>
    </div>

    <div class="grid grid-cols-3 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.reactance)"
          :max-fraction-digits="2"
          id="reactance"
          fluid
          v-model="reactance"
          v-tooltip.bottom="
            `Reactance of transmission line. Used to calculate Voltage Angle of site`
          "
        />
        <label for="reactance">Reactance X (Ω)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.difflimit)"
          :max-fraction-digits="2"
          id="difflimit"
          fluid
          v-model="difflimit"
          v-tooltip.bottom="
            `Angle difference limit restricts the difference between angles of source and destination sites`
          "
        />
        <label for="difflimit">Angle difference limit deg (°)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.basevoltage)"
          :max-fraction-digits="2"
          id="basevoltage"
          fluid
          v-model="basevoltage"
          v-tooltip.bottom="
            `Base voltage of transmission line is required for Per Unit System conversion of Voltage Angle`
          "
        />
        <label for="basevoltage">Base Voltage (kV)</label>
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
const site_names = computed(() => sites.value?.map(s => s.name) || [])
const { data: com_in } = useProjectSiteCommodities(route, sitein)
const { data: com_out } = useProjectSiteCommodities(route, siteout)
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
  if (capup.value === undefined) invalids.value.push(Errors.capup)
  if (
    capup.value !== undefined &&
    caplo.value !== undefined &&
    capup.value >= 0 &&
    capup.value < caplo.value
  )
    invalids.value.push(Errors.capup, Errors.caplo)

  if (wacc.value === undefined || wacc.value < 0)
    invalids.value.push(Errors.wacc)
  if (depreciation.value === undefined || depreciation.value < 0)
    invalids.value.push(Errors.depreciation)

  if (reactance.value !== undefined && reactance.value < 0)
    invalids.value.push(Errors.reactance)
  if (
    difflimit.value !== undefined &&
    (difflimit.value < -90 || difflimit.value > 90)
  )
    invalids.value.push(Errors.difflimit)
  if (basevoltage.value !== undefined && basevoltage.value < 0)
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
