<template>
  <div class="mt-2 flex flex-col gap-3">
    <FloatLabel variant="on">
      <InputText
        :invalid="invalids.includes(Errors.name)"
        :disabled="!advanced"
        fluid
        id="name"
        v-model="name"
      />
      <label for="name">Name</label>
    </FloatLabel>
    <FloatLabel variant="on">
      <Textarea
        fluid
        id="description"
        v-model="description"
        :disabled="!advanced"
      />
      <label for="description">Description</label>
    </FloatLabel>
    <div class="grid grid-cols-3 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.instcapc)"
          :max-fraction-digits="2"
          v-tooltip.bottom="'Existing storage capacity per storage type'"
          id="instcapc"
          fluid
          v-model="instcapc"
        />
        <label for="instcapc">Installed capacity ({{ unitC }})</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.caploc)"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'Minimum required storage capacity. Must be smaller or equal to \'inst-cap-c\'.'
          "
          id="caploc"
          fluid
          v-model="caploc"
        />
        <label for="caploc">Minimum capacity ({{ unitC }})</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.capupc)"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'Maximum allowed storage capacity. Must be bigger or equal to \'inst-cap-c\'. Set negative for infinity.'
          "
          id="capupc"
          fluid
          v-model="capupc"
        />
        <label for="capupc">Maximum capacity ({{ unitC }})</label>
      </FloatLabel>
    </div>
    <div class="grid grid-cols-3 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.invcostc)"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'Total investement cost for adding storage capacity. Is annualized in the model using the annuity factor derived from \'wacc\' and \'depreciation\'.'
          "
          id="invcostc"
          fluid
          v-model="invcostc"
        />
        <label for="invcostc">Investment cost cap. (€/{{ unitC }})</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.fixcostc)"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            `Operation independent costs for existing and new storage capacities per ${unitC}.`
          "
          id="fixcostc"
          fluid
          v-model="fixcostc"
        />
        <label for="fixcostc">Fix cost capacity (€/{{ unitC }}/a)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes(Errors.varcostc)"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            `Operation dependent costs per ${unitC} stored. This value is usually zero, but can be exploited for modelling short-term storage technologies or ones that have increased wear and tear proportional to amount of stored energy.`
          "
          id="varcostc"
          fluid
          v-model="varcostc"
        />
        <label for="varcostc">Variable cost cap. (€/{{ unitC }}))</label>
      </FloatLabel>
    </div>

    <Accordion value="1" v-if="advanced">
      <AccordionPanel pt:root:class="border-0" value="0">
        <AccordionHeader>Advanced</AccordionHeader>
        <AccordionContent pt:root:class="pt-1">
          <div class="mt-2 flex flex-col gap-3">
            <div class="grid grid-cols-3 gap-3">
              <FloatLabel variant="on">
                <InputNumber
                  :invalid="invalids.includes(Errors.instcapp)"
                  :max-fraction-digits="2"
                  v-tooltip.bottom="'Existing storage power per storage type'"
                  id="instcapp"
                  fluid
                  v-model="instcapp"
                />
                <label for="instcapp"
                  >Installed storage power ({{ unitR }})</label
                >
              </FloatLabel>
              <FloatLabel variant="on">
                <InputNumber
                  :invalid="invalids.includes(Errors.caplop)"
                  :max-fraction-digits="2"
                  v-tooltip.bottom="
                    'Minimum required input/output power. Must be smaller or equal to \'inst-cap-p\'.'
                  "
                  id="caplop"
                  fluid
                  v-model="caplop"
                />
                <label for="caplo">Minimum power ({{ unitR }})</label>
              </FloatLabel>
              <FloatLabel variant="on">
                <InputNumber
                  :invalid="invalids.includes(Errors.capupp)"
                  :max-fraction-digits="2"
                  v-tooltip.bottom="
                    'Maximum allowed input/output power. Must be bigger or equal to \'inst-cap-p\'. Set negative for infinity.'
                  "
                  id="capupp"
                  fluid
                  v-model="capupp"
                />
                <label for="capupp">Maximum power ({{ unitR }})</label>
              </FloatLabel>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <FloatLabel variant="on">
                <InputNumber
                  :invalid="invalids.includes(Errors.effin)"
                  :max-fraction-digits="2"
                  v-tooltip.bottom="'Energy efficiency of storing process.'"
                  id="effin"
                  fluid
                  v-model="effin"
                />
                <label for="effin">Efficiency input</label>
              </FloatLabel>
              <FloatLabel variant="on">
                <InputNumber
                  :invalid="invalids.includes(Errors.effout)"
                  :max-fraction-digits="2"
                  v-tooltip.bottom="'Energy efficiency of power output.'"
                  id="effout"
                  fluid
                  v-model="effout"
                />
                <label for="effout">Efficiency output</label>
              </FloatLabel>
            </div>

            <div class="grid grid-cols-3 gap-3">
              <FloatLabel variant="on">
                <InputNumber
                  :invalid="invalids.includes(Errors.invcostp)"
                  :max-fraction-digits="2"
                  v-tooltip.bottom="
                    'Total investement cost for adding power input/output capacity. Is annualized in the model using the annuity factor derived from \'wacc\' and \'depreciation\'.'
                  "
                  id="invcostp"
                  fluid
                  v-model="invcostp"
                />
                <label for="invcostp"
                  >Investment cost power (€/{{ unitR }})</label
                >
              </FloatLabel>
              <FloatLabel variant="on">
                <InputNumber
                  :invalid="invalids.includes(Errors.fixcostp)"
                  :max-fraction-digits="2"
                  v-tooltip.bottom="
                    `Operation independent costs for existing and new capacities per ${unitR} input/output power.`
                  "
                  id="fixcostp"
                  fluid
                  v-model="fixcostp"
                />
                <label for="fixcostp">Annual fix cost (€/{{ unitR }}/a)</label>
              </FloatLabel>
              <FloatLabel variant="on">
                <InputNumber
                  :invalid="invalids.includes(Errors.varcostp)"
                  :max-fraction-digits="2"
                  v-tooltip.bottom="
                    `Operation dependent costs for input or output of energy per ${unitC}_out stored or retrieved.`
                  "
                  id="varcostc"
                  fluid
                  v-model="varcostp"
                />
                <label for="varcostp"
                  >Variable cost in/out (€/{{ unitC }})</label
                >
              </FloatLabel>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <FloatLabel variant="on">
                <InputNumber
                  :invalid="invalids.includes(Errors.wacc)"
                  :max-fraction-digits="2"
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
                  :invalid="invalids.includes(Errors.depreciation)"
                  :max-fraction-digits="2"
                  v-tooltip.bottom="
                    'Economic lifetime (more conservative than technical lifetime) of a storage investment in years (a). Used to calculate annuity factor for investment costs.'
                  "
                  id="depreciation"
                  fluid
                  v-model="depreciation"
                />
                <label for="depreciation">Depreciation period (a)</label>
              </FloatLabel>
            </div>
            <div class="grid grid-cols-3 gap-3">
              <FloatLabel variant="on">
                <InputNumber
                  :invalid="invalids.includes(Errors.init)"
                  :max-fraction-digits="2"
                  v-tooltip.bottom="
                    'Fraction of storage capacity that is full at the simulation start (t0). This level also has to be reached in the final timestep (tN).'
                  "
                  id="init"
                  fluid
                  v-model="init"
                />
                <label for="init">Initial storage content</label>
              </FloatLabel>
              <FloatLabel variant="on">
                <InputNumber
                  :invalid="invalids.includes(Errors.discharge)"
                  :max-fraction-digits="20"
                  v-tooltip.bottom="
                    'Energy losses due to self-discharge per hour as a fraction (1=100%/h).'
                  "
                  id="discharge"
                  fluid
                  v-model="discharge"
                />
                <label for="discharge">Discharge</label>
              </FloatLabel>
              <FloatLabel variant="on">
                <InputNumber
                  :invalid="invalids.includes(Errors.epratio)"
                  :max-fraction-digits="2"
                  v-tooltip.bottom="
                    'Fixed ratio of the storage energy capacity to its power capacity. For the types of storages whose energy and power capacity may be sized independently from each other, this cell should be left empty.'
                  "
                  id="epratio"
                  fluid
                  v-model="epratio"
                />
                <label for="epratio">Energy to power ratio (hours)</label>
              </FloatLabel>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <FloatLabel variant="on">
                <Select
                  optionLabel="disp_name"
                  dataKey="name"
                  v-model="commodity"
                  display="chip"
                  :options="coms"
                  filter
                  fluid
                  id="coms"
                />
                <label for="coms">Commodity</label>
              </FloatLabel>
            </div>
          </div>
        </AccordionContent>
      </AccordionPanel>
    </Accordion>
    <Message v-if="commodity?.default" severity="warn">
      Default commodities will be added automatically
    </Message>
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
import { computed, inject, ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useRoute } from 'vue-router'
import type { Storage } from '@/backend/interfaces'
import {
  useDefCommodities,
  useProjectSiteCommodities,
} from '@/backend/commodities'

const toast = useToast()
const route = useRoute()

const advanced = inject('advanced')

const props = defineProps<{
  submitLabel: string
  storage?: Storage
  loading: boolean
  site_name: string
  delete?: boolean
}>()
const emit = defineEmits<{
  submit: [storage: Storage]
  onDelete: []
}>()

const { data: commodities } = useProjectSiteCommodities(route, props.site_name)
const { data: def_commodities } = useDefCommodities()

const coms = computed(() => {
  if (!commodities.value) return []
  if (!def_commodities.value) return commodities.value

  return [
    ...commodities.value.map(com => {
      return {
        name: com.name,
        disp_name: com.name,
        default: false,
        unitR: com.unitR,
        unitC: com.unitC,
      }
    }),
    ...def_commodities.value
      .filter(
        def_com => !commodities.value.some(com => def_com.name == com.name),
      )
      .map(def_com => {
        return {
          name: def_com.name,
          disp_name: def_com.name + ' (Default)',
          default: true,
          unitR: def_com.unitR,
          unitC: def_com.unitC,
        }
      }),
  ]
})

function defaultValue<T>(val: T | null | undefined, def: T) {
  if (val == null) return def
  return val
}

const name = ref(defaultValue(props.storage?.name, ''))
const description = ref(defaultValue(props.storage?.description, ''))

const instcapc = ref(defaultValue(props.storage?.instcapc, undefined))
const caploc = ref(defaultValue(props.storage?.caploc, undefined))
const capupc = ref(defaultValue(props.storage?.capupc, undefined))

const instcapp = ref(defaultValue(props.storage?.instcapp, undefined))
const caplop = ref(defaultValue(props.storage?.caplop, undefined))
const capupp = ref(defaultValue(props.storage?.capupp, undefined))

const effin = ref(defaultValue(props.storage?.effin, undefined))
const effout = ref(defaultValue(props.storage?.effout, undefined))

const invcostc = ref(defaultValue(props.storage?.invcostc, undefined))
const fixcostc = ref(defaultValue(props.storage?.fixcostc, undefined))
const varcostc = ref(defaultValue(props.storage?.varcostc, undefined))

const invcostp = ref(defaultValue(props.storage?.invcostp, undefined))
const fixcostp = ref(defaultValue(props.storage?.fixcostp, undefined))
const varcostp = ref(defaultValue(props.storage?.varcostp, undefined))

const wacc = ref(defaultValue(props.storage?.wacc, undefined))
const depreciation = ref(defaultValue(props.storage?.depreciation, undefined))

const init = ref(defaultValue(props.storage?.init, undefined))
const discharge = ref(defaultValue(props.storage?.discharge, undefined))
const epratio = ref(defaultValue(props.storage?.epratio, undefined))

interface ComTag {
  name: string
  disp_name: string
  default: boolean
  unitR: string
  unitC: string
}

const commodity = ref<ComTag | undefined>(
  props.storage
    ? {
        name: props.storage.commodity,
        disp_name: props.storage.commodity,
        default: false,
        unitR: 'kW',
        unitC: 'kWh',
      }
    : undefined,
)

const unitR = computed(() => commodity.value?.unitR || 'kW')
const unitC = computed(() => commodity.value?.unitC || 'kWh')
watch(
  commodities,
  () => {
    if (!commodities.value || !commodity.value) return

    commodities.value.forEach(com => {
      if (com.name !== commodity.value?.name) return

      commodity.value.unitR = com.unitR
      commodity.value.unitC = com.unitC
    })
  },
  { immediate: true },
)

enum Errors {
  name,
  description,
  instcapc,
  caploc,
  capupc,
  instcapp,
  caplop,
  capupp,
  effin,
  effout,
  invcostc,
  fixcostc,
  varcostc,
  invcostp,
  fixcostp,
  varcostp,
  wacc,
  depreciation,
  init,
  discharge,
  epratio,
  commodity,
}

const invalids = ref<Errors[]>([])

function check() {
  invalids.value = []
  if (!name.value) invalids.value.push(Errors.name)

  if (instcapc.value === undefined || instcapc.value < 0)
    invalids.value.push(Errors.instcapc)
  if (instcapp.value === undefined || instcapp.value < 0)
    invalids.value.push(Errors.instcapp)
  if (instcapc.value !== undefined)
    if (caploc.value === undefined || caploc.value < 0)
      invalids.value.push(Errors.caploc)
  if (instcapp.value !== undefined)
    if (caplop.value === undefined || caplop.value < 0)
      invalids.value.push(Errors.caplop)
  if (instcapc.value !== undefined)
    if (
      capupc.value === undefined ||
      (capupc.value < instcapc.value && capupc.value >= 0)
    )
      invalids.value.push(Errors.capupc)
  if (instcapp.value !== undefined)
    if (
      capupp.value === undefined ||
      (capupp.value < instcapp.value && capupp.value >= 0)
    )
      invalids.value.push(Errors.capupp)
  if (
    caploc.value !== undefined &&
    capupc.value !== undefined &&
    capupc.value >= 0 &&
    caploc.value > capupc.value
  ) {
    invalids.value.push(Errors.caploc)
    invalids.value.push(Errors.capupc)
  }
  if (
    caplop.value !== undefined &&
    capupp.value !== undefined &&
    capupp.value >= 0 &&
    caplop.value > capupp.value
  ) {
    invalids.value.push(Errors.caplop)
    invalids.value.push(Errors.capupp)
  }

  if (effin.value === undefined || effin.value < 0 || effin.value > 1)
    invalids.value.push(Errors.effin)
  if (effout.value === undefined || effout.value < 0 || effout.value > 1)
    invalids.value.push(Errors.effout)

  if (invcostc.value === undefined || invcostc.value < 0)
    invalids.value.push(Errors.invcostc)
  if (fixcostc.value === undefined || fixcostc.value < 0)
    invalids.value.push(Errors.fixcostc)
  if (varcostc.value === undefined || varcostc.value < 0)
    invalids.value.push(Errors.varcostc)
  if (invcostp.value === undefined || invcostp.value < 0)
    invalids.value.push(Errors.invcostp)
  if (fixcostp.value === undefined || fixcostp.value < 0)
    invalids.value.push(Errors.fixcostp)
  if (varcostp.value === undefined || varcostp.value < 0)
    invalids.value.push(Errors.varcostp)

  if (wacc.value === undefined || wacc.value < 0 || wacc.value > 1)
    invalids.value.push(Errors.wacc)
  if (depreciation.value === undefined || depreciation.value < 0)
    invalids.value.push(Errors.depreciation)

  if (init.value === undefined || init.value < 0 || init.value > 1)
    invalids.value.push(Errors.init)
  if (
    discharge.value === undefined ||
    discharge.value < 0 ||
    discharge.value > 1
  )
    invalids.value.push(Errors.discharge)

  if (epratio.value !== undefined && epratio.value < 0)
    invalids.value.push(Errors.epratio)

  if (commodity.value === undefined) invalids.value.push(Errors.commodity)

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
    instcapc: instcapc.value || 0,
    caploc: caploc.value || 0,
    capupc: capupc.value || 0,
    instcapp: instcapp.value || 0,
    caplop: caplop.value || 0,
    capupp: capupp.value || 0,
    effin: effin.value || 0,
    effout: effout.value || 0,
    invcostc: invcostc.value || 0,
    fixcostc: fixcostc.value || 0,
    varcostc: varcostc.value || 0,
    invcostp: invcostp.value || 0,
    fixcostp: fixcostp.value || 0,
    varcostp: varcostp.value || 0,
    wacc: wacc.value || 0,
    depreciation: depreciation.value || 0,
    init: init.value || 0,
    discharge: discharge.value || 0,
    epratio: epratio.value || 0,
    commodity: commodity.value?.name || '',
  })
}

function deleteStorage() {
  emit('onDelete')
}
</script>

<style scoped></style>
