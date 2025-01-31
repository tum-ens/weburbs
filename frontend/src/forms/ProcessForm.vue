<template>
  <div class="mt-2 flex flex-col gap-3">
    {{ invalids }}
    <FloatLabel variant="on">
      <InputText
        :invalid="invalids.includes('name')"
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
          :invalid="invalids.includes('instcap')"
          :max-fraction-digits="2"
          v-tooltip.bottom="'Existing power throughput capacity per process'"
          id="instcap"
          fluid
          v-model="instcap"
        />
        <label for="instcap">Installed capacity (kW)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('caplo')"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'Minimum required power throughput capacity that is allowed per process. Must be smaller or equal to \'cap-up\', but can be bigger than \'inst-cap\' to force investment.'
          "
          id="caplo"
          fluid
          v-model="caplo"
        />
        <label for="caplo">Minimum capacity (kW)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('capup')"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'Maximum allowed power throughput capacity per process. Must be bigger than or equal to max(\'cap-lo\', \'inst-cap\').'
          "
          id="capup"
          fluid
          v-model="capup"
        />
        <label for="capup">Maximum capacity (kW)</label>
      </FloatLabel>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('maxgrad')"
          :max-fraction-digits="2"
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
          :max-fraction-digits="2"
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
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'Total investement cost for adding capacity. Is annualized in the model using the annuity factor derived from \'wacc\' and \'depreciation\'.'
          "
          id="invcost"
          fluid
          v-model="invcost"
        />
        <label for="invcost">Investment cost (€/kW)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('fixcost')"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'Operation independent costs for existing and new capacities per kW throughput power.'
          "
          id="fixcost"
          fluid
          v-model="fixcost"
        />
        <label for="fixcost">Annual fix cost (€/kW/a)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('varcost')"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'Variable costs per throughput energy unit (kWh) produced. This includes wear and tear of moving parts, operation liquids, but excluding fuel costs, as they are included in table Commodity, column \'price\'.'
          "
          id="varcost"
          fluid
          v-model="varcost"
        />
        <label for="varcost">Variable costs (€/kWh)</label>
      </FloatLabel>
    </div>
    <div class="grid grid-cols-3 gap-3">
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('wacc')"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'Percentage of costs for capital after taxes. Used to calculate annuity factor for investment costs.'
          "
          id="wacc"
          fluid
          v-model="wacc"
        />
        <label for="wacc">Weighted average cost of capital</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('depreciation')"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'Economic lifetime (more conservative than technical lifetime) of a process investment in years (a). Used to calculate annuity factor for investment costs.'
          "
          id="depreciation"
          fluid
          v-model="depreciation"
        />
        <label for="depreciation">Depreciation period (a)</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <InputNumber
          :invalid="invalids.includes('areapercap')"
          :max-fraction-digits="2"
          v-tooltip.bottom="
            'If a process requires area set value here. If no area use is to be considered leave empty.'
          "
          id="areapercap"
          fluid
          v-model="areapercap"
        />
        <label for="areapercap">Area use per capacity (m^2/kW)</label>
      </FloatLabel>
    </div>

    <Accordion value="1" v-if="advanced">
      <AccordionPanel pt:root:class="border-0" value="0">
        <AccordionHeader>Advanced</AccordionHeader>
        <AccordionContent pt:root:class="pt-1">
          <div class="grid grid-cols-2 gap-3">
            <div class="flex flex-col gap-3">
              <FloatLabel variant="on">
                <MultiSelect
                  optionLabel="disp_name"
                  dataKey="name"
                  v-model="inComs"
                  display="chip"
                  :options="coms"
                  filter
                  fluid
                  id="inComs"
                >
                  <template #emptyfilter
                    >Create commodities before using them</template
                  >
                </MultiSelect>
                <label for="inComs">Incoming commodities</label>
              </FloatLabel>
              <div
                v-for="inCom in inComs"
                :key="inCom.name"
                class="grid grid-cols-3 gap-3 items-center"
              >
                <span>{{ inCom.disp_name }}</span>
                <FloatLabel variant="on">
                  <InputNumber
                    id="ratio"
                    :max-fraction-digits="2"
                    fluid
                    v-tooltip="
                      'Input/output quantities, relative to process throughput. Leave empty to not set it.'
                    "
                    v-model="inCom.ratio"
                    :invalid="inCom.ratio === undefined || inCom.ratio < 0"
                  />
                  <label for="ratio">Ratio</label>
                </FloatLabel>
                <FloatLabel variant="on">
                  <InputNumber
                    id="ratiomin"
                    :max-fraction-digits="2"
                    fluid
                    v-tooltip="
                      'Input/Output ratio at point of minimum operation (min-fract in \'Process\' sheet). All values have to be larger/equal to ratio! Leave empty to not set it.'
                    "
                    v-model="inCom.ratiomin"
                    :invalid="
                      inCom.ratiomin === undefined || inCom.ratiomin < 0
                    "
                  />
                  <label for="ratiomin">Minimum ratio</label>
                </FloatLabel>
              </div>
            </div>
            <div class="flex flex-col gap-3">
              <FloatLabel variant="on">
                <MultiSelect
                  optionLabel="disp_name"
                  dataKey="name"
                  v-model="outComs"
                  display="chip"
                  :options="coms"
                  filter
                  fluid
                  id="outComs"
                >
                  <template #emptyfilter
                    >Create commodities before using them</template
                  >
                </MultiSelect>
                <label for="outComs">Outgoing commodities</label>
              </FloatLabel>
              <div
                v-for="outCom in outComs"
                :key="outCom.name"
                class="grid grid-cols-3 gap-3 items-center"
              >
                <span>{{ outCom.disp_name }}</span>
                <FloatLabel variant="on">
                  <InputNumber
                    id="ratio"
                    :max-fraction-digits="2"
                    fluid
                    v-tooltip="
                      'Input/output quantities, relative to process throughput. Leave empty to not set it.'
                    "
                    v-model="outCom.ratio"
                    :invalid="outCom.ratio === undefined || outCom.ratio < 0"
                  />
                  <label for="ratio">Ratio</label>
                </FloatLabel>
                <FloatLabel variant="on">
                  <InputNumber
                    id="ratiomin"
                    :max-fraction-digits="2"
                    fluid
                    v-tooltip="
                      'Input/Output ratio at point of minimum operation (min-fract in \'Process\' sheet). All values have to be larger/equal to ratio! Leave empty to not set it.'
                    "
                    v-model="outCom.ratiomin"
                    :invalid="
                      outCom.ratiomin === undefined || outCom.ratiomin < 0
                    "
                  />
                  <label for="ratiomin">Minimum ratio</label>
                </FloatLabel>
              </div>
            </div>
          </div>
        </AccordionContent>
      </AccordionPanel>
    </Accordion>
    <Message
      v-if="inComs.some(com => com.default) || outComs.some(com => com.default)"
      severity="warn"
    >
      Default commodities will be added automatically
    </Message>
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
import { computed, inject, ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import type { Process, ProcessCommodity } from '@/backend/interfaces'
import {
  useDefCommodities,
  useProjectSiteCommodities,
} from '@/backend/commodities'
import { useRoute } from 'vue-router'

const toast = useToast()
const route = useRoute()

const advanced = inject('advanced')

const props = defineProps<{
  submitLabel: string
  process?: Process
  loading: boolean
  site_name: string
  delete?: boolean
}>()
const emit = defineEmits<{
  submit: [process: Process]
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
        ratio: 1,
        ratiomin: 1,
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
          ratio: 1,
          ratiomin: 1,
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
const depreciation = ref(defaultValue(props.process?.depreciation, undefined))
const areapercap = ref(defaultValue(props.process?.areapercap, undefined))

interface ProcComTag extends ProcessCommodity {
  disp_name: string
  default: boolean
}

const inComs = ref<ProcComTag[]>([])
const outComs = ref<ProcComTag[]>([])
watch(
  coms,
  () => {
    if (!props.process) {
      inComs.value = []
      outComs.value = []
      return
    }

    inComs.value = props.process.in.map(proccom => {
      return {
        ...proccom,
        disp_name: proccom.name,
        default: false,
      }
    })
    outComs.value = props.process.out.map(proccom => {
      return {
        ...proccom,
        disp_name: proccom.name,
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
  if (depreciation.value === undefined || depreciation.value < 0)
    invalids.value.push('depreciation')
  if (areapercap.value !== undefined && areapercap.value < 0)
    invalids.value.push('areapercap')

  for (const inCom of inComs.value) {
    if (inCom.ratio !== undefined && inCom.ratio < 0)
      invalids.value.push('inComRatio')
    if (inCom.ratiomin !== undefined && inCom.ratiomin < 0)
      invalids.value.push('inComRatioMin')
  }
  for (const outCom of outComs.value) {
    if (outCom.ratio !== undefined && outCom.ratio < 0)
      invalids.value.push('outComRatio')
    if (outCom.ratiomin !== undefined && outCom.ratiomin < 0)
      invalids.value.push('outComRatioMin')
  }

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
    depreciation: depreciation.value || 0,
    areapercap: areapercap.value,
    in: inComs.value.map(com => {
      return {
        name: com.name,
        ratio: com.ratio,
        ratiomin: com.ratiomin,
      }
    }),
    out: outComs.value.map(com => {
      return {
        name: com.name,
        ratio: com.ratio,
        ratiomin: com.ratiomin,
      }
    }),
  })
}

function deleteProc() {
  emit('onDelete')
}
</script>

<style scoped></style>
