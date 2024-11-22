<template>
  <div class="mt-2 flex flex-col gap-3">
    <FloatLabel variant="on">
      <InputText
        :invalid="nameInvalid"
        class="w-full"
        id="name"
        v-model="name"
      />
      <label for="name">Name</label>
    </FloatLabel>
    <FloatLabel variant="on">
      <InputNumber
        :invalid="areaInvalid"
        class="w-full"
        id="area"
        v-model="area"
      />
      <label for="area">Area</label>
    </FloatLabel>
    <FloatLabel variant="on">
      <InputMask
        :auto-clear="false"
        :invalid="latInvalid"
        mask="a99°99'99.999''"
        class="w-full"
        id="lat"
        v-model="lat"
      />
      <label for="lat">Latitude</label>
    </FloatLabel>
    <FloatLabel variant="on">
      <InputMask
        :auto-clear="false"
        :invalid="lonInvalid"
        mask="a999°99'99.999''"
        class="w-full"
        id="lon"
        v-model="lon"
      />
      <label for="lon">Longitude</label>
    </FloatLabel>
    <Button @click="submit">{{ !!site ? 'Update' : 'Create' }}</Button>
  </div>
</template>

<script setup lang="ts">
import type { Site } from '@/backend/interfaces'
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { decimalToDms, dmsToDecimal } from '@/helper/coordinates'
import { useUpdateSite } from '@/backend/sites'

const toast = useToast()
const route = useRoute()
const props = defineProps<{
  site?: Site
}>()
const emit = defineEmits<{
  update: [string]
  updateMarker: [number, number]
  deleteMarker: []
}>()

const name = ref(props.site?.name || '')
const area = ref(props.site?.area || undefined)
const lat = ref(props.site ? decimalToDms(props.site.lat, false) : '')
const lon = ref(props.site ? decimalToDms(props.site.lon, true) : '')

const nameInvalid = ref(false)
const areaInvalid = ref(false)
const lonInvalid = ref(false)
const latInvalid = ref(false)

const latReg = /([NS])(\d+)°(\d+)'([\d.]+)''/
const lonReg = /([EW])(\d+)°(\d+)'([\d.]+)''/
watch(
  [lon, lat],
  () => {
    if (lat.value.match(latReg) && lon.value.match(lonReg)) {
      emit('updateMarker', dmsToDecimal(lat.value), dmsToDecimal(lon.value))
    } else {
      emit('deleteMarker')
    }
  },
  {
    immediate: true,
  },
)

function mapClick(event: L.LeafletMouseEvent) {
  lat.value = decimalToDms(event.latlng.lat, false)
  lon.value = decimalToDms(event.latlng.lng, true)
}
defineExpose({ mapClick })

const { mutate: updateSite } = useUpdateSite(route)

function submit() {
  let error = false
  if (!name.value) {
    error = true
    nameInvalid.value = true
  } else {
    nameInvalid.value = false
  }
  if (!area.value || area.value < 0) {
    error = true
    areaInvalid.value = true
  } else {
    areaInvalid.value = false
  }
  if (!lon.value || !lon.value.match(lonReg)) {
    error = true
    lonInvalid.value = true
  } else {
    lonInvalid.value = false
  }
  if (!lat.value || !lat.value.match(latReg)) {
    error = true
    latInvalid.value = true
  } else {
    latInvalid.value = false
  }

  if (error) {
    toast.add({
      summary: 'Error',
      detail: 'Not all fields have been filled properly',
      severity: 'error',
      life: 2000,
    })
    return
  }

  if (area.value && lon.value && lat.value)
    updateSite(
      {
        name: props.site?.name || name.value,
        site: {
          name: name.value,
          area: area.value,
          lon: dmsToDecimal(lon.value),
          lat: dmsToDecimal(lat.value),
        },
      },
      {
        onSuccess() {
          toast.add({
            summary: 'Success',
            detail: props.site ? 'Site was updated' : 'Site was created',
            severity: 'success',
            life: 2000,
          })
          emit('update', name.value)
        },
      },
    )
}
</script>

<style scoped></style>
