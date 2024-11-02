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
        :invalid="longInvalid"
        mask="a99°99'99.999''"
        class="w-full"
        id="long"
        v-model="long"
      />
      <label for="long">Longitude</label>
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
    <Button @click="submit">{{ !!site ? 'Update' : 'Create' }}</Button>
  </div>
</template>

<script setup lang="ts">
import type { Site } from '@/backend/interfaces'
import { ref } from 'vue'
import { useUpdateSite } from '@/backend/projects'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const route = useRoute()
const props = defineProps<{
  site?: Site
}>()
const emit = defineEmits<{
  update: [string]
}>()

const name = ref(props.site?.name || '')
const area = ref(props.site?.area || undefined)
const long = ref(props.site ? decimalToDms(props.site.long, true) : '')
const lat = ref(props.site ? decimalToDms(props.site.lat, false) : '')

const nameInvalid = ref(false)
const areaInvalid = ref(false)
const longInvalid = ref(false)
const latInvalid = ref(false)

const { mutate: updateSite } = useUpdateSite(route)

const longReg = /([EW])(\d+)°(\d+)'([\d.]+)''/
const latReg = /([NS])(\d+)°(\d+)'([\d.]+)''/

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
  if (!long.value || !long.value.match(longReg)) {
    error = true
    longInvalid.value = true
  } else {
    longInvalid.value = false
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

  if (area.value && long.value && lat.value)
    updateSite(
      {
        name: props.site?.name || name.value,
        site: {
          name: name.value,
          area: area.value,
          long: dmsToDecimal(long.value),
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

function dmsToDecimal(dms: string) {
  const regex = /([NSEW])(\d+)°(\d+)'([\d.]+)''/
  const matches = dms.match(regex)
  if (!matches) {
    throw new Error('Invalid DMS format')
  }
  const [, direction, degrees, minutes, seconds] = matches
  let decimal =
    parseInt(degrees) + parseInt(minutes) / 60 + parseFloat(seconds) / 3600
  if (direction === 'W' || direction === 'S') {
    decimal = -decimal
  }
  return decimal
}

function decimalToDms(decimal: number, long: boolean) {
  const direction = decimal < 0 ? (long ? 'W' : 'N') : long ? 'E' : 'S'
  decimal = Math.abs(decimal)
  const degrees = Math.floor(decimal)
  const minutesDecimal = (decimal - degrees) * 60
  const minutes = Math.floor(minutesDecimal)
  const seconds = (minutesDecimal - minutes) * 60
  return `${direction}${degrees.toString().padStart(2, '0')}°${minutes.toString().padStart(2, '0')}'${seconds < 10 ? '0' : ''}${seconds.toFixed(3)}''`
}
</script>

<style scoped></style>
