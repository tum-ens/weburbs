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
          @click="
            () => {
              clickedTransmission = trans
              editVisible = true
            }
          "
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
  />
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import CreateTransmissionDialog from '@/dialogs/CreateTransmissionDialog.vue'
import { ref } from 'vue'
import { useTransmission } from '@/backend/transmission'
import Transformer from '@/components/TransformerComponent.vue'
import { type Transmission, TransmissionType } from '@/backend/interfaces'
import EditTransmissionDialog from '@/dialogs/EditTransmissionDialog.vue'

const route = useRoute()
const router = useRouter()

const createVisible = ref(false)
const editVisible = ref(false)

const clickedTransmission = ref<Transmission | null>(null)

const { data: transmissions } = useTransmission(route)
</script>

<style scoped></style>
