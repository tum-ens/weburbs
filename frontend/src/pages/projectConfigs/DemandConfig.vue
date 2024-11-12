<template>
  <Card>
    <template #title>Demand</template>
    <template #content>
      <Accordion>
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
          @click="
            router.push({
              name: 'ProjectSuplm',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Suplm >>
        </Button>
      </div></template
    >
  </Card>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useSites } from '@/backend/sites'
import DemandOverview from '@/components/DemandOverview.vue'

const route = useRoute()
const router = useRouter()

const { data: sites } = useSites(route)
</script>

<style scoped></style>
