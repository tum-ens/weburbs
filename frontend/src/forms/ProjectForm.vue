<template>
  <div v-if="project" class="mt-2 flex flex-col gap-3">
    <FloatLabel variant="on">
      <InputText class="w-full" id="name" v-model="name"/>
      <label for="name">Name</label>
    </FloatLabel>
    <FloatLabel variant="on">
      <Textarea class="w-full" id="description" v-model="description"/>
      <label for="description">Description</label>
    </FloatLabel>

    <Accordion value="0">
      <!-- @vue-ignore -->
      <AccordionPanel pt:root:class="border-0">
        <AccordionHeader>Advanced</AccordionHeader>
        <AccordionContent>
          <div class="flex flex-col mt-2 gap-5">
            <div class="lg:grid lg:grid-cols-3 lg:gap-3 flex flex-col gap-2">
              <FloatLabel variant="on" class="lg:col-span-1">
                <InputNumber
                  class="w-full"
                  inputId="co2limit"
                  v-model="co2limit"
                />
                <label for="co2limit">Co2 Limit</label>
              </FloatLabel>
              <Message
                class="lg:col-span-2 flex items-center"
                size="small"
                severity="secondary"
                variant="simple"
              >
                Limits the sum of all created (as calculated by
                commodity_balance) CO2 in all sites; Only relevant if not
                minimized
              </Message>
            </div>
            <div class="lg:grid lg:grid-cols-3 lg:gap-3 flex flex-col gap-2">
              <FloatLabel variant="on" class="lg:col-span-1">
                <InputNumber
                  class="w-full"
                  inputId="costlimit"
                  v-model="costlimit"
                />
                <label for="costlimit">Cost limit</label>
              </FloatLabel>
              <Message
                class="lg:col-span-2 flex items-center"
                size="small"
                severity="secondary"
                variant="simple"
              >
                Limits the sum of all costs in all sites; Only relevant if not
                minimized
              </Message>
            </div>
          </div>
        </AccordionContent>
      </AccordionPanel>
    </Accordion>
    <Button
      @click="() => emit('submit', name, description, co2limit, costlimit)"
    >
      {{ submitLabel }}
    </Button>
  </div>
</template>

<script setup lang="ts">
import {ref, watch} from 'vue'
import type {Project} from '@/backend/interfaces'

const props = defineProps<{
  submitLabel: string
  project: Project
}>()
const emit = defineEmits<{
  submit: [
    name: string,
    description: string,
    co2limit: number,
    costlimit: number,
  ]
}>()

const name = ref('')
const description = ref('')
const co2limit = ref(0)
const costlimit = ref(0)

watch(
  props.project,
  () => {
    if (props.project) {
      name.value = props.project.name
      description.value = props.project.description
      co2limit.value = props.project.co2limit
      costlimit.value = props.project.costlimit
    }
  },
  {
    immediate: true,
  },
)
</script>

<style scoped></style>
