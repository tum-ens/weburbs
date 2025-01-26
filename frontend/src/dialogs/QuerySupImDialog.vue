<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    :header="`Generate SupIm for '${props.commodity.name}'`"
  >
    <div class="flex flex-col gap-3">
      <Select v-model="option" :options />
      <Button
        @click="query"
        :disabled="!option || isPending"
        :loading="isPending"
        label="Query"
      />
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import type { Commodity, Site } from '@/backend/interfaces'
import { useQuerySupIm } from '@/backend/supim'
import { useToast } from 'primevue/usetoast'
import { useRoute } from 'vue-router'
import { ref } from 'vue'

const toast = useToast()
const route = useRoute()

const visible = defineModel<boolean>()
const props = defineProps<{
  site: Site
  commodity: Commodity
}>()

const options = ['Solar', 'Wind']
const option = ref()

const { mutate: generateSupIm, isPending } = useQuerySupIm(
  route,
  props.site,
  props.commodity,
)

function query() {
  if (!option.value) return

  generateSupIm(
    { type: option.value },
    {
      onSuccess() {
        toast.add({
          summary: 'Success',
          detail: `SupIm for ${props.commodity.name} was generated`,
          severity: 'success',
          life: 2000,
        })
        visible.value = false
      },
    },
  )
}
</script>

<style scoped></style>
