<template>
  <Card>
    <template #title>Demand</template>
    <template #content>
      <Accordion v-model:value="curSite" lazy>
        <AccordionPanel
          v-for="site in sites"
          :key="site.name"
          :value="site.name"
        >
          <AccordionHeader>{{ site.name }}</AccordionHeader>
          <AccordionContent>
            <DemandOverview :site="site" />
          </AccordionContent>
        </AccordionPanel>
      </Accordion>

      <div class="mt-3 flex justify-end">
        <Button
          v-if="advanced"
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
        <Button
          v-else
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
      </div></template
    >
  </Card>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useSites } from '@/backend/sites'
import DemandOverview from '@/components/DemandOverview.vue'
import { inject, ref, watch } from 'vue'

const route = useRoute()
const router = useRouter()

const advanced = inject('advanced')

const curSite = ref('')

const { data: sites } = useSites(route)
watch(
  sites,
  () => {
    if (!sites.value || sites.value.length === 0) return

    curSite.value = sites.value[0].name
  },
  { immediate: true },
)
</script>

<style scoped></style>
