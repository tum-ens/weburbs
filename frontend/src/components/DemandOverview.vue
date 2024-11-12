<template>
  <div class="flex flex-row gap-3">
    <Select
      class="w-52"
      v-model="com"
      :options="commodities"
      optionLabel="name"
    />
    <Button @click="generate">Generate</Button>
  </div>
</template>

<script setup lang="ts">
import type { Site } from '@/backend/interfaces'
import { useRoute } from 'vue-router'
import { useProjectSiteCommodities } from '@/backend/commodities'
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useGenerateDemand } from '@/backend/demand'

const route = useRoute()
const toast = useToast()

const props = defineProps<{
  site: Site
}>()

const { data: commodities } = useProjectSiteCommodities(route, props.site.name)
const { mutate: generateDemand } = useGenerateDemand(route)

const com = ref()

function generate() {
  generateDemand(
    { site_name: props.site.name, com_name: com.value.name },
    {
      onSuccess() {
        toast.add({
          summary: 'Success',
          detail: `Demand for ${com.value.name} was generated`,
          severity: 'success',
          life: 2000,
        })
      },
    },
  )
}
</script>

<style scoped></style>
