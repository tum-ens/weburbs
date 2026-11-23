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
    <Message v-if="nameError" severity="error" variant="simple" size="small">
      {{ nameError }}
    </Message>
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

    <Accordion v-if="advanced">
      <AccordionPanel pt:root:class="border-0" value="0">
        <AccordionHeader>Advanced</AccordionHeader>
        <AccordionContent pt:root:class="pt-1">
          <FloatLabel variant="on">
            <InputNumber
              :invalid="areaInvalid"
              class="w-full"
              id="area"
              v-model="area"
              v-tooltip.bottom="
                'Gives the total usable area at a site. A constraint is set for all processes that take up a given area per capacity (e.g. Photovoltaics). If no constraint is to be set, leave empty.'
              "
            />
            <label for="area">Area</label>
          </FloatLabel>
        </AccordionContent>
      </AccordionPanel>
    </Accordion>

    <div class="flex flex-row gap-3">
      <Button
        v-if="site"
        fluid
        :loading="deleting"
        label="Delete"
        severity="danger"
        @click="showDeleteDialog = true"
      />
      <Button fluid :loading="updating" @click="submit">
        {{ site ? 'Update' : 'Create' }}
      </Button>
    </div>
  </div>

  <Dialog
    v-if="site"
    v-model:visible="showDeleteDialog"
    modal
    header="Delete Site"
    :style="{ width: '450px' }"
    :closable="false"
  >
    <div class="flex items-center space-x-3 mb-4">
      <i class="pi pi-exclamation-triangle text-red-500 text-2xl"></i>
      <span class="text-lg">
        Are you sure you want to delete the site
        <strong>"{{ site.name }}"</strong>?
      </span>
    </div>
    <p class="text-gray-600 mb-4">
      This action cannot be undone. All commodities, processes, storage, demand,
      and other data for this site will be permanently removed. Transmissions
      connected to this site will also be deleted.
    </p>
    <template #footer>
      <Button text class="mr-2" @click="showDeleteDialog = false">
        Cancel
      </Button>
      <Button severity="danger" :loading="deleting" @click="deleteSite">
        <span v-if="deleting">Deleting...</span>
        <span v-else>Delete</span>
      </Button>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import type { Site } from '@/backend/interfaces'
import { inject, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { decimalToDms, dmsToDecimal } from '@/helper/coordinates'
import type { AxiosError } from 'axios'
import { useDeleteSite, useUpdateSite } from '@/backend/sites'
import { getNameValidationError } from '@/helper/nameValidation'
import { defaultSite } from '@/backend/defaults'

const toast = useToast()
const route = useRoute()
const props = defineProps<{
  site?: Site
}>()
const emit = defineEmits<{
  update: [string]
  delete: []
  updateMarker: [number, number]
  deleteMarker: []
}>()

const showDeleteDialog = ref(false)

const advanced = inject('advanced')

const name = ref(props.site?.name || defaultSite.name)
const area = ref(props.site?.area || defaultSite.area)
const lat = ref(
  props.site ? decimalToDms(props.site.lat, false) : defaultSite.lat,
)
const lon = ref(
  props.site ? decimalToDms(props.site.lon, true) : defaultSite.lon,
)

const nameInvalid = ref(false)
const nameError = ref<string | null>(null)
const areaInvalid = ref(false)
const lonInvalid = ref(false)
const latInvalid = ref(false)

const latReg = /([NS])(\d+)°(\d+)'([\d.]+)''/
const lonReg = /([EW])(\d+)°(\d+)'([\d.]+)''/

watch(name, () => {
  if (!name.value) {
    nameInvalid.value = false
    nameError.value = null
    return
  }
  nameError.value = getNameValidationError(name.value)
  nameInvalid.value = nameError.value !== null
})

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

const { mutate: updateSite, isPending: updating } = useUpdateSite(route)
const { mutate: removeSite, isPending: deleting } = useDeleteSite(route)

function submit() {
  let error = false
  if (!name.value) {
    error = true
    nameInvalid.value = true
    nameError.value = null
  } else {
    nameError.value = getNameValidationError(name.value)
    if (nameError.value) {
      error = true
      nameInvalid.value = true
    } else {
      nameInvalid.value = false
    }
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
      detail: nameError.value || 'Not all fields have been filled properly',
      severity: 'error',
      life: 2000,
    })
    return
  }

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

function deleteSite() {
  if (!props.site) return

  removeSite(props.site.name, {
    onSuccess() {
      showDeleteDialog.value = false
      toast.add({
        summary: 'Deleted',
        detail: `Site ${props.site!.name} has been deleted`,
        severity: 'success',
        life: 2000,
      })
      emit('delete')
    },
    onError(error) {
      toast.add({
        summary: 'Error deleting',
        detail:
          (<AxiosError>error)?.response?.data ||
          `An error occurred when deleting ${props.site!.name}`,
        severity: 'error',
        life: 2000,
      })
    },
  })
}
</script>

<style scoped></style>
