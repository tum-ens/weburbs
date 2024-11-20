<template>
  <Card v-if="sites">
    <template #title>Sites</template>
    <template #content>
      <div class="grid grid-cols-2 gap-3">
        <Accordion v-model:value="curSite" lazy>
          <AccordionPanel
            v-for="site in sites"
            :key="site.name"
            :value="site.name"
          >
            <AccordionHeader>{{ site.name }}</AccordionHeader>
            <AccordionContent>
              <SiteForm
                :ref="
                  f => {
                    if (curSite === site.name)
                      form = <InstanceType<typeof SiteForm>>f
                  }
                "
                :site="site"
                @update="name => (curSite = name)"
                @updateMarker="updateMarker"
                @deleteMarker="deleteMarker"
              />
            </AccordionContent>
          </AccordionPanel>
          <AccordionPanel value="__new">
            <AccordionHeader>New Site</AccordionHeader>
            <AccordionContent>
              <SiteForm
                :ref="
                  f => {
                    if (curSite === '__new')
                      form = <InstanceType<typeof SiteForm>>f
                  }
                "
                @update="
                  name => {
                    curSite = name
                  }
                "
                @updateMarker="updateMarker"
                @deleteMarker="deleteMarker"
              />
            </AccordionContent>
          </AccordionPanel>
        </Accordion>
        <div>
          <l-map
            @click="mapClick"
            :zoom="2"
            :use-global-leaflet="false"
            :center="[47.41322, -1.219482]"
          >
            <l-tile-layer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              layer-type="base"
              name="OpenStreetMap"
            />
            <l-marker
              v-for="marker in markers"
              :key="marker[0]"
              :lat-lng="marker"
            />
            <l-marker v-if="marker" :lat-lng="marker" />
          </l-map>
        </div>
      </div>
      <div class="mt-3 flex justify-end">
        <Button
          :disabled="sites.length === 0"
          @click="
            router.push({
              name: 'ProjectProcess',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Processes >>
        </Button>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import SiteForm from '@/forms/SiteForm.vue'
import { useRoute, useRouter } from 'vue-router'
import { computed, ref } from 'vue'
import { LMap, LMarker, LTileLayer } from '@vue-leaflet/vue-leaflet'
import 'leaflet/dist/leaflet.css'
import { useSites } from '@/backend/sites'

const route = useRoute()
const router = useRouter()

const { data: sites } = useSites(route)

const curSite = ref('__new')
const form = ref<InstanceType<typeof SiteForm>>()

const marker = ref<[number, number] | undefined>(undefined)
const markers = computed<[number, number][]>(() => {
  if (!sites.value) return []

  return sites.value
    .filter(s => s.name != curSite.value)
    .map(s => [s.lat, s.long])
})

function updateMarker(lat: number, lng: number) {
  marker.value = [lat, lng]
}

function deleteMarker() {
  marker.value = undefined
}

function mapClick(event: L.LeafletMouseEvent) {
  if (form.value) form.value.mapClick(event)
  else console.log('form not found')
}
</script>

<style scoped></style>
