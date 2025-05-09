<template>
  <Accordion v-model:value="curSite" lazy>
    <AccordionPanel v-for="site in sites" :key="site.name" :value="site.name">
      <AccordionHeader>{{ site.name }}</AccordionHeader>
      <AccordionContent>
        <slot :site="site" />
      </AccordionContent>
    </AccordionPanel>
  </Accordion>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useSites } from '@/backend/sites'
import { useRoute } from 'vue-router'

const route = useRoute()

const { data: sites } = useSites(route)

const curSite = defineModel<string | undefined>('curSite', {
  default: undefined,
})

watch(
  sites,
  () => {
    if (!curSite.value && sites.value) {
      curSite.value = sites.value[0].name
    }
  },
  { immediate: true },
)
</script>

<style scoped></style>
