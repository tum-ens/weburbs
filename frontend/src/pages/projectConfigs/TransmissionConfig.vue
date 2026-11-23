<template>
  <Card>
    <template #title>
      <div class="flex flex-row justify-between">
        <span>Transmissions</span>
        <Button label="Add transmission" @click="createVisible = true" />
      </div>
    </template>
    <template #content>
      <div
        v-if="transmissions?.length"
        class="grid grid-cols-[repeat(auto-fill,minmax(12rem,1fr))] md:grid-cols-[repeat(auto-fill,minmax(17rem,1fr))] gap-3"
      >
        <Transformer
          v-for="trans in transmissions"
          :key="trans.sitein + trans.siteout + trans.commodity"
          :title="trans.commodity"
          :description="TransmissionType[trans.type]"
          :in="[trans.sitein]"
          :out="[trans.siteout]"
          :show-actions="true"
          component-type="transmission"
          @click="
            () => {
              clickedTransmission = trans
              editVisible = true
            }
          "
          @duplicate="duplicateTransmission(trans)"
        />
      </div>
      <div v-else>
        <span>No transmission added</span>
      </div>

      <div class="mt-3 flex justify-end gap-3">
        <Button
          @click="
            router.push({
              name: 'ProjectDSM',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          DSM >>
        </Button>
      </div>
    </template>
  </Card>
  <CreateTransmissionDialog v-model:visible="createVisible" />
  <EditTransmissionDialog
    v-if="clickedTransmission"
    :transmission="clickedTransmission"
    v-model:visible="editVisible"
    :from_energy_diagram="route.query.from === 'energy-diagram'"
  />
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import CreateTransmissionDialog from '@/dialogs/CreateTransmissionDialog.vue'
import { ref } from 'vue'
import {
  useTransmission,
  useDuplicateTransmission,
} from '@/backend/transmission'
import Transformer from '@/components/TransformerComponent.vue'
import { type Transmission, TransmissionType } from '@/backend/interfaces'
import EditTransmissionDialog from '@/dialogs/EditTransmissionDialog.vue'
import { useToast } from 'primevue/usetoast'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const createVisible = ref(false)
const editVisible = ref(false)

const clickedTransmission = ref<Transmission | null>(null)

const { data: transmissions } = useTransmission(route)

// Duplicate transmission functionality
const duplicateTransmissionMutation = useDuplicateTransmission(route)

const duplicateTransmission = async (transmission: Transmission) => {
  try {
    await duplicateTransmissionMutation.mutateAsync({
      sitein_name: transmission.sitein,
      siteout_name: transmission.siteout,
      com_name: transmission.commodity,
    })
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Reverse transmission created successfully',
      life: 3000,
    })
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response?.status === 400) {
      toast.add({
        severity: 'warn',
        summary: 'Warning',
        detail: 'Reverse transmission already exists',
        life: 3000,
      })
    } else {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to create reverse transmission',
        life: 3000,
      })
      console.error('Failed to duplicate transmission:', error)
    }
  }
}
</script>

<style scoped></style>
