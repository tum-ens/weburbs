<template>
  <Dialog
    v-model:visible="visible"
    modal
    :header="`WebURBS Documentation (${currentVersion})`"
    :style="{ width: '90vw', maxWidth: '1200px' }"
    :maximizable="true"
    :closable="true"
  >
    <div class="documentation-content">
      <!-- Navigation Tabs -->
      <TabView v-model:activeIndex="activeTabIndex">
        <TabPanel header="Architecture" value="architecture">
          <div class="tab-content">
            <h3 class="text-xl font-bold mb-4 text-primary">System Architecture</h3>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div class="architecture-section">
                <h4 class="text-lg font-semibold mb-3 text-secondary">Frontend Architecture</h4>
                <ul class="list-disc list-inside space-y-2 text-gray-700">
                  <li><strong>Framework:</strong> Vue.js 3 with TypeScript</li>
                  <li><strong>UI Library:</strong> PrimeVue components</li>
                  <li><strong>Styling:</strong> Tailwind CSS</li>
                  <li><strong>Build Tool:</strong> Vite</li>
                  <li><strong>State Management:</strong> Vue Composition API</li>
                  <li><strong>Routing:</strong> Vue Router</li>
                </ul>
              </div>
              
              <div class="architecture-section">
                <h4 class="text-lg font-semibold mb-3 text-secondary">Backend Architecture</h4>
                <ul class="list-disc list-inside space-y-2 text-gray-700">
                  <li><strong>Framework:</strong> Django (Python)</li>
                  <li><strong>Database:</strong> PostgreSQL (default) / SQLite</li>
                  <li><strong>API:</strong> RESTful API with Django REST Framework</li>
                  <li><strong>Authentication:</strong> Django built-in auth system</li>
                  <li><strong>Optimization:</strong> URBS optimizer integration</li>
                </ul>
              </div>
            </div>
            
            <div class="mt-6">
              <h4 class="text-lg font-semibold mb-3 text-secondary">System Components</h4>
              <div class="bg-gray-50 p-4 rounded-lg">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div class="text-center p-3 bg-white rounded border">
                    <i class="pi pi-desktop text-2xl text-primary mb-2"></i>
                    <h5 class="font-semibold">Frontend</h5>
                    <p class="text-sm text-gray-600">User interface for configuration and visualization</p>
                  </div>
                  <div class="text-center p-3 bg-white rounded border">
                    <i class="pi pi-server text-2xl text-primary mb-2"></i>
                    <h5 class="font-semibold">Backend</h5>
                    <p class="text-sm text-gray-600">Data management and optimization engine</p>
                  </div>
                  <div class="text-center p-3 bg-white rounded border">
                    <i class="pi pi-database text-2xl text-primary mb-2"></i>
                    <h5 class="font-semibold">Database</h5>
                    <p class="text-sm text-gray-600">Persistent storage for projects and configurations</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </TabPanel>
        
        <TabPanel header="Modeling Steps" value="modeling">
          <div class="tab-content">
            <h3 class="text-xl font-bold mb-4 text-primary">Step-by-Step Modeling Guide</h3>
            
            <div class="space-y-6">
              <div class="step-item">
                <div class="step-number">1</div>
                <div class="step-content">
                  <h4 class="text-lg font-semibold text-secondary">Project Setup</h4>
                  <p class="text-gray-700 mb-2">Create a new project and configure global settings including project name, description, and basic parameters.</p>
                  <div class="bg-blue-50 p-3 rounded border-l-4 border-blue-400">
                    <strong>Tip:</strong> Start with a descriptive project name and clear description to keep track of your work.
                  </div>
                </div>
              </div>
              
              <div class="step-item">
                <div class="step-number">2</div>
                <div class="step-content">
                  <h4 class="text-lg font-semibold text-secondary">Site Configuration</h4>
                  <p class="text-gray-700 mb-2">Define geographical locations where your energy system components will be situated. Set coordinates and site-specific parameters.</p>
                  <div class="bg-green-50 p-3 rounded border-l-4 border-green-400">
                    <strong>Note:</strong> Sites can represent cities, regions, or specific locations depending on your modeling scope.
                  </div>
                </div>
              </div>
              
              <div class="step-item">
                <div class="step-number">3</div>
                <div class="step-content">
                  <h4 class="text-lg font-semibold text-secondary">Commodity Definition</h4>
                  <p class="text-gray-700 mb-2">Define energy carriers and materials that flow through your system (electricity, heat, hydrogen, etc.).</p>
                  <div class="bg-yellow-50 p-3 rounded border-l-4 border-yellow-400">
                    <strong>Important:</strong> Set appropriate units and constraints for each commodity type.
                  </div>
                </div>
              </div>
              
              <div class="step-item">
                <div class="step-number">4</div>
                <div class="step-content">
                  <h4 class="text-lg font-semibold text-secondary">Process Configuration</h4>
                  <p class="text-gray-700 mb-2">Define energy conversion and production processes (solar panels, wind turbines, power plants, etc.).</p>
                  <div class="bg-purple-50 p-3 rounded border-l-4 border-purple-400">
                    <strong>Key:</strong> Configure input/output commodities, efficiency, costs, and capacity constraints.
                  </div>
                </div>
              </div>
              
              <div class="step-item">
                <div class="step-number">5</div>
                <div class="step-content">
                  <h4 class="text-lg font-semibold text-secondary">Demand Specification</h4>
                  <p class="text-gray-700 mb-2">Define energy demand patterns over time (8760 hours per year) for different commodities at each site.</p>
                  <div class="bg-orange-50 p-3 rounded border-l-4 border-orange-400">
                    <strong>Data:</strong> Use historical data or create synthetic demand profiles based on your use case.
                  </div>
                </div>
              </div>
              
              <div class="step-item">
                <div class="step-number">6</div>
                <div class="step-content">
                  <h4 class="text-lg font-semibold text-secondary">Storage Systems</h4>
                  <p class="text-gray-700 mb-2">Configure energy storage solutions (batteries, thermal storage, etc.) with efficiency and cost parameters.</p>
                  <div class="bg-indigo-50 p-3 rounded border-l-4 border-indigo-400">
                    <strong>Consider:</strong> Storage capacity, charge/discharge efficiency, and degradation over time.
                  </div>
                </div>
              </div>
              
              <div class="step-item">
                <div class="step-number">7</div>
                <div class="step-content">
                  <h4 class="text-lg font-semibold text-secondary">Transmission & Distribution</h4>
                  <p class="text-gray-700 mb-2">Set up energy transmission networks between sites with capacity and efficiency constraints.</p>
                  <div class="bg-red-50 p-3 rounded border-l-4 border-red-400">
                    <strong>Planning:</strong> Consider grid infrastructure costs and transmission losses.
                  </div>
                </div>
              </div>
              
              <div class="step-item">
                <div class="step-number">8</div>
                <div class="step-content">
                  <h4 class="text-lg font-semibold text-secondary">Simulation & Optimization</h4>
                  <p class="text-gray-700 mb-2">Run the URBS optimization to find the least-cost energy system configuration.</p>
                  <div class="bg-teal-50 p-3 rounded border-l-4 border-teal-400">
                    <strong>Analysis:</strong> Review results, costs, and system performance metrics.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </TabPanel>
        
        <TabPanel header="Features" value="features">
          <div class="tab-content">
            <h3 class="text-xl font-bold mb-4 text-primary">Tool Features & Capabilities</h3>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div class="feature-category">
                <h4 class="text-lg font-semibold mb-3 text-secondary">Core Modeling Features</h4>
                <div class="space-y-3">
                  <div class="feature-item">
                    <i class="pi pi-sitemap text-primary mr-2"></i>
                    <span><strong>Multi-site modeling:</strong> Configure energy systems across multiple geographical locations</span>
                  </div>
                  <div class="feature-item">
                    <i class="pi pi-bolt text-primary mr-2"></i>
                    <span><strong>Commodity management:</strong> Define various energy carriers and materials</span>
                  </div>
                  <div class="feature-item">
                    <i class="pi pi-hammer text-primary mr-2"></i>
                    <span><strong>Process configuration:</strong> Set up energy conversion technologies</span>
                  </div>
                  <div class="feature-item">
                    <i class="pi pi-gauge text-primary mr-2"></i>
                    <span><strong>Demand modeling:</strong> Create time-series demand profiles</span>
                  </div>
                  <div class="feature-item">
                    <i class="pi pi-warehouse text-primary mr-2"></i>
                    <span><strong>Storage systems:</strong> Configure energy storage solutions</span>
                  </div>
                  <div class="feature-item">
                    <i class="pi pi-wifi text-primary mr-2"></i>
                    <span><strong>Transmission networks:</strong> Model energy distribution systems</span>
                  </div>
                </div>
              </div>
              
              <div class="feature-category">
                <h4 class="text-lg font-semibold mb-3 text-secondary">Advanced Features</h4>
                <div class="space-y-3">
                  <div class="feature-item">
                    <i class="pi pi-sun text-primary mr-2"></i>
                    <span><strong>SupIm integration:</strong> Automatic solar and wind data from Renewable Ninja</span>
                  </div>
                  <div class="feature-item">
                    <i class="pi pi-sliders-v text-primary mr-2"></i>
                    <span><strong>DSM (Demand Side Management):</strong> Load shifting and demand response</span>
                  </div>
                  <div class="feature-item">
                    <i class="pi pi-dollar text-primary mr-2"></i>
                    <span><strong>Buy/Sell pricing:</strong> Market interaction and price signals</span>
                  </div>
                  <div class="feature-item">
                    <i class="pi pi-hourglass text-primary mr-2"></i>
                    <span><strong>Time-varying efficiency:</strong> Seasonal and temporal efficiency changes</span>
                  </div>
                  <div class="feature-item">
                    <i class="pi pi-chart-line text-primary mr-2"></i>
                    <span><strong>Cost optimization:</strong> Minimize total system costs</span>
                  </div>
                  <div class="feature-item">
                    <i class="pi pi-calendar text-primary mr-2"></i>
                    <span><strong>8760-hour modeling:</strong> Full year hourly resolution</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mt-6">
              <h4 class="text-lg font-semibold mb-3 text-secondary">User Experience Features</h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="text-center p-4 bg-blue-50 rounded-lg border">
                  <i class="pi pi-upload text-2xl text-blue-600 mb-2"></i>
                  <h5 class="font-semibold text-blue-800">Data Import</h5>
                  <p class="text-sm text-blue-700">Upload Excel files and JSON configurations</p>
                </div>
                <div class="text-center p-4 bg-green-50 rounded-lg border">
                  <i class="pi pi-eye text-2xl text-green-600 mb-2"></i>
                  <h5 class="font-semibold text-green-800">Visualization</h5>
                  <p class="text-sm text-green-700">Interactive charts and energy flow diagrams</p>
                </div>
                <div class="text-center p-4 bg-purple-50 rounded-lg border">
                  <i class="pi pi-cog text-2xl text-purple-600 mb-2"></i>
                  <h5 class="font-semibold text-purple-800">Templates</h5>
                  <p class="text-sm text-purple-700">Pre-configured default data and examples</p>
                </div>
              </div>
            </div>
          </div>
        </TabPanel>
        
        <TabPanel header="Configuration" value="configuration">
          <div class="tab-content">
            <h3 class="text-xl font-bold mb-4 text-primary">Configuration Guide</h3>
            
            <div class="space-y-6">
              <div class="config-section">
                <h4 class="text-lg font-semibold mb-3 text-secondary">Default Data Configuration</h4>
                <p class="text-gray-700 mb-3">WebURBS provides pre-configured default data that can be customized for your specific use case.</p>
                <div class="bg-gray-50 p-4 rounded-lg">
                  <h5 class="font-semibold mb-2">Configuration Files Location:</h5>
                  <code class="bg-gray-200 px-2 py-1 rounded text-sm">backend/config/</code>
                  <ul class="list-disc list-inside mt-2 space-y-1 text-sm">
                    <li><code>base_coms.json</code> - Default commodities</li>
                    <li><code>base_demand.json</code> - Default demand patterns</li>
                    <li><code>base_procs.json</code> - Default processes</li>
                    <li><code>base_stor.json</code> - Default storage systems</li>
                  </ul>
                </div>
              </div>
              
              <div class="config-section">
                <h4 class="text-lg font-semibold mb-3 text-secondary">Environment Variables</h4>
                <div class="overflow-x-auto">
                  <table class="min-w-full border border-gray-300">
                    <thead class="bg-gray-100">
                      <tr>
                        <th class="border border-gray-300 px-3 py-2 text-left">Variable</th>
                        <th class="border border-gray-300 px-3 py-2 text-left">Description</th>
                        <th class="border border-gray-300 px-3 py-2 text-left">Example</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td class="border border-gray-300 px-3 py-2 font-mono text-sm">RN_KEY</td>
                        <td class="border border-gray-300 px-3 py-2">Renewable Ninja API key</td>
                        <td class="border border-gray-300 px-3 py-2 font-mono text-sm">your_api_key_here</td>
                      </tr>
                      <tr>
                        <td class="border border-gray-300 px-3 py-2 font-mono text-sm">SECRET_KEY</td>
                        <td class="border border-gray-300 px-3 py-2">Django secret key</td>
                        <td class="border border-gray-300 px-3 py-2 font-mono text-sm">change_me</td>
                      </tr>
                      <tr>
                        <td class="border border-gray-300 px-3 py-2 font-mono text-sm">VUE_APP_API_URL</td>
                        <td class="border border-gray-300 px-3 py-2">Frontend API endpoint</td>
                        <td class="border border-gray-300 px-3 py-2 font-mono text-sm">https://your.domain</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              
              <div class="config-section">
                <h4 class="text-lg font-semibold mb-3 text-secondary">Data Upload Formats</h4>
                <div class="bg-yellow-50 p-4 rounded border-l-4 border-yellow-400">
                  <h5 class="font-semibold text-yellow-800 mb-2">Supported Formats:</h5>
                  <ul class="list-disc list-inside space-y-1 text-yellow-700">
                    <li><strong>Excel (.xlsx):</strong> Multi-sheet configuration files</li>
                    <li><strong>JSON:</strong> Structured configuration data</li>
                    <li><strong>Time Series:</strong> 8760-hour data arrays</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </TabPanel>

        <TabPanel header="Versions" value="versions">
          <div class="tab-content">
            <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
              <h3 class="text-xl font-bold text-primary">Version history</h3>
              <span class="text-sm font-semibold px-3 py-1 rounded-full bg-primary/10 text-primary">
                Current {{ currentVersion }}
              </span>
            </div>
            <p class="text-gray-700 mb-4">
              A new version tab is added whenever a feature is introduced, a
              bug is fixed, or behaviour changes. Versions use
              <code>vX.X.X.X.X</code>.
            </p>

            <TabView v-model:activeIndex="activeVersionIndex">
              <TabPanel
                v-for="ver in versions"
                :key="ver.version"
                :header="ver.version"
                :value="ver.version"
              >
                <div class="version-entry">
                  <div class="flex flex-wrap items-center gap-2 mb-2">
                    <span class="text-lg font-semibold text-secondary">{{
                      ver.version
                    }}</span>
                    <span
                      class="text-xs font-semibold uppercase tracking-wide px-2 py-0.5 rounded"
                      :class="versionTypeClass(ver.type)"
                    >
                      {{ ver.type }}
                    </span>
                    <span class="text-sm text-gray-500">{{ ver.date }}</span>
                  </div>
                  <h4 class="font-semibold mb-2">{{ ver.title }}</h4>
                  <ul class="list-disc list-inside space-y-1 text-gray-700">
                    <li v-for="note in ver.notes" :key="note">{{ note }}</li>
                  </ul>
                </div>
              </TabPanel>
            </TabView>
          </div>
        </TabPanel>
      </TabView>
    </div>
    
    <template #footer>
      <div class="flex justify-between items-center">
        <div class="text-sm text-gray-600">
          <span v-if="activeTabIndex === 0">Architecture Overview</span>
          <span v-else-if="activeTabIndex === 1">Modeling Steps</span>
          <span v-else-if="activeTabIndex === 2">Tool Features</span>
          <span v-else-if="activeTabIndex === 3">Configuration Guide</span>
          <span v-else-if="activeTabIndex === 4">
            Versions ({{ currentVersion }})
          </span>
        </div>
        <Button label="Close" icon="pi pi-times" @click="closeDialog" />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import Dialog from 'primevue/dialog'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'

const visible = defineModel<boolean>('visible', { default: false })

const activeTabIndex = ref(0)
const activeVersionIndex = ref(0)

type VersionType = 'feature' | 'bugfix' | 'change'

interface VersionEntry {
  version: string
  date: string
  type: VersionType
  title: string
  notes: string[]
}

// Newest first. Prepend a new vX.X.X.X.X entry for each feature, bugfix, or change.
const versions: VersionEntry[] = [
  {
    version: 'v0.0.0.0.11',
    date: '2026-11-18',
    type: 'feature',
    title: 'Download input timeseries as Excel',
    notes: [
      'SupIm, demand, time-variable efficiency, and buy/sell price charts now have a Download button beside the graph when a timeseries is present.',
      'The file is named project_series.xlsx. Column A holds the 8760 hourly values. Demand files also store the quantity in cell B1.',
      'Upload that file again on the same screen to restore the series. Simulation result charts are unchanged.',
    ],
  },
  {
    version: 'v0.0.0.0.10',
    date: '2026-09-24',
    type: 'bugfix',
    title: 'Energy diagram storage no longer overlaps processes',
    notes: [
      'Storage attached to a mid-diagram commodity (for example a battery on Elec) was drawn on top of processes in the same column.',
      'It now sits below those processes while staying connected to its selected commodity.',
    ],
  },
  {
    version: 'v0.0.0.0.9',
    date: '2026-09-24',
    type: 'bugfix',
    title: 'Energy diagram storage attaches to its selected commodity',
    notes: [
      'Storage on the energy diagram was always drawn on the rightmost commodity line (often Methanol).',
      'It now connects to the commodity chosen on the storage form, for example Elec for a lithium-ion battery.',
    ],
  },
  {
    version: 'v0.0.0.0.8',
    date: '2026-09-24',
    type: 'feature',
    title: 'Choose commodity types for simulation timeseries',
    notes: [
      'In Configure simulation, choosing Report → With timeseries shows a multi-select for Demand, Buy, Sell, and Env.',
      'The Excel result file now writes a timeseries sheet for each selected type (not Demand only). Site result charts follow the same selection.',
    ],
  },
  {
    version: 'v0.0.0.0.7',
    date: '2026-09-09',
    type: 'feature',
    title: 'LCOE unit dropdown on Compare Results',
    notes: [
      'Compare Results levelized-cost chart now has a unit dropdown to switch between €/MWh and €/kWh.',
    ],
  },
  {
    version: 'v0.0.0.0.6',
    date: '2026-09-09',
    type: 'change',
    title: 'Site process and storage charts ignore electricity/heat filter',
    notes: [
      'Installed process and storage bar charts on the simulation results page now show every process and storage at the site.',
      'The Electricity / Heat dropdown at the top still drives KPIs, LCOE/LCOH, and cost tables, but no longer hides heat or electricity assets in those site charts.',
    ],
  },
  {
    version: 'v0.0.0.0.5',
    date: '2026-09-09',
    type: 'feature',
    title: 'LCOE generated and consumed on Compare Results',
    notes: [
      'Compare Results now has a dropdown to switch between LCOE generated (per delivered energy) and LCOE consumed (per demand).',
      'A second dropdown selects Electricity (LCOE) or Heat (LCOH). Each project is shown as a bar in €/MWh so mixed kW/MW models stay comparable.',
    ],
  },
  {
    version: 'v0.0.0.0.4',
    date: '2026-08-25',
    type: 'feature',
    title: 'Version history in the Docs tab',
    notes: [
      'Added a Versions tab in documentation. Each change, feature, or bugfix gets its own version panel.',
      'Version numbers follow vX.X.X.X.X, with the latest shown as the current version.',
    ],
  },
  {
    version: 'v0.0.0.0.3',
    date: '2026-08-25',
    type: 'feature',
    title: 'Grid sell and curtailment on demand timeseries',
    notes: [
      'Processes that consume a demand commodity (Grid Sell, Curtailpower, and similar sinks) now appear as negative bars on the site timeseries.',
      'They sit below the axis together with storage charging and exports, while generation stays positive.',
      'Re-run the simulation so the optimizer includes consumed-process timeseries in the result.',
    ],
  },
  {
    version: 'v0.0.0.0.2',
    date: '2026-08-25',
    type: 'change',
    title: 'Six decimal places for price and cost inputs',
    notes: [
      'Investment, fixed, and variable costs now accept up to 6 decimal places on process, storage, and transmission forms.',
      'Commodity price uses the same precision.',
    ],
  },
  {
    version: 'v0.0.0.0.1',
    date: '2026-08-25',
    type: 'bugfix',
    title: 'Capacity units follow the commodity, not hardcoded MW',
    notes: [
      'Process capacity on the results page used a hardcoded MW label even when Elec and Solar were in kW/kWh.',
      'Capacity, demand, production, and storage now convert from the commodity unit to the selected display unit (kW or MW).',
      'If electricity is configured in kW, results open in kW so solar build and peak demand share the same scale.',
    ],
  },
]

const currentVersion = computed(() => versions[0]?.version ?? 'v0.0.0.0.0')

function versionTypeClass(type: VersionType) {
  if (type === 'feature') return 'bg-green-100 text-green-800'
  if (type === 'bugfix') return 'bg-red-100 text-red-800'
  return 'bg-blue-100 text-blue-800'
}

function closeDialog() {
  visible.value = false
}
</script>

<style scoped>
.documentation-content {
  max-height: 70vh;
  overflow-y: auto;
}

.tab-content {
  padding: 1rem 0;
}

.step-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.step-number {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.step-content {
  flex: 1;
}

.feature-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border-left: 3px solid #e2e8f0;
}

.feature-category {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
}

.config-section {
  background: white;
  padding: 1.5rem;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
}

.architecture-section {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
}

.version-entry {
  background: #f8fafc;
  padding: 1.25rem;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  margin-top: 0.75rem;
}

code {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}
</style>
