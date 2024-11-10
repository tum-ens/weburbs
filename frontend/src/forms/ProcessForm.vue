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
    <FloatLabel variant="on">
      <Textarea fluid id="description" v-model="description" />
      <label for="description">Description</label>
    </FloatLabel>
    <div class="grid grid-cols-3 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('instcap')"
          v-tooltip.bottom="'Existing power throughput capacity per process'"
          id="instcap"
          fluid
          v-model="instcap"
        />
        <label for="instcap">Installed capacity (MW)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('caplo')"
          v-tooltip.bottom="
            'Minimum required power throughput capacity that is allowed per process. Must be smaller or equal to \'cap-up\', but can be bigger than \'inst-cap\' to force investment.'
          "
          id="caplo"
          fluid
          v-model="caplo"
        />
        <label for="caplo">Minimum capacity (MW)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('capup')"
          v-tooltip.bottom="
            'Maximum allowed power throughput capacity per process. Must be bigger than or equal to max(\'cap-lo\', \'inst-cap\').'
          "
          id="capup"
          fluid
          v-model="capup"
        />
        <label for="capup">Maximum capacity (MW)</label>
      </FloatLabel>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('maxgrad')"
          v-tooltip.bottom="
            'Maximum allowed power gradient relative to power throughput capacity. Set value to negative or greater than 1/dt to disable it. '
          "
          id="maxgrad"
          fluid
          v-model="maxgrad"
        />
        <label for="maxgrad">Maximal power gradient (1/h)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('minfraction')"
          v-tooltip.bottom="
            'This value sets the minimum possible fraction of the process capacity which the process can run at. Must be greater equal 0.'
          "
          id="minfraction"
          fluid
          v-model="minfraction"
        />
        <label for="minfraction">Minimum load fraction</label>
      </FloatLabel>
    </div>
    <div class="grid grid-cols-3 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('invcost')"
          v-tooltip.bottom="
            'Total investement cost for adding capacity. Is annualized in the model using the annuity factor derived from \'wacc\' and \'depreciation\'.'
          "
          id="invcost"
          fluid
          v-model="invcost"
        />
        <label for="invcost">Investment cost (€/MW)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('fixcost')"
          v-tooltip.bottom="
            'Operation independent costs for existing and new capacities per MW throughput power.'
          "
          id="fixcost"
          fluid
          v-model="fixcost"
        />
        <label for="fixcost">Annual fix cost (€/MW/a)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('varcost')"
          v-tooltip.bottom="
            'Variable costs per throughput energy unit (MWh) produced. This includes wear and tear of moving parts, operation liquids, but excluding fuel costs, as they are included in table Commodity, column \'price\'.'
          "
          id="varcost"
          fluid
          v-model="varcost"
        />
        <label for="varcost">Variable costs (€/MWh)</label>
      </FloatLabel>
    </div>
    <div class="grid grid-cols-3 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('wacc')"
          suffix="%"
          v-tooltip.bottom="
            'Percentage (%) of costs for capital after taxes. Used to calculate annuity factor for investment costs.'
          "
          id="wacc"
          fluid
          v-model="wacc"
        />
        <label for="wacc">Weighted average cost of capital</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('deprecation')"
          v-tooltip.bottom="
            'Economic lifetime (more conservative than technical lifetime) of a process investment in years (a). Used to calculate annuity factor for investment costs.'
          "
          id="deprecation"
          fluid
          v-model="deprecation"
        />
        <label for="deprecation">Depreciation period (a)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('areapercap')"
          v-tooltip.bottom="
            'If a process requires area set value here. If no area use is to be considered leave empty.'
          "
          id="areapercap"
          fluid
          v-model="areapercap"
        />
        <label for="areapercap">Area use per capacity (m^2/MW)</label>
      </FloatLabel>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <FloatLabel variant="on">
        <MultiSelect
          optionLabel="name"
          v-model="inComs"
          display="chip"
          :options="coms"
          filter
          fluid
          id="inComs"
        />
        <label for="inComs">Incoming commodities</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <MultiSelect
          optionLabel="disp_name"
          v-model="outComs"
          display="chip"
          :options="coms"
          filter
          fluid
          id="outComs"
        />
        <label for="outComs">Outgoing commodities</label>
      </FloatLabel>
    </div>
    <Message
      v-if="inComs.some(com => com.default) || outComs.some(com => com.default)"
      severity="warn"
      >Default commodities will be added automatically
    </Message>
    <Button :loading="loading" @click="submit">
      {{ submitLabel }}
    </Button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import type { Commodity, Process } from '@/backend/interfaces'
import {
  useDefCommodities,
  useProjectSiteCommodities,
} from '@/backend/commodities'
import { useRoute } from 'vue-router'

const toast = useToast()
const route = useRoute()

const props = defineProps<{
  submitLabel: string
  process?: Process
  loading: boolean
  site_name: string
}>()
const emit = defineEmits<{
  submit: [process: Process]
}>()

const { data: commodities } = useProjectSiteCommodities(route, props.site_name)
const { data: def_commodities } = useDefCommodities()

const coms = computed(() => {
  if (!commodities.value) return []
  if (!def_commodities.value) return commodities.value

  return [
    ...commodities.value.map(com => {
      return {
        ...com,
        disp_name: com.name,
        default: false,
      }
    }),
    ...def_commodities.value
      .filter(
        def_com => !commodities.value.some(com => def_com.name == com.name),
      )
      .map(def_com => {
        return {
          ...def_com,
          disp_name: def_com.name + ' (Default)',
          default: true,
        }
      }),
  ]
})

function defaultValue<T>(val: T | null | undefined, def: T) {
  if (val == null) return def
  return val
}

const name = ref(defaultValue(props.process?.name, ''))
const description = ref(defaultValue(props.process?.description, ''))

const instcap = ref(defaultValue(props.process?.instcap, undefined))
const caplo = ref(defaultValue(props.process?.caplo, undefined))
const capup = ref(defaultValue(props.process?.capup, undefined))

const maxgrad = ref(defaultValue(props.process?.maxgrad, undefined))
const minfraction = ref(defaultValue(props.process?.minfraction, undefined))

const invcost = ref(defaultValue(props.process?.invcost, undefined))
const fixcost = ref(defaultValue(props.process?.fixcost, undefined))
const varcost = ref(defaultValue(props.process?.varcost, undefined))

const wacc = ref(defaultValue(props.process?.wacc, undefined))
const deprecation = ref(defaultValue(props.process?.deprecation, undefined))
const areapercap = ref(defaultValue(props.process?.areapercap, undefined))

interface TaggedCommodity extends Commodity {
  disp_name: string
  default: boolean
}

const inComs = ref<TaggedCommodity[]>([])
const outComs = ref<TaggedCommodity[]>([])
watch(
  coms,
  () => {
    inComs.value = coms.value
      .filter(com => props.process?.in.includes(com.name))
      .map(com => {
        return {
          ...com,
          disp_name: com.name,
          default: false,
        }
      })
    outComs.value = coms.value
      .filter(com => props.process?.out.includes(com.name))
      .map(com => {
        return {
          ...com,
          disp_name: com.name,
          default: false,
        }
      })
  },
  { immediate: true },
)

const invalids = ref<string[]>([])

function check() {
  invalids.value = []
  if (!name.value) invalids.value.push('name')

  if (instcap.value === undefined || instcap.value < 0)
    invalids.value.push('instcap')
  if (caplo.value === undefined || caplo.value < 0) invalids.value.push('caplo')
  if (capup.value === undefined) invalids.value.push('capup')
  if (
    caplo.value !== undefined &&
    capup.value !== undefined &&
    capup.value >= 0 &&
    caplo.value > capup.value
  ) {
    invalids.value.push('caplo')
    invalids.value.push('capup')
  }

  if (maxgrad.value === undefined) invalids.value.push('maxgrad')
  if (minfraction.value === undefined || minfraction.value < 0)
    invalids.value.push('minfraction')

  if (invcost.value === undefined || invcost.value < 0)
    invalids.value.push('invcost')
  if (fixcost.value === undefined || fixcost.value < 0)
    invalids.value.push('fixcost')
  if (varcost.value === undefined || varcost.value < 0)
    invalids.value.push('varcost')

  if (wacc.value === undefined || wacc.value < 0 || wacc.value > 1)
    invalids.value.push('wacc')
  if (deprecation.value === undefined || deprecation.value < 0)
    invalids.value.push('deprecation')
  if (areapercap.value !== undefined && areapercap.value < 0)
    invalids.value.push('areapercap')

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
    name: name.value,
    description: description.value,
    instcap: instcap.value || 0,
    caplo: caplo.value || 0,
    capup: capup.value || 0,
    maxgrad: maxgrad.value || 0,
    minfraction: minfraction.value || 0,
    invcost: invcost.value || 0,
    fixcost: fixcost.value || 0,
    varcost: varcost.value || 0,
    wacc: wacc.value || 0,
    deprecation: deprecation.value || 0,
    areapercap: areapercap.value,
    in: inComs.value.map(inCom => inCom.name),
    out: outComs.value.map(outCom => outCom.name),
  })
}
</script>

<style scoped></style>
