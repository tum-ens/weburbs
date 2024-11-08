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
        :invalid="lngInvalid"
        mask="a999°99'99.999''"
        class="w-full"
        id="lng"
        v-model="lng"
      />
      <label for="lng">Longitude</label>
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
const lng = ref(props.site ? decimalToDms(props.site.long, true) : '')

const nameInvalid = ref(false)
const areaInvalid = ref(false)
const lngInvalid = ref(false)
const latInvalid = ref(false)

const latReg = /([NS])(\d+)°(\d+)'([\d.]+)''/
const lngReg = /([EW])(\d+)°(\d+)'([\d.]+)''/
watch(
  [lng, lat],
  () => {
    if (lat.value.match(latReg) && lng.value.match(lngReg)) {
      emit('updateMarker', dmsToDecimal(lat.value), dmsToDecimal(lng.value))
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
  lng.value = decimalToDms(event.latlng.lng, true)
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
  if (!lng.value || !lng.value.match(lngReg)) {
    error = true
    lngInvalid.value = true
  } else {
    lngInvalid.value = false
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

  if (area.value && lng.value && lat.value)
    updateSite(
      {
        name: props.site?.name || name.value,
        site: {
          name: name.value,
          area: area.value,
          long: dmsToDecimal(lng.value),
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
