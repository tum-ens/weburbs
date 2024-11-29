<template>
  <Card>
    <template #title>SupIm</template>
    <template #content>
      <Accordion lazy v-model:value="curSite">
        <AccordionPanel
          v-for="site in sites"
          :key="site.name"
          :value="site.name"
        >
          <AccordionHeader>{{ site.name }}</AccordionHeader>
          <AccordionContent>
            <SupImOverview :site="site" />
          </AccordionContent>
        </AccordionPanel>
      </Accordion>

      <div class="mt-3 flex justify-end gap-3">
        <Button
          severity="info"
          @click="
            router.push({
              name: 'ProjectTransmission',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Transmission >>
        </Button>
        <Button
          @click="
            router.push({
              name: 'ProjectSimulation',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Simulation >>
        </Button>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useSites } from '@/backend/sites'
import SupImOverview from '@/components/SupImOverview.vue'
import { ref, watch } from 'vue'

const route = useRoute()
const router = useRouter()

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
