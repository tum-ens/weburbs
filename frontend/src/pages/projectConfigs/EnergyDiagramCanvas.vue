<template>
  <div class="energy-diagram-container">
    <!-- Map Section -->
    <Card class="mb-4">
      <template #title>Sites Map</template>
      <template #content>
        <!-- Real Interactive Map -->
        <div ref="mapContainerRef" class="map-container h-96 relative">
          <!-- Loading overlay -->
          <div
            v-if="mapLoading"
            class="absolute inset-0 bg-gray-100 bg-opacity-75 flex items-center justify-center z-10"
          >
            <div class="text-center">
              <i class="pi pi-spin pi-spinner text-2xl text-blue-600 mb-2"></i>
              <p class="text-gray-600">Loading map...</p>
            </div>
          </div>

          <!-- Error overlay -->
          <div
            v-if="mapError"
            class="absolute inset-0 bg-red-50 border-2 border-red-200 rounded-lg flex items-center justify-center z-10"
          >
            <div class="text-center">
              <i
                class="pi pi-exclamation-triangle text-2xl text-red-600 mb-2"
              ></i>
              <p class="text-red-600 mb-2">Map failed to load</p>
              <Button @click="retryMap" size="small" severity="secondary"
                >Retry</Button
              >
            </div>
          </div>

          <l-map
            @click="onMapClick"
            @ready="onMapReady"
            @error="onMapError"
            :zoom="mapZoom"
            :use-global-leaflet="false"
            :center="mapCenter"
            :bounds="mapBounds"
            :bounds-options="{ padding: [10, 10], maxZoom: 15 }"
          >
            <l-tile-layer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              layer-type="base"
              name="OpenStreetMap"
              :options="{
                maxZoom: 19,
                attribution: '© OpenStreetMap contributors',
                crossOrigin: true,
              }"
            />
            <l-marker
              v-for="site in sites"
              :key="site.name"
              :lat-lng="[site.lat, site.lon]"
              @click="selectSite(site)"
              :class="{ 'selected-site': selectedSite?.name === site.name }"
            >
              <l-popup>
                <div class="text-center">
                  <h3 class="font-bold">{{ site.name }}</h3>
                  <p class="text-sm text-gray-600">
                    Lat: {{ site.lat }}, Lon: {{ site.lon }}
                  </p>
                </div>
              </l-popup>
            </l-marker>

            <!-- Transmission lines between sites -->
            <l-polyline
              v-for="transmission in transmissions"
              :key="`${transmission.sitein}-${transmission.siteout}-${transmission.commodity}`"
              :lat-lngs="getTransmissionCoordinates(transmission)"
              :color="'orange'"
              :weight="3"
              :opacity="0.7"
              :dash-array="'10,5'"
            />
          </l-map>
        </div>
      </template>
    </Card>

    <!-- Energy Diagram Canvas -->
    <Card v-if="selectedSite" class="mb-4">
      <template #title>
        Energy System Diagram - {{ selectedSite.name }}
        <Button icon="pi pi-times" text @click="closeCanvas" class="ml-auto" />
      </template>
      <template #content>
        <div class="canvas-container">
          <!-- Toolbar -->
          <div class="toolbar mb-4 p-2 bg-gray-50 rounded-lg">
            <div class="flex items-center gap-4">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium">Add Elements:</span>
                <Button
                  icon="pi pi-plus"
                  size="small"
                  @click="addCommodity"
                  class="bg-blue-500 hover:bg-blue-600 min-w-32 px-4"
                >
                  Commodity
                </Button>
                <Button
                  icon="pi pi-plus"
                  size="small"
                  @click="addProcess"
                  class="bg-green-500 hover:bg-green-600 min-w-32 px-4"
                >
                  Process
                </Button>
                <Button
                  icon="pi pi-plus"
                  size="small"
                  @click="addStorage"
                  class="bg-yellow-500 hover:bg-yellow-600 min-w-32 px-4"
                >
                  Storage
                </Button>
              </div>
            </div>
          </div>

          <!-- Instructions and Legend -->
          <div class="flex gap-4 mb-4">
            <!-- Instructions -->
            <div class="instructions flex-1 p-3 bg-blue-50 rounded-lg">
              <h4 class="font-medium text-blue-800 mb-2">How to Use</h4>
              <p class="text-sm text-blue-700">
                Click on any element (commodity, process, or storage) to edit
                its parameters in the dedicated form. Use the "Add Elements"
                buttons to create new components.
              </p>
            </div>
            <!-- Site Statistics -->
            <div class="statistics flex-1 p-2 bg-green-50 rounded-lg">
              <h4 class="font-medium text-green-800 mb-2">Site Statistics</h4>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div class="text-center">
                  <div class="text-2xl font-bold text-green-600">
                    {{ commodities?.length || 0 }}
                  </div>
                  <div class="text-green-700">Commodities</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-green-600">
                    {{ processes?.length || 0 }}
                  </div>
                  <div class="text-green-700">Processes</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-green-600">
                    {{ storage?.length || 0 }}
                  </div>
                  <div class="text-green-700">Storage Units</div>
                </div>
              </div>
            </div>

            <!-- Legend -->
            <div class="legend flex-1 p-3 bg-gray-50 rounded-lg">
              <h4 class="font-medium text-gray-800 mb-2">Diagram Legend</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div class="flex items-center gap-2">
                  <div class="w-4 h-4 bg-blue-500 rounded"></div>
                  <span>Commodities (Vertical Lines)</span>
                </div>
                <div class="flex items-center gap-2">
                  <div class="w-4 h-4 bg-green-500 rounded"></div>
                  <span>Processes (Boxes)</span>
                </div>
                <div class="flex items-center gap-2">
                  <div
                    class="w-4 h-4 bg-yellow-200 border-2 border-yellow-600 rounded-lg relative"
                  >
                    <div
                      class="w-4 h-1 bg-yellow-200 border-2 border-yellow-600 rounded-full absolute -top-0.5 left-0"
                    ></div>
                  </div>
                  <span>Storage (Cylinders)</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Diagram window: fixed-height viewport that scrolls when the diagram is large -->
          <div class="diagram-window">
            <div
              ref="canvasRef"
              class="canvas bg-white relative"
              :style="`width: ${calculateCanvasWidth()}px; height: ${calculateCanvasHeight()}px;`"
              @click="deselectAll"
            >
              <!-- Commodities (Vertical Lines) -->
              <div
                v-for="commodity in diagramData.commodities"
                :key="commodity.id"
                class="commodity absolute cursor-pointer"
                :style="{
                  left: commodity.x + 'px',
                  top: '40px',
                  width: '4px',
                  height: 'calc(100% - 80px)',
                }"
                :class="{ selected: selectedElement?.id === commodity.id }"
                @click.stop="selectElement(commodity)"
              >
                <div
                  class="commodity-label absolute -top-8 -left-2 bg-blue-500 text-white px-2 py-1 rounded text-xs whitespace-nowrap"
                  :style="{ left: '0px' }"
                >
                  {{ commodity.name }}
                </div>
              </div>

              <!-- Processes (Horizontal Boxes) -->
              <div
                v-for="process in diagramData.processes"
                :key="process.id"
                class="process absolute cursor-pointer bg-green-500 text-white p-2 rounded text-xs text-center"
                :style="{
                  left: process.x + 'px',
                  top: process.y + 'px',
                  width: process.width + 'px',
                  height: process.height + 'px',
                }"
                :class="{ selected: selectedElement?.id === process.id }"
                @click.stop="selectElement(process)"
              >
                {{ process.name }}
              </div>

              <!-- Storage (Cylindrical) -->
              <div
                v-for="storage in diagramData.storage"
                :key="storage.id"
                class="storage absolute cursor-pointer"
                :style="{
                  left: storage.x + 'px',
                  top: storage.y + 'px',
                }"
                :class="{ selected: selectedElement?.id === storage.id }"
                @click.stop="selectElement(storage)"
              >
                <!-- Cylinder body -->
                <div
                  class="storage-cylinder w-12 h-16 bg-yellow-200 border-2 border-yellow-600 rounded-lg relative"
                >
                  <!-- Oval top -->
                  <div
                    class="storage-top w-12 h-3 bg-yellow-200 border-2 border-yellow-600 rounded-full absolute -top-1.5 left-0"
                  ></div>
                  <!-- Storage label -->
                  <div
                    class="storage-label absolute -top-8 left-1/2 transform -translate-x-1/2 bg-yellow-600 text-white px-2 py-1 rounded text-xs whitespace-nowrap border border-yellow-700"
                  >
                    {{ storage.name }}
                  </div>
                </div>
              </div>

              <!-- Connection Lines -->
              <svg
                v-for="connection in diagramData.connections"
                :key="connection.id"
                class="connection absolute pointer-events-none"
                style="left: 0px; top: 0px; width: 100%; height: 100%"
              >
                <line
                  :x1="connection.x1"
                  :y1="connection.y1"
                  :x2="connection.x2"
                  :y2="connection.y2"
                  :stroke="connection.strokeColor"
                  :stroke-width="connection.strokeWidth"
                />
                <!-- For storage connections that need a vertical then horizontal line -->
                <line
                  v-if="connection.x3 !== undefined"
                  :x1="connection.x2"
                  :y1="connection.y2"
                  :x2="connection.x3"
                  :y2="connection.y3"
                  stroke="gray"
                  stroke-width="2"
                />
              </svg>
            </div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  LMap,
  LMarker,
  LTileLayer,
  LPopup,
  LPolyline,
} from '@vue-leaflet/vue-leaflet'
import 'leaflet/dist/leaflet.css'
import { useSites } from '@/backend/sites'
import { useProjectSiteCommodities } from '@/backend/commodities'
import { useTransmission } from '@/backend/transmission'

import { useQuery } from '@tanstack/vue-query'
import axios from 'axios'
import type { Map as LeafletMap } from 'leaflet'
import type { Site, Commodity, Process, Storage } from '@/backend/interfaces'

const route = useRoute()
const router = useRouter()
const canvasRef = ref<HTMLElement>()
const isMounted = ref(false)
const selectedSite = ref<Site | null>(null)
const selectedElement = ref<DiagramElement | null>(null)
const mapLoading = ref(true)
const mapError = ref(false)

// Data fetching
const { data: sites } = useSites(route)
const { data: commodities } = useProjectSiteCommodities(
  route,
  computed(() => selectedSite.value?.name),
)
const { data: processes } = useQuery({
  queryKey: [
    'processes',
    computed(() => route.params.proj),
    computed(() => selectedSite.value?.name),
  ],
  queryFn: () => {
    if (!selectedSite.value?.name) return []
    return axios
      .get<
        Process[]
      >(`/api/project/${route.params.proj}/site/${selectedSite.value.name}/processes/`)
      .then(response => response.data)
  },
  enabled: computed(() => !!selectedSite.value?.name),
})
const { data: storage } = useQuery({
  queryKey: [
    'storage',
    computed(() => route.params.proj),
    computed(() => selectedSite.value?.name),
  ],
  queryFn: () => {
    if (!selectedSite.value?.name) return []
    return axios
      .get<
        Storage[]
      >(`/api/project/${route.params.proj}/site/${selectedSite.value.name}/storage/`)
      .then(response => response.data)
  },
  enabled: computed(() => !!selectedSite.value?.name),
})

const { data: transmissions } = useTransmission(route)

// Diagram data structure
interface DiagramConnection {
  id: string
  x1: number
  y1: number
  x2: number
  y2: number
  type: string
  strokeWidth?: number
  strokeColor?: string
  inputIndex?: number
  outputIndex?: number
  x3?: number
  y3?: number
}

interface DiagramElement {
  id: string
  name: string
  x: number
  y?: number
  width?: number
  height?: number
  type: 'commodity' | 'process' | 'storage'
  data: Commodity | Process | Storage
}

interface DiagramData {
  commodities: DiagramElement[]
  processes: DiagramElement[]
  storage: DiagramElement[]
  connections: DiagramConnection[]
}

const diagramData = ref<DiagramData>({
  commodities: [],
  processes: [],
  storage: [],
  connections: [],
})

// Map zoom and bounds computed properties
const mapZoom = computed(() => {
  if (!sites.value || sites.value.length === 0) return 6 // Good default zoom
  if (sites.value.length === 1) return 10 // Close zoom for single site
  return undefined // Let bounds handle zoom for multiple sites
})

const mapCenter = computed(() => {
  if (!sites.value || sites.value.length === 0)
    return [47.41322, -1.219482] as [number, number] // Default center

  if (sites.value.length === 1) {
    return [sites.value[0].lat, sites.value[0].lon] as [number, number]
  }

  // Calculate center point for multiple sites
  const totalLat = sites.value.reduce((sum, site) => sum + site.lat, 0)
  const totalLon = sites.value.reduce((sum, site) => sum + site.lon, 0)
  return [totalLat / sites.value.length, totalLon / sites.value.length] as [
    number,
    number,
  ]
})

const mapBounds = computed(() => {
  if (!sites.value || sites.value.length <= 1) return undefined

  // Calculate bounds to include all sites - farthest sites will be at edges
  const lats = sites.value.map(site => site.lat)
  const lons = sites.value.map(site => site.lon)

  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  const minLon = Math.min(...lons)
  const maxLon = Math.max(...lons)

  // Add minimal padding to ensure sites are visible at edges
  const latPadding = (maxLat - minLat) * 0.05 // 5% padding
  const lonPadding = (maxLon - minLon) * 0.05 // 5% padding

  return [
    [minLat - latPadding, minLon - lonPadding],
    [maxLat + latPadding, maxLon + lonPadding],
  ]
})

// Helper function to get coordinates for transmission lines
const getTransmissionCoordinates = (transmission: {
  sitein: string
  siteout: string
}) => {
  const siteIn = sites.value?.find(s => s.name === transmission.sitein)
  const siteOut = sites.value?.find(s => s.name === transmission.siteout)

  if (siteIn && siteOut) {
    return [
      [siteIn.lat, siteIn.lon] as [number, number],
      [siteOut.lat, siteOut.lon] as [number, number],
    ]
  }
  return [] as [number, number][]
}

// Map event handlers
let leafletMap: LeafletMap | null = null
const mapContainerRef = ref<HTMLElement>()
let mapResizeObserver: ResizeObserver | null = null

// Leaflet caches its container size at init time. After in-app (SPA) navigation the
// container often isn't at its final size yet (lazy route chunk + layout still settling),
// so the map renders blank/gray until a manual refresh. We re-measure repeatedly until
// the container has a real size, and also observe future size changes.
const invalidateMap = () => leafletMap?.invalidateSize()

const refreshMapSize = () => {
  // Staged retries cover the cold first-load case where the container only gets its
  // final height a few frames after the map reports "ready".
  ;[0, 100, 300, 600, 1000, 1500].forEach(delay => {
    setTimeout(() => nextTick(invalidateMap), delay)
  })
}

const onMapReady = (mapObject: LeafletMap) => {
  console.log('Map loaded successfully')
  leafletMap = mapObject
  mapLoading.value = false
  mapError.value = false
  refreshMapSize()

  // Keep the map in sync with any later size changes of its container.
  if (
    mapContainerRef.value &&
    'ResizeObserver' in window &&
    !mapResizeObserver
  ) {
    mapResizeObserver = new ResizeObserver(() => invalidateMap())
    mapResizeObserver.observe(mapContainerRef.value)
  }
}

const handleWindowResize = () => invalidateMap()

// Set a timeout to handle slow map loading
onMounted(() => {
  window.addEventListener('resize', handleWindowResize)

  setTimeout(() => {
    if (mapLoading.value) {
      console.warn('Map loading timeout - switching to fallback')
      mapLoading.value = false
      // The fallback tile layer will be used automatically
    }
  }, 10000) // 10 second timeout
})

onUnmounted(() => {
  window.removeEventListener('resize', handleWindowResize)
  mapResizeObserver?.disconnect()
  mapResizeObserver = null
})

const onMapError = (error: unknown) => {
  console.error('Map loading error:', error)
  mapLoading.value = false
  mapError.value = true
}

const retryMap = () => {
  mapError.value = false
  mapLoading.value = true
  // Force map re-render by updating a reactive property
  nextTick(() => {
    // The map will re-initialize
  })
}

function findCommodityForStorage(stor: Storage) {
  const name = stor.commodity?.trim()
  if (name) {
    const exact = diagramData.value.commodities.find(c => c.name === name)
    if (exact) return exact
    const lower = name.toLowerCase()
    const fuzzy = diagramData.value.commodities.find(
      c => c.name.toLowerCase() === lower,
    )
    if (fuzzy) return fuzzy
  }
  return undefined
}

const STORAGE_BODY_W = 48
const STORAGE_BODY_H = 64
const STORAGE_LABEL_H = 32
const STORAGE_PAD = 14

function rectsOverlap(
  a: { left: number; right: number; top: number; bottom: number },
  b: { left: number; right: number; top: number; bottom: number },
) {
  return (
    a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top
  )
}

function storageBounds(x: number, y: number, name: string) {
  const labelW = Math.max(STORAGE_BODY_W, name.length * 7 + 20)
  return {
    left: x + STORAGE_BODY_W / 2 - labelW / 2 - STORAGE_PAD,
    right: x + STORAGE_BODY_W / 2 + labelW / 2 + STORAGE_PAD,
    top: y - STORAGE_LABEL_H - STORAGE_PAD,
    bottom: y + STORAGE_BODY_H + STORAGE_PAD,
  }
}

function processBounds(p: {
  x?: number
  y?: number
  width?: number
  height?: number
  name?: string
}) {
  const width = p.width || 120
  const height = p.height || 40
  const labelW = Math.max(width, (p.name?.length || 0) * 7)
  return {
    left: Math.min(p.x || 0, (p.x || 0) + width / 2 - labelW / 2) - 8,
    right:
      Math.max((p.x || 0) + width, (p.x || 0) + width / 2 + labelW / 2) + 8,
    top: (p.y || 0) - 8,
    bottom: (p.y || 0) + height + 8,
  }
}

// Initialize diagram data when site is selected
const initializeDiagramData = async () => {
  if (!selectedSite.value) return

  await nextTick()

  // Wait for data to be loaded
  if (!commodities.value || !processes.value || !storage.value) {
    console.log('Waiting for data to load...')
    return
  }

  console.log('Initializing diagram with:', {
    commodities: commodities.value,
    processes: processes.value,
    storage: storage.value,
  })

  // First, analyze the process flow to determine commodity positions
  const inputCommodities = new Map<string, number>()
  const outputCommodities = new Map<string, number>()

  // Count input and output usage for each commodity
  processes.value?.forEach(process => {
    if (process.in) {
      process.in.forEach(input => {
        inputCommodities.set(
          input.name,
          (inputCommodities.get(input.name) || 0) + 1,
        )
      })
    }
    if (process.out) {
      process.out.forEach(output => {
        outputCommodities.set(
          output.name,
          (outputCommodities.get(output.name) || 0) + 1,
        )
      })
    }
  })

  // Create a directed graph to represent commodity dependencies
  const commodityGraph = new Map<string, Set<string>>()
  const commodityInDegree = new Map<string, number>()

  // Initialize the graph
  commodities.value?.forEach(com => {
    commodityGraph.set(com.name, new Set())
    commodityInDegree.set(com.name, 0)
  })

  // Build the dependency graph based on process connections
  processes.value?.forEach(process => {
    if (process.in && process.out) {
      // For each process, create edges from inputs to outputs
      process.in.forEach(input => {
        process.out.forEach(output => {
          if (input.name !== output.name) {
            // Add edge: input -> output (input must come before output)
            commodityGraph.get(input.name)?.add(output.name)
            commodityInDegree.set(
              output.name,
              (commodityInDegree.get(output.name) || 0) + 1,
            )
          }
        })
      })
    }
  })

  // Topological sort to ensure left-to-right flow
  const sortedCommodities: typeof commodities.value = []
  const queue: string[] = []

  // Add commodities with no incoming edges (pure inputs) to the queue
  commodityInDegree.forEach((inDegree, commodityName) => {
    if (inDegree === 0) {
      queue.push(commodityName)
    }
  })

  // Process the queue
  while (queue.length > 0) {
    // Sort queue alphabetically for consistent ordering when multiple options exist
    queue.sort()

    const currentCommodity = queue.shift()!
    const commodity = commodities.value?.find(c => c.name === currentCommodity)
    if (commodity) {
      sortedCommodities.push(commodity)
    }

    // Remove edges from current commodity and update in-degrees
    const neighbors = commodityGraph.get(currentCommodity) || new Set()
    neighbors.forEach(neighbor => {
      const currentInDegree = commodityInDegree.get(neighbor) || 0
      commodityInDegree.set(neighbor, currentInDegree - 1)

      // If in-degree becomes 0, add to queue
      if (currentInDegree - 1 === 0) {
        queue.push(neighbor)
      }
    })
  }

  // Handle any remaining commodities (cycles or isolated nodes)
  const remainingCommodities =
    commodities.value?.filter(
      com => !sortedCommodities.find(sorted => sorted.name === com.name),
    ) || []

  if (remainingCommodities.length > 0) {
    console.warn(
      'Detected cycles or isolated nodes in commodity dependencies:',
      remainingCommodities.map(c => c.name),
    )

    // Try to resolve cycles by breaking them at the process level
    remainingCommodities.forEach(com => {
      // Find processes that use this commodity as both input and output
      const conflictingProcesses =
        processes.value?.filter(p => {
          const isInput = p.in?.some(input => input.name === com.name)
          const isOutput = p.out?.some(output => output.name === com.name)
          return isInput && isOutput
        }) || []

      if (conflictingProcesses.length > 0) {
        console.warn(
          `Commodity ${com.name} is used as both input and output in processes:`,
          conflictingProcesses.map(p => p.name),
        )
      }

      // Add to the end of the sorted list (this will be the rightmost position)
      sortedCommodities.push(com)
    })
  }

  console.log(
    'Final commodity ordering for left-to-right flow:',
    sortedCommodities.map(c => c.name),
  )
  console.log('Dependency graph:', Object.fromEntries(commodityGraph))

  // Validate that the ordering maintains left-to-right flow
  const validationErrors: string[] = []
  processes.value?.forEach(process => {
    if (process.in && process.out) {
      const inputIndices = process.in.map(input =>
        sortedCommodities.findIndex(c => c.name === input.name),
      )
      const outputIndices = process.out.map(output =>
        sortedCommodities.findIndex(c => c.name === output.name),
      )

      const maxInputIndex = Math.max(...inputIndices)
      const minOutputIndex = Math.min(...outputIndices)

      if (maxInputIndex >= minOutputIndex) {
        validationErrors.push(
          `Process ${process.name}: Inputs at indices ${inputIndices} should be to the left of outputs at indices ${outputIndices}`,
        )
      }
    }
  })

  if (validationErrors.length > 0) {
    console.error('Commodity ordering validation failed:', validationErrors)
  } else {
    console.log(
      '✅ Commodity ordering successfully maintains left-to-right flow',
    )
  }

  console.log(
    'Commodity layout:',
    sortedCommodities.map(name => {
      const inputCount = inputCommodities.get(name.name) || 0
      const outputCount = outputCommodities.get(name.name) || 0
      const netUsage = inputCount - outputCount
      return {
        name: name.name,
        inputCount: inputCount,
        outputCount: outputCount,
        netUsage: netUsage,
        type: name.type,
      }
    }),
  )

  // Shared layout constants
  const processWidth = 120
  const processHeight = 40
  const positioningMargin = 40 // horizontal gap kept between a process box and a commodity line
  const leftBound = 60 // inside site boundary
  // Width of the single commodity gap a process must fit in without touching either line.
  const minProcessGap = processWidth + positioningMargin * 2

  // Initialize commodities with even base spacing, then relax positions so that every
  // process can sit inside a single commodity gap without ever overlapping a commodity line.
  // Each process lives in exactly one gap:
  //  - if it has outputs, the gap immediately to the LEFT of its leftmost output line
  //  - otherwise, the gap immediately to the RIGHT of its rightmost input line
  const startX = 120
  const baseGap = 100

  const commodityIndex = new Map<string, number>()
  sortedCommodities.forEach((c, i) => commodityIndex.set(c.name, i))

  const commodityXs = sortedCommodities.map((_, i) => startX + i * baseGap)

  // Widen the hosting gap (and shift everything to its right) until the process fits cleanly.
  const widenGap = (rightIndex: number) => {
    // Position of the commodity line bordering the gap on the left (or the canvas edge).
    const leftEdge = rightIndex > 0 ? commodityXs[rightIndex - 1] : leftBound
    const deficit = minProcessGap - (commodityXs[rightIndex] - leftEdge)
    if (deficit > 0) {
      const from = rightIndex > 0 ? rightIndex : 0
      for (let k = from; k < commodityXs.length; k++) {
        commodityXs[k] += deficit
      }
      return true
    }
    return false
  }

  for (let iter = 0; iter <= sortedCommodities.length; iter++) {
    let changed = false

    processes.value?.forEach(p => {
      const inIdx = (p.in || [])
        .map(i => commodityIndex.get(i.name))
        .filter((v): v is number => v !== undefined)
      const outIdx = (p.out || [])
        .map(o => commodityIndex.get(o.name))
        .filter((v): v is number => v !== undefined)

      if (outIdx.length) {
        // Gap to the left of the leftmost output line.
        const leftmostOutput = Math.min(...outIdx)
        if (widenGap(leftmostOutput)) changed = true
      } else if (inIdx.length) {
        // Gap to the right of the rightmost input line (only if there is a line to the right).
        const rightmostInput = Math.max(...inIdx)
        if (
          rightmostInput + 1 < commodityXs.length &&
          widenGap(rightmostInput + 1)
        ) {
          changed = true
        }
      }
    })

    if (!changed) break
  }

  diagramData.value.commodities = sortedCommodities.map((com, index) => ({
    id: `commodity-${com.name}`,
    name: com.name,
    x: commodityXs[index],
    y: 30, // All commodities at same height
    type: 'commodity' as const,
    data: com,
  }))

  // Position processes dynamically between their input and output commodities
  const processPositions = new Map<string, { x: number; y: number }>()

  // Track used Y positions to avoid horizontal alignment
  // const usedYPositions = new Set<number>() // Removed duplicate declaration

  // Group processes by their X position ranges to ensure proper vertical spacing
  const processGroups: {
    xRange: [number, number]
    processes: { process: Process; desiredX: number; desiredY: number }[]
  }[] = []

  processes.value?.forEach(process => {
    const inputComEls = (process.in || [])
      .map(i => diagramData.value.commodities.find(c => c.name === i.name))
      .filter(Boolean) as { x: number; y?: number }[]
    const outputComEls = (process.out || [])
      .map(o => diagramData.value.commodities.find(c => c.name === o.name))
      .filter(Boolean) as { x: number; y?: number }[]

    let desiredX: number | undefined

    // Each process is placed inside a single commodity gap, never on top of a commodity line.
    // The gap was guaranteed wide enough by the relaxation pass above.
    if (outputComEls.length) {
      // Sit just to the left of the leftmost output line (inside the gap left of it).
      const leftmostOutputX = Math.min(...outputComEls.map(c => c.x))
      desiredX = leftmostOutputX - processWidth - positioningMargin
    } else if (inputComEls.length) {
      // Sit just to the right of the rightmost input line.
      const rightmostInputX = Math.max(...inputComEls.map(c => c.x))
      desiredX = rightmostInputX + positioningMargin
    }

    // Keep the process inside the left site boundary. The right side is allowed to grow
    // because the canvas width is derived from commodity positions (see calculateCanvasWidth).
    if (desiredX !== undefined) {
      desiredX = Math.max(desiredX, leftBound)
    }

    // Group processes by X position ranges (within 50px = same vertical column)
    let addedToGroup = false
    for (const group of processGroups) {
      if (
        desiredX &&
        desiredX >= group.xRange[0] &&
        desiredX <= group.xRange[1]
      ) {
        group.processes.push({ process, desiredX, desiredY: 0 })
        addedToGroup = true
        break
      }
    }

    if (!addedToGroup && desiredX !== undefined) {
      processGroups.push({
        xRange: [desiredX - 25, desiredX + 25],
        processes: [{ process, desiredX, desiredY: 0 }],
      })
    }

    // Store initial position
    if (desiredX !== undefined) {
      processPositions.set(process.name, { x: desiredX, y: 0 }) // Y will be calculated after grouping
    } else {
      processPositions.set(process.name, { x: 400, y: 0 })
    }
  })

  // Calculate Y positions for each group with proper margins
  processGroups.forEach(group => {
    const sortedProcesses = group.processes.sort((a, b) => {
      // Sort by input commodity Y position for logical flow
      const aInputY = a.process.in?.[0]
        ? diagramData.value.commodities.find(
            c => c.name === a.process.in[0].name,
          )?.y || 0
        : 0
      const bInputY = b.process.in?.[0]
        ? diagramData.value.commodities.find(
            c => c.name === b.process.in[0].name,
          )?.y || 0
        : 0
      return aInputY - bInputY
    })

    const minMargin = 60 // Reduced margin to keep processes closer together
    let currentY = 40 // Start much closer to the top

    sortedProcesses.forEach((procInfo, index) => {
      // Calculate ideal Y based on connected commodities
      const inputComEls = (procInfo.process.in || [])
        .map(i => diagramData.value.commodities.find(c => c.name === i.name))
        .filter(Boolean) as { x: number; y?: number }[]
      const outputComEls = (procInfo.process.out || [])
        .map(o => diagramData.value.commodities.find(c => c.name === o.name))
        .filter(Boolean) as { x: number; y?: number }[]

      const yValues: number[] = []
      inputComEls.forEach(c => {
        if (c.y !== undefined) yValues.push(c.y + 20)
      })
      outputComEls.forEach(c => {
        if (c.y !== undefined) yValues.push(c.y + 20)
      })

      let idealY = yValues.length
        ? Math.round(yValues.reduce((a, b) => a + b, 0) / yValues.length)
        : currentY

      // Ensure minimum margin from previous process in same column
      if (index > 0) {
        const prevProcess = sortedProcesses[index - 1]
        const prevY = processPositions.get(prevProcess.process.name)?.y || 0
        const minY = prevY + processHeight + minMargin
        idealY = Math.max(idealY, minY)
      }

      // Update process position
      processPositions.set(procInfo.process.name, {
        x: procInfo.desiredX,
        y: idealY,
      })

      currentY = idealY + processHeight + minMargin
    })
  })

  // Force vertical separation for processes that are too close horizontally
  const finalProcessPositions = new Map<string, { x: number; y: number }>()
  const usedYPositions = new Set<number>()

  // Sort processes by X position to process them in order
  const sortedProcesses = Array.from(processPositions.entries()).sort(
    (a, b) => a[1].x - b[1].x,
  )

  sortedProcesses.forEach(([processName, position]) => {
    let finalY = position.y

    // Check if this process is too close horizontally to previous processes
    const horizontalThreshold = 150 // Increased threshold to force more vertical separation

    for (const [, existingPos] of finalProcessPositions) {
      if (Math.abs(position.x - existingPos.x) < horizontalThreshold) {
        // Force vertical separation with larger margin
        const minY = existingPos.y + processHeight + 120
        finalY = Math.max(finalY, minY)
      }
    }

    // Ensure no Y position conflicts
    while (usedYPositions.has(finalY)) {
      finalY += 60
    }

    usedYPositions.add(finalY)
    finalProcessPositions.set(processName, { x: position.x, y: finalY })
  })

  // Update process positions with final calculated positions
  finalProcessPositions.forEach((pos, processName) => {
    processPositions.set(processName, pos)
  })

  // Initialize processes with dynamic positioning
  diagramData.value.processes = (processes.value || []).map((proc, index) => {
    const position = processPositions.get(proc.name)
    const finalX = position ? position.x : 400
    let finalY = position ? position.y : 150 + index * 120

    // Check for collisions with commodities and adjust if needed
    const processBounds = {
      left: finalX,
      right: finalX + processWidth,
      top: finalY,
      bottom: finalY + processHeight,
    }

    // Check collision with commodities
    diagramData.value.commodities.forEach(commodity => {
      const commodityBounds = {
        left: commodity.x - 20, // Add some buffer
        right: commodity.x + 20,
        top: (commodity.y || 0) - 20,
        bottom: (commodity.y || 0) + 120, // Commodity height
      }

      // If collision detected, move process down
      if (
        processBounds.left < commodityBounds.right &&
        processBounds.right > commodityBounds.left &&
        processBounds.top < commodityBounds.bottom &&
        processBounds.bottom > commodityBounds.top
      ) {
        finalY = commodityBounds.bottom + 20
        processBounds.top = finalY
        processBounds.bottom = finalY + processHeight
      }
    })

    return {
      id: `process-${proc.name}`,
      name: proc.name,
      x: finalX,
      y: finalY,
      width: processWidth,
      height: processHeight,
      type: 'process',
      data: proc,
    }
  })

  // Initialize storage on the commodity selected in the storage form,
  // then drop it below any process that occupies the same column.
  const siteStorage = storage.value || []
  const placedStorage: { x: number; y: number; name: string }[] = []

  diagramData.value.storage = siteStorage.map((stor, index) => {
    const targetCommodity = findCommodityForStorage(stor)

    if (!targetCommodity) {
      const fallback = {
        id: `storage-${stor.name}`,
        name: stor.name,
        x: 800,
        y: 300 + index * 80,
        type: 'storage' as const,
        data: stor,
      }
      placedStorage.push(fallback)
      return fallback
    }

    const storageX = targetCommodity.x + 60
    const occupied = [
      ...diagramData.value.processes.map(p => processBounds(p)),
      ...placedStorage.map(s => storageBounds(s.x, s.y, s.name)),
    ]

    const candidate = storageBounds(storageX, 0, stor.name)
    const blocking = occupied.filter(
      rect => rect.left < candidate.right && rect.right > candidate.left,
    )
    let storageY = blocking.length
      ? Math.max(...blocking.map(rect => rect.bottom)) + STORAGE_LABEL_H + 16
      : 110

    // Safety scan in case two items still collide after the column drop
    for (let step = 0; step < 80; step++) {
      const next = storageBounds(storageX, storageY, stor.name)
      if (!occupied.some(rect => rectsOverlap(next, rect))) break
      storageY += 16
    }

    const placed = {
      id: `storage-${stor.name}`,
      name: stor.name,
      x: storageX,
      y: storageY,
      type: 'storage' as const,
      data: stor,
    }
    placedStorage.push(placed)
    return placed
  })

  // Generate connections
  generateConnections()

  console.log('Diagram initialized:', diagramData.value)
}

// Calculate canvas height so it always encloses every positioned element
const calculateCanvasHeight = () => {
  const bottomPadding = 80
  let maxBottom = 600 // keep a comfortable minimum height

  diagramData.value.processes.forEach(p => {
    maxBottom = Math.max(maxBottom, (p.y || 0) + (p.height || 40))
  })
  diagramData.value.storage.forEach(s => {
    maxBottom = Math.max(maxBottom, (s.y || 0) + 80) // cylinder height
  })

  return maxBottom + bottomPadding
}

// Calculate canvas width based on actual commodity positions and spacing
const calculateCanvasWidth = () => {
  if (diagramData.value.commodities.length === 0) return 800

  // Find the rightmost commodity
  const rightmostCommodity = Math.max(
    ...diagramData.value.commodities.map(c => c.x),
  )

  // Add buffer for processes and storage that might be positioned beyond commodities
  const buffer = 300

  return Math.max(800, rightmostCommodity + buffer)
}

// Watch for data changes and reinitialize
watch(
  [commodities, processes, storage],
  () => {
    if (selectedSite.value) {
      console.log('Data changed, reinitializing diagram...')
      nextTick(() => {
        initializeDiagramData()
      })
    }
  },
  { deep: true },
)

const generateConnections = () => {
  diagramData.value.connections = []

  console.log('Generating connections for processes:', processes.value)

  // Connect processes to commodities based on input/output
  processes.value?.forEach(process => {
    console.log(
      'Processing process:',
      process.name,
      'with inputs:',
      process.in,
      'outputs:',
      process.out,
    )

    const processEl = diagramData.value.processes.find(
      p => p.name === process.name,
    )
    const yProc =
      processEl && processEl.y !== undefined ? processEl.y + 20 : undefined

    // Handle input connections (left side) - horizontal lines
    if (process.in && processEl && yProc !== undefined) {
      const inputCount = process.in.length
      process.in.forEach((input, inputIndex) => {
        const commodity = diagramData.value.commodities.find(
          c => c.name === input.name,
        )

        if (commodity && commodity.y !== undefined) {
          // Calculate parallel line offset for multiple inputs
          const lineOffset =
            inputCount > 1 ? (inputIndex - (inputCount - 1) / 2) * 12 : 0
          const yOffset = yProc + lineOffset

          // Create horizontal line from commodity to process left edge
          diagramData.value.connections.push({
            id: `conn-${process.name}-in-${input.name}`,
            x1: commodity.x + 2, // From center of commodity line (4px width, so center is at +2)
            y1: yOffset,
            x2: processEl.x, // To process left edge
            y2: yOffset, // Same Y level - horizontal line
            type: 'input', // Mark as input connection
            strokeWidth: 3, // Thicker line for inputs
            strokeColor: '#2563eb', // Blue color for inputs
            inputIndex: inputIndex, // Track input order
          })
          console.log(
            `Connected ${input.name} (input ${inputIndex + 1}) to ${process.name} at y=${yOffset}`,
          )
        }
      })
    }

    // Handle output connections (right side) - horizontal lines
    if (process.out && processEl && yProc !== undefined) {
      const outputCount = process.out.length
      process.out.forEach((output, outputIndex) => {
        const commodity = diagramData.value.commodities.find(
          c => c.name === output.name,
        )

        if (commodity && commodity.y !== undefined) {
          // Calculate parallel line offset for multiple outputs
          const lineOffset =
            outputCount > 1 ? (outputIndex - (outputCount - 1) / 2) * 12 : 0
          const yOffset = yProc + lineOffset

          // Create horizontal line from process right edge to commodity
          const procWidth = processEl.width ?? 120
          diagramData.value.connections.push({
            id: `conn-${process.name}-out-${output.name}`,
            x1: processEl.x + procWidth, // From process right edge
            y1: yOffset,
            x2: commodity.x + 2, // To center of commodity line (4px width, so center is at +2)
            y2: yOffset, // Same Y level - horizontal line
            type: 'output', // Mark as output connection
            strokeWidth: 2, // Normal line for outputs
            strokeColor: '#dc2626', // Red color for outputs
            outputIndex: outputIndex, // Track output order
          })
          console.log(
            `Connected ${process.name} (output ${outputIndex + 1}) to ${output.name} at y=${yOffset}`,
          )
        }
      })
    }
  })

  // Connect each storage to the commodity configured on that storage
  diagramData.value.storage.forEach(storageEl => {
    const targetCommodity = findCommodityForStorage(storageEl.data as Storage)

    if (targetCommodity && storageEl.y !== undefined) {
      const storageCenterY = storageEl.y + 8

      diagramData.value.connections.push({
        id: `conn-storage-${storageEl.name}-${targetCommodity.name}`,
        x1: targetCommodity.x + 2,
        y1: storageCenterY,
        x2: storageEl.x,
        y2: storageCenterY,
        type: 'storage',
        strokeWidth: 2,
        strokeColor: '#ca8a04',
      })
    }
  })

  console.log('Generated connections:', diagramData.value.connections)
}

// Event handlers
const selectSite = (site: Site) => {
  selectedSite.value = site
}

const openCanvas = (site: Site) => {
  selectedSite.value = site
  console.log('Opening canvas for site:', site.name)

  // Wait a bit for data to load, then initialize
  setTimeout(() => {
    if (commodities.value && processes.value && storage.value) {
      initializeDiagramData()
    } else {
      console.log('Data not ready yet, waiting...')
      // Try again after a short delay
      setTimeout(() => {
        initializeDiagramData()
      }, 500)
    }
  }, 100)
}

const closeCanvas = () => {
  selectedSite.value = null
  selectedElement.value = null
}

const onMapClick = () => {
  // Handle map clicks if needed
}

const selectElement = (element: DiagramElement) => {
  console.log('Element selected:', element)
  selectedElement.value = element
  // Automatically navigate to the edit form for the selected element
  navigateToEditForm(element)
}

const deselectAll = () => {
  selectedElement.value = null
}

// Navigate to the appropriate form for editing the selected element
const navigateToEditForm = (element: DiagramElement) => {
  const projectId = route.params.proj as string
  const siteName = selectedSite.value?.name

  console.log('Navigation attempt:', {
    projectId,
    siteName,
    elementType: element.type,
    elementName: element.name,
  })

  if (!projectId || !siteName) {
    console.error('Missing project ID or site name for navigation')
    return
  }

  // Navigate to the appropriate form based on element type with query parameters to auto-open edit dialog
  switch (element.type) {
    case 'commodity':
      router.push({
        name: 'ProjectCommodity',
        params: { proj: projectId },
        query: {
          site: siteName,
          edit: element.name,
          autoEdit: 'true',
          from: 'energy-diagram',
        },
      })
      break
    case 'process':
      router.push({
        name: 'ProjectProcess',
        params: { proj: projectId },
        query: {
          site: siteName,
          edit: element.name,
          autoEdit: 'true',
          from: 'energy-diagram',
        },
      })
      break
    case 'storage':
      router.push({
        name: 'ProjectStorage',
        params: { proj: projectId },
        query: {
          site: siteName,
          edit: element.name,
          autoEdit: 'true',
          from: 'energy-diagram',
        },
      })
      break

    default:
      console.warn('Unknown element type for navigation:', element.type)
      return
  }

  console.log('Navigated to edit form for:', element.name)
}

// Add new elements
const addCommodity = () => {
  const projectId = route.params.proj as string
  const siteName = selectedSite.value?.name

  if (!projectId || !siteName) {
    console.error('Missing project ID or site name for navigation')
    return
  }

  console.log('Navigating to create commodity form from energy diagram')
  router.push({
    name: 'ProjectCommodity',
    params: { proj: projectId },
    query: {
      site: siteName,
      create: 'true',
      from: 'energy-diagram',
    },
  })
}

const addProcess = () => {
  const projectId = route.params.proj as string
  const siteName = selectedSite.value?.name

  if (!projectId || !siteName) {
    console.error('Missing project ID or site name for navigation')
    return
  }

  console.log('Navigating to create process form from energy diagram')
  router.push({
    name: 'ProjectProcess',
    params: { proj: projectId },
    query: {
      site: siteName,
      create: 'true',
      from: 'energy-diagram',
    },
  })
}

const addStorage = () => {
  const projectId = route.params.proj as string
  const siteName = selectedSite.value?.name

  if (!projectId || !siteName) {
    console.error('Missing project ID or site name for navigation')
    return
  }

  console.log('Navigating to create storage form from energy diagram')
  router.push({
    name: 'ProjectStorage',
    params: { proj: projectId },
    query: {
      site: siteName,
      create: 'true',
      from: 'energy-diagram',
    },
  })
}

onMounted(() => {
  console.log('EnergyDiagramCanvas mounted!')
  console.log('Route params:', route.params)
  console.log('Initial sites data:', sites.value)

  isMounted.value = true
})

// Watch for site query parameter to auto-open diagram when returning from edit dialogs
watch(
  () => route.query.site,
  siteName => {
    if (siteName && sites.value) {
      const targetSite = sites.value.find(s => s.name === siteName)
      if (targetSite && !selectedSite.value) {
        console.log('Auto-opening energy diagram for site:', siteName)
        openCanvas(targetSite)
      }
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.energy-diagram-container {
  padding: 1rem;
}

.map-container {
  position: relative;
}

.canvas {
  position: relative;
}

.commodity {
  background: linear-gradient(to bottom, #3b82f6, #1d4ed8);
  border-radius: 2px;
  transition: all 0.2s ease;
}

.commodity:hover {
  background: linear-gradient(to bottom, #2563eb, #1e40af);
  transform: scaleX(1.2);
}

.commodity.selected {
  background: linear-gradient(to bottom, #f59e0b, #d97706);
  transform: scaleX(1.3);
}

.process {
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.process:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.process.selected {
  background-color: #f59e0b !important;
  transform: scale(1.1);
}

.storage {
  transition: all 0.2s ease;
}

.storage:hover {
  transform: scale(1.1);
}

.storage.selected .storage-cylinder {
  background-color: #f59e0b !important;
  border-color: #d97706 !important;
}

.storage-cylinder {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.storage-top {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.storage:hover .storage-cylinder {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.storage:hover .storage-top {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.connection {
  pointer-events: none;
}

.canvas {
  cursor: crosshair;
}

/* Fixed-height inline window that scrolls when the diagram is larger than the viewport */
.diagram-window {
  position: relative;
  width: 100%;
  height: 600px;
  overflow: auto;
  resize: vertical;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: #ffffff;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

.diagram-window::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.diagram-window::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.diagram-window::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.diagram-window::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.canvas-container {
  position: relative;
  width: 100%;
}

.canvas .commodity,
.canvas .process,
.canvas .storage {
  cursor: pointer;
}

.selected-site {
  z-index: 1000;
}

.commodity-label {
  transform: translateX(-50%);
  white-space: nowrap;
}

.storage-label {
  white-space: nowrap;
}

.properties-panel {
  border: 1px solid #dbeafe;
}

.properties-panel input {
  transition: all 0.2s ease;
}

.properties-panel input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.statistics {
  border: 1px solid #bbf7d0;
}

.legend {
  border: 1px solid #e5e7eb;
}

.instructions {
  border: 1px solid #dbeafe;
}

/* Leaflet marker customization */
:deep(.leaflet-marker-icon) {
  transition: all 0.2s ease;
}

:deep(.leaflet-marker-icon:hover) {
  transform: scale(1.2);
}

:deep(.leaflet-marker-icon.selected-site) {
  filter: drop-shadow(0 0 10px #f59e0b);
}
</style>
