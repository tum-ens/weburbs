<template>
  <DefaultLayout>
    <Card>
      <template #title>
        <span>Compare Results</span>
      </template>
      <template #content>
        <div class="flex flex-col gap-4">
          <div class="flex items-end gap-3 flex-wrap">
            <FloatLabel variant="on" class="w-[28rem] max-w-full">
              <MultiSelect
                inputId="compare-projects"
                fluid
                display="chip"
                filter
                :showToggleAll="false"
                :selectionLimit="6"
                :options="projectOptions"
                optionLabel="name"
                optionValue="name"
                v-model="selectedProjects"
              />
              <label for="compare-projects">Select up to 6 projects</label>
            </FloatLabel>
            <span class="text-sm text-surface-500 dark:text-surface-400">
              Only projects with completed simulation results can be compared.
            </span>
          </div>

          <!-- Per-project errors (e.g. no simulation results) -->
          <div v-if="errorRows.length" class="flex flex-col gap-2">
            <Message
              v-for="row in errorRows"
              :key="row.project"
              severity="error"
              :closable="false"
            >
              {{ row.project }}: {{ row.error }}
            </Message>
          </div>

          <div
            v-if="loading"
            class="flex items-center gap-2 text-surface-500 dark:text-surface-400"
          >
            <i class="pi pi-spin pi-spinner" />
            <span>Loading simulation results…</span>
          </div>

          <template v-if="!loading && chartProjects.length">
            <!-- Stacked cost breakdown comparison bar chart -->
            <div>
              <h3 class="font-bold mb-1">Total costs</h3>
              <div
                v-if="availableCostCategories.length"
                class="flex flex-wrap items-center gap-x-4 gap-y-2 mb-3"
              >
                <span class="text-sm text-surface-500 dark:text-surface-400">
                  Show:
                </span>
                <label
                  v-for="category in availableCostCategories"
                  :key="category"
                  :for="`cost-cat-${category}`"
                  class="flex items-center gap-2 cursor-pointer text-sm"
                >
                  <Checkbox
                    :inputId="`cost-cat-${category}`"
                    v-model="selectedCostCategories"
                    :value="category"
                  />
                  <span
                    class="inline-block w-2.5 h-2.5 rounded-sm shrink-0"
                    :style="{ backgroundColor: costColor(category) }"
                  />
                  {{ category }}
                </label>
              </div>
              <Message
                v-if="!selectedCostCategories.length"
                severity="info"
                :closable="false"
                class="mb-3"
              >
                Select at least one cost category to display the chart.
              </Message>
              <PlotlyDiagram
                v-if="selectedCostCategories.length"
                title="Cost breakdown comparison"
                :data="chartData"
                titleX="Project"
                titleY="Cost [€]"
                :bargap="0.35"
                :margin="{ t: 60, l: 100, r: 30, b: 90 }"
              />
            </div>

            <!-- LCOE generated / consumed comparison -->
            <div>
              <div class="flex items-end gap-3 flex-wrap mb-3">
                <h3 class="font-bold">Levelized cost</h3>
                <FloatLabel variant="on" class="w-56">
                  <Select
                    inputId="compare-lcoe-metric"
                    fluid
                    :options="lcoeMetricOptions"
                    optionLabel="label"
                    optionValue="value"
                    v-model="selectedLcoeMetric"
                  />
                  <label for="compare-lcoe-metric">LCOE metric</label>
                </FloatLabel>
                <FloatLabel variant="on" class="w-44">
                  <Select
                    inputId="compare-lcoe-carrier"
                    fluid
                    :options="lcoeCarrierOptions"
                    optionLabel="label"
                    optionValue="value"
                    v-model="selectedLcoeCarrier"
                  />
                  <label for="compare-lcoe-carrier">Commodity</label>
                </FloatLabel>
                <FloatLabel variant="on" class="w-36">
                  <Select
                    inputId="compare-lcoe-unit"
                    fluid
                    :options="lcoeUnitOptions"
                    optionLabel="label"
                    optionValue="value"
                    v-model="selectedLcoeUnit"
                  />
                  <label for="compare-lcoe-unit">LCOE unit</label>
                </FloatLabel>
              </div>
              <PlotlyDiagram
                v-if="lcoeChartData.length"
                :title="lcoeChartTitle"
                :data="lcoeChartData"
                titleX="Project"
                :titleY="lcoeChartAxis"
                :bargap="0.35"
                :margin="{ t: 60, l: 100, r: 30, b: 90 }"
              />
              <div
                v-else
                class="text-sm text-surface-500 dark:text-surface-400"
              >
                No energy data available to compute
                {{ selectedLcoeCarrier === 'heat' ? 'LCOH' : 'LCOE' }}.
              </div>
            </div>

            <!-- Process installed capacity (grouped by process name) -->
            <div v-if="processCapChart.length">
              <h3 class="font-bold mb-1">Installed capacity — Processes</h3>
              <PlotlyDiagram
                title="Installed capacity per process"
                :data="processCapChart"
                barmode="group"
                titleX="Process"
                titleY="Installed capacity [MW]"
                :bargap="0.3"
                :bargroupgap="0.08"
                :margin="{ t: 60, l: 100, r: 30, b: 120 }"
              />
            </div>

            <!-- Process total annual production (grouped by process name) -->
            <div v-if="processProdChart.length">
              <h3 class="font-bold mb-1">Total annual production — Processes</h3>
              <PlotlyDiagram
                title="Annual production per process"
                :data="processProdChart"
                barmode="group"
                titleX="Process"
                titleY="Annual production [MWh]"
                :bargap="0.3"
                :bargroupgap="0.08"
                :margin="{ t: 60, l: 100, r: 30, b: 120 }"
              />
            </div>

            <!-- Storage installed capacity (grouped by storage name) -->
            <div v-if="storageCapChart.length">
              <h3 class="font-bold mb-1">Installed capacity — Storage</h3>
              <PlotlyDiagram
                title="Installed energy capacity per storage"
                :data="storageCapChart"
                barmode="group"
                titleX="Storage"
                titleY="Energy capacity [MWh]"
                :bargap="0.3"
                :bargroupgap="0.08"
                :margin="{ t: 60, l: 100, r: 30, b: 120 }"
              />
            </div>

            <!-- Storage full cycles (grouped by storage name) -->
            <div v-if="storageCyclesChart.length">
              <h3 class="font-bold mb-1">Full cycles — Storage</h3>
              <PlotlyDiagram
                title="Storage full cycles"
                :data="storageCyclesChart"
                barmode="group"
                titleX="Storage"
                titleY="Full cycles"
                :bargap="0.3"
                :bargroupgap="0.08"
                :margin="{ t: 60, l: 100, r: 30, b: 120 }"
              />
            </div>
          </template>
          <div
            v-else-if="!loading && !selectedProjects.length"
            class="text-surface-500 dark:text-surface-400"
          >
            Select projects above to compare their results.
          </div>
          <div
            v-else-if="!loading && !chartProjects.length"
            class="text-surface-500 dark:text-surface-400"
          >
            None of the selected projects have results to compare yet.
          </div>
        </div>
      </template>
    </Card>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import axios from 'axios'
import DefaultLayout from '@/layout/DefaultLayout.vue'
import PlotlyDiagram from '@/plotly/PlotlyDiagram.vue'
import { useProjectList } from '@/backend/projects'
import { useAuthenticated } from '@/backend/security'
import { SimulationResultStatus } from '@/backend/interfaces'
import type {
  Simulation,
  SimulationInfo,
  SimulationsResults,
} from '@/backend/interfaces'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { convertToDisplayEnergy, findCarrierUnits } from '@/helper/units'

const router = useRouter()
const route = useRoute()
const toast = useToast()

const { data: authenticated } = useAuthenticated()
watch(
  authenticated,
  () => {
    if (authenticated.value === false) {
      router.push({ name: 'Login', query: { redirect: route.fullPath } })
    }
  },
  { immediate: true },
)

const { data: projects } = useProjectList()
const projectOptions = computed(() => projects.value ?? [])

const selectedProjects = ref<string[]>([])

interface ProjectMetrics {
  processCap: Record<string, number>
  processProd: Record<string, number>
  storageCap: Record<string, number>
  storageCycles: Record<string, number>
}

interface LcoeValues {
  elecGenerated: number
  elecConsumed: number
  heatGenerated: number
  heatConsumed: number
}

interface CompareRow {
  project: string
  costs: Record<string, number> | null
  metrics: ProjectMetrics | null
  lcoe: LcoeValues | null
  error?: string
}

const rows = ref<CompareRow[]>([])
const loading = ref(false)

const errorRows = computed(() => rows.value.filter(r => !!r.error))
const chartProjects = computed(() =>
  rows.value.filter(r => r.error === undefined && r.costs !== null),
)

// Distinct color per project, kept consistent across all comparison charts.
const PROJECT_COLORS = [
  '#3b82f6',
  '#f59e0b',
  '#10b981',
  '#ef4444',
  '#8b5cf6',
  '#14b8a6',
]

// Fixed colors per known cost category, plus a fallback palette for any extras.
const COST_COLORS: Record<string, string> = {
  Invest: '#3b82f6',
  Fixed: '#f59e0b',
  Fuel: '#ef4444',
  Variable: '#10b981',
  Purchase: '#8b5cf6',
  Environmental: '#6b7280',
  Environment: '#6b7280',
}
const FALLBACK_COLORS = [
  '#ec4899',
  '#14b8a6',
  '#a855f7',
  '#84cc16',
  '#f97316',
  '#0ea5e9',
]
const PREFERRED_ORDER = [
  'Invest',
  'Fixed',
  'Fuel',
  'Variable',
  'Purchase',
  'Environmental',
  'Environment',
]

const selectedCostCategories = ref<string[]>([])

function sortCostCategories(categories: string[]): string[] {
  return [...categories].sort((a, b) => {
    const ia = PREFERRED_ORDER.indexOf(a)
    const ib = PREFERRED_ORDER.indexOf(b)
    return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib)
  })
}

function costColor(category: string): string {
  if (COST_COLORS[category]) return COST_COLORS[category]
  const idx = availableCostCategories.value.indexOf(category)
  return FALLBACK_COLORS[
    (idx >= 0 ? idx : 0) % FALLBACK_COLORS.length
  ]
}

const availableCostCategories = computed(() => {
  const categories: string[] = []
  for (const row of chartProjects.value) {
    for (const key of Object.keys(row.costs ?? {})) {
      if (!categories.includes(key)) categories.push(key)
    }
  }
  return sortCostCategories(categories)
})

watch(
  availableCostCategories,
  categories => {
    if (!categories.length) {
      selectedCostCategories.value = []
      return
    }
    const kept = selectedCostCategories.value.filter(c =>
      categories.includes(c),
    )
    const added = categories.filter(
      c => !selectedCostCategories.value.includes(c),
    )
    selectedCostCategories.value =
      kept.length === 0 ? [...categories] : [...kept, ...added]
  },
  { immediate: true },
)

// One stacked bar per project; one trace (colored) per cost category.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const chartData = computed<any[]>(() => {
  const valid = chartProjects.value
  if (!valid.length) return []

  const categories = availableCostCategories.value.filter(c =>
    selectedCostCategories.value.includes(c),
  )
  if (!categories.length) return []

  const traces = categories.map(category => {
    const yValues = valid.map(r => r.costs?.[category] ?? 0)
    return {
      type: 'bar',
      name: category,
      x: valid.map(r => r.project),
      y: yValues,
      // Compact value centered in each segment; hide labels for ~zero values.
      text: yValues.map(v => (Math.abs(v) > 1e-6 ? compactNumber(v) : '')),
      texttemplate: '%{text}',
      textposition: 'inside',
      insidetextanchor: 'middle',
      constraintext: 'inside',
      cliponaxis: false,
      textfont: { size: 9, color: '#ffffff' },
      textangle: 0,
      hovertemplate: `${category}: %{y:,.0f} €<extra></extra>`,
      marker: { color: costColor(category) },
    }
  })

  // Total label on top of each project's stacked bar (selected categories only).
  const totals = valid.map(r =>
    categories.reduce((sum, cat) => sum + (r.costs?.[cat] ?? 0), 0),
  )
  traces.push({
    type: 'scatter',
    mode: 'text',
    name: 'Total',
    x: valid.map(r => r.project),
    y: totals,
    text: totals.map(t => compactNumber(t)),
    texttemplate: '%{text}',
    textposition: 'top center',
    textfont: { size: 12, color: '#111827' },
    cliponaxis: false,
    showlegend: false,
    hoverinfo: 'skip',
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } as any)

  return traces
})

const compactFormatter = new Intl.NumberFormat('en', {
  notation: 'compact',
  maximumFractionDigits: 1,
})
function compactNumber(value: number): string {
  return compactFormatter.format(value)
}

// Build a grouped bar chart: x = union of entity names, one bar (trace) per
// project so equally-named entities sit adjacent. Missing entities render as 0.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function groupedChart(metricKey: keyof ProjectMetrics): any[] {
  const valid = chartProjects.value
  if (!valid.length) return []

  const names: string[] = []
  for (const row of valid) {
    for (const name of Object.keys(row.metrics?.[metricKey] ?? {})) {
      if (!names.includes(name)) names.push(name)
    }
  }
  if (!names.length) return []
  names.sort()

  return valid.map((row, i) => {
    const yValues = names.map(n => row.metrics?.[metricKey]?.[n] ?? 0)
    return {
      type: 'bar',
      name: row.project,
      x: names,
      y: yValues,
      text: yValues.map(v => (Math.abs(v) > 1e-6 ? compactNumber(v) : '')),
      texttemplate: '%{text}',
      textposition: 'outside',
      textfont: { size: 9 },
      cliponaxis: false,
      hovertemplate: `${row.project} — %{x}: %{y:,.2f}<extra></extra>`,
      marker: { color: PROJECT_COLORS[i % PROJECT_COLORS.length] },
    }
  })
}

const processCapChart = computed(() => groupedChart('processCap'))
const processProdChart = computed(() => groupedChart('processProd'))
const storageCapChart = computed(() => groupedChart('storageCap'))
const storageCyclesChart = computed(() => groupedChart('storageCycles'))

const lcoeMetricOptions = [
  { label: 'LCOE generated (per delivered)', value: 'generated' },
  { label: 'LCOE consumed (per demand)', value: 'consumed' },
]
const lcoeCarrierOptions = [
  { label: 'Electricity', value: 'elec' },
  { label: 'Heat', value: 'heat' },
]
const lcoeUnitOptions = [
  { label: '€/MWh', value: 'MWh' },
  { label: '€/kWh', value: 'kWh' },
]
const selectedLcoeMetric = ref<'generated' | 'consumed'>('generated')
const selectedLcoeCarrier = ref<'elec' | 'heat'>('elec')
const selectedLcoeUnit = ref<'MWh' | 'kWh'>('MWh')

const lcoeUnitSuffix = computed(() => `€/${selectedLcoeUnit.value}`)

const lcoeChartTitle = computed(() => {
  const name = selectedLcoeCarrier.value === 'heat' ? 'LCOH' : 'LCOE'
  return selectedLcoeMetric.value === 'generated'
    ? `${name} generated (per delivered)`
    : `${name} consumed (per demand)`
})

const lcoeChartAxis = computed(() => {
  const name = selectedLcoeCarrier.value === 'heat' ? 'LCOH' : 'LCOE'
  return `${name} [${lcoeUnitSuffix.value}]`
})

// Stored LCOE is €/MWh; kWh is 1/1000 of that.
function lcoeInSelectedUnit(valuePerMWh: number): number {
  return selectedLcoeUnit.value === 'kWh' ? valuePerMWh / 1000 : valuePerMWh
}

function formatLcoe(value: number): string {
  if (Math.abs(value) < 1e-12) return ''
  return selectedLcoeUnit.value === 'kWh' ? value.toFixed(4) : value.toFixed(2)
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const lcoeChartData = computed<any[]>(() => {
  const valid = chartProjects.value.filter(r => r.lcoe)
  if (!valid.length) return []

  const key: keyof LcoeValues =
    selectedLcoeCarrier.value === 'heat'
      ? selectedLcoeMetric.value === 'generated'
        ? 'heatGenerated'
        : 'heatConsumed'
      : selectedLcoeMetric.value === 'generated'
        ? 'elecGenerated'
        : 'elecConsumed'

  const yValues = valid.map(r => lcoeInSelectedUnit(r.lcoe?.[key] ?? 0))
  if (yValues.every(v => Math.abs(v) < 1e-12)) return []

  const unit = lcoeUnitSuffix.value
  return [
    {
      type: 'bar',
      name: lcoeChartTitle.value,
      x: valid.map(r => r.project),
      y: yValues,
      text: yValues.map(v => formatLcoe(v)),
      texttemplate: '%{text}',
      textposition: 'outside',
      textfont: { size: 11 },
      cliponaxis: false,
      hovertemplate: `%{x}: %{y:,.4f} ${unit}<extra></extra>`,
      marker: {
        color: valid.map(
          (_, i) => PROJECT_COLORS[i % PROJECT_COLORS.length],
        ),
      },
      showlegend: false,
    },
  ]
})

function sumArray(arr: unknown): number {
  return Array.isArray(arr)
    ? arr.reduce<number>((a, b) => a + (typeof b === 'number' ? b : 0), 0)
    : 0
}

// Extract per-process and per-storage comparison metrics from a result payload.
// `config` carries commodity types so production can be limited to demand commodities.
function computeMetrics(
  result: SimulationsResults,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  config: any,
): ProjectMetrics {
  const processCap: Record<string, number> = {}
  const processProd: Record<string, number> = {}
  const storageCap: Record<string, number> = {}

  const isDemandCommodity = (site: string, com: string) =>
    config?.site?.[site]?.commodity?.[com]?.Type === 'Demand'

  // Process installed capacity (Total) aggregated across sites by name.
  const processObj = result.process ?? {}
  for (const site of Object.keys(processObj)) {
    for (const [proc, vals] of Object.entries(processObj[site] ?? {})) {
      processCap[proc] = (processCap[proc] ?? 0) + (vals?.Total ?? 0)
    }
  }

  const resultsObj = result.results ?? {}

  // Process annual production = sum of created timeseries, split per output
  // commodity (a process can feed more than one commodity). Limited to demand
  // commodities only.
  for (const site of Object.keys(resultsObj)) {
    for (const com of Object.keys(resultsObj[site] ?? {})) {
      if (!isDemandCommodity(site, com)) continue
      const created = resultsObj[site][com]?.created ?? {}
      for (const [proc, ts] of Object.entries(created)) {
        const key = `${proc} (${com})`
        processProd[key] = (processProd[key] ?? 0) + sumArray(ts)
      }
    }
  }

  // Storage energy capacity (CTotal) by storage name + retrieved-energy
  // attribution for full cycles (keyed per storage + commodity).
  const cycleCap: Record<string, number> = {}
  const cycleRetrieved: Record<string, number> = {}
  const storageObj = result.storage ?? {}
  for (const site of Object.keys(storageObj)) {
    for (const com of Object.keys(storageObj[site] ?? {})) {
      const storCom = storageObj[site][com] ?? {}

      let commodityCap = 0
      for (const stor of Object.values(storCom)) {
        commodityCap += stor?.CTotal ?? 0
      }
      const retrieved = sumArray(resultsObj[site]?.[com]?.storage?.Retrieved)

      for (const [storName, stor] of Object.entries(storCom)) {
        const cap = stor?.CTotal ?? 0
        storageCap[storName] = (storageCap[storName] ?? 0) + cap

        const key = `${storName} (${com})`
        const share = commodityCap > 0 ? cap / commodityCap : 0
        cycleCap[key] = (cycleCap[key] ?? 0) + cap
        cycleRetrieved[key] = (cycleRetrieved[key] ?? 0) + retrieved * share
      }
    }
  }

  // Full cycles = retrieved energy / installed energy capacity.
  const storageCycles: Record<string, number> = {}
  for (const key of Object.keys(cycleCap)) {
    const cap = cycleCap[key]
    storageCycles[key] = cap > 0 ? (cycleRetrieved[key] ?? 0) / cap : 0
  }

  return { processCap, processProd, storageCap, storageCycles }
}

function isElecCommodity(name: string): boolean {
  return name.toUpperCase().includes('ELEC')
}

function isHeatCommodity(name: string): boolean {
  const n = name.toUpperCase()
  return (
    n.includes('HEAT') ||
    n.includes('THERMAL') ||
    n.includes('MJ') ||
    n.includes('GJ') ||
    n.includes('KWH_TH')
  )
}

function totalSystemCost(costs: Record<string, number>): number {
  return (
    (costs.Invest || 0) +
    (costs.Fixed || 0) +
    (costs.Fuel || 0) +
    (costs.Variable || 0) +
    (costs.Purchase || 0) +
    (costs.Environmental ?? costs.Environment ?? 0)
  )
}

function lcoeFromEnergy(
  totalCost: number,
  energyNative: number,
  unitC?: string,
): number {
  if (!energyNative || !totalCost) return 0
  const energyMWh = convertToDisplayEnergy(energyNative, unitC, 'MW')
  if (!energyMWh) return 0
  return totalCost / energyMWh
}

function sumCarrierEnergy(
  result: SimulationsResults,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  config: any,
  match: (name: string) => boolean,
): { generated: number; consumed: number } {
  let generated = 0
  let consumed = 0
  const resultsObj = result.results ?? {}
  for (const site of Object.keys(resultsObj)) {
    const siteConfig = config?.site?.[site]
    for (const com of Object.keys(resultsObj[site] ?? {})) {
      if (!match(com)) continue
      const comResults = resultsObj[site][com]
      for (const procName of Object.keys(comResults?.created ?? {})) {
        if (!siteConfig?.process?.[procName]) continue
        generated += sumArray(comResults.created[procName])
      }
      consumed += sumArray(comResults?.demand)
    }
  }
  return { generated, consumed }
}

function computeLcoe(
  result: SimulationsResults,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  config: any,
  costs: Record<string, number>,
): LcoeValues {
  const totalCost = totalSystemCost(costs)
  const elec = sumCarrierEnergy(result, config, isElecCommodity)
  const heat = sumCarrierEnergy(result, config, isHeatCommodity)
  const elecUnitC = findCarrierUnits(config, 'elec').unitC
  const heatUnitC = findCarrierUnits(config, 'heat').unitC
  return {
    elecGenerated: lcoeFromEnergy(totalCost, elec.generated, elecUnitC),
    elecConsumed: lcoeFromEnergy(totalCost, elec.consumed, elecUnitC),
    heatGenerated: lcoeFromEnergy(totalCost, heat.generated, heatUnitC),
    heatConsumed: lcoeFromEnergy(totalCost, heat.consumed, heatUnitC),
  }
}

async function loadProjectCosts(project: string): Promise<CompareRow> {
  try {
    const sims = await axios
      .get<SimulationInfo[]>(`/api/project/${project}/simulate/results/`)
      .then(res => res.data)

    const completed = sims
      .filter(s => s.completed && s.status === SimulationResultStatus.Optimal)
      .sort(
        (a, b) =>
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
      )

    if (!completed.length) {
      return {
        project,
        costs: null,
        metrics: null,
        lcoe: null,
        error: 'No simulation results',
      }
    }

    const simId = completed[0].id
    const [full, config] = await Promise.all([
      axios
        .get<Simulation>(`/api/project/${project}/simulate/result/${simId}/`)
        .then(res => res.data),
      axios
        .get(`/api/project/${project}/simulate/result/${simId}/config/`)
        .then(res => res.data)
        .catch(() => null),
    ])

    const raw = (full.result?.costs ?? {}) as Record<string, unknown>
    const costs: Record<string, number> = {}
    for (const [key, value] of Object.entries(raw)) {
      if (typeof value === 'number') costs[key] = value
    }
    const metrics = computeMetrics(full.result, config)
    const lcoe = computeLcoe(full.result, config, costs)
    return { project, costs, metrics, lcoe }
  } catch {
    return {
      project,
      costs: null,
      metrics: null,
      lcoe: null,
      error: 'Failed to load results',
    }
  }
}

let loadToken = 0
watch(
  selectedProjects,
  async selected => {
    const token = ++loadToken
    if (!selected.length) {
      rows.value = []
      return
    }

    loading.value = true
    const previousErrors = new Set(errorRows.value.map(r => r.project))
    const results = await Promise.all(selected.map(loadProjectCosts))

    // Ignore stale responses if the selection changed meanwhile.
    if (token !== loadToken) return

    rows.value = results
    loading.value = false

    for (const row of results) {
      if (row.error && !previousErrors.has(row.project)) {
        toast.add({
          severity: 'warn',
          summary: row.project,
          detail: row.error,
          life: 4000,
        })
      }
    }
  },
  { deep: true },
)
</script>

<style scoped></style>
