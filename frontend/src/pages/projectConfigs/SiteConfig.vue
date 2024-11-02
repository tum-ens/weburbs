<template>
  <Card>
    <template #title> Sites </template>
    <template #content>
      <Accordion v-if="sites" v-model:value="curSite">
        <AccordionPanel
          v-for="site in sites"
          :key="site.name"
          :value="site.name"
        >
          <AccordionHeader>{{ site.name }}</AccordionHeader>
          <AccordionContent>
            <SiteForm :site="site" @update="name => (curSite = name)" />
          </AccordionContent>
        </AccordionPanel>
        <AccordionPanel value="__new">
          <AccordionHeader>New Site</AccordionHeader>
          <AccordionContent>
            <SiteForm
              @update="
                name => {
                  console.log(name)
                  curSite = name
                }
              "
            />
          </AccordionContent>
        </AccordionPanel>
      </Accordion>
    </template>
  </Card>
</template>

<script setup lang="ts">
import SiteForm from '@/forms/SiteForm.vue'
import { useSites } from '@/backend/projects'
import { useRoute } from 'vue-router'
import { ref } from 'vue'

const route = useRoute()

const { data: sites } = useSites(route)

const curSite = ref('__new')
</script>

<style scoped></style>
