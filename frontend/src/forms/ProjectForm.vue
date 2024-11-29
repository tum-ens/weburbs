<template>
  <div v-if="project" class="mt-2 flex flex-col gap-3">
    <FloatLabel variant="on">
      <InputText
        :invalid="nameInvalid"
        class="w-full"
        id="name"
        v-model="name"
      />
      <label for="name">Name</label>
    </FloatLabel>
    <FloatLabel variant="on">
      <Textarea class="w-full" id="description" v-model="description" />
      <label for="description">Description</label>
    </FloatLabel>

    <Accordion value="1" v-if="advanced">
      <AccordionPanel pt:root:class="border-0" value="0">
        <AccordionHeader>Advanced</AccordionHeader>
        <AccordionContent>
          <div class="flex flex-col mt-2 gap-5">
            <div class="lg:grid lg:grid-cols-3 lg:gap-3 flex flex-col gap-2">
              <FloatLabel variant="on" class="lg:col-span-1">
                <InputNumber
                  :invalid="co2limitInvalid"
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
                  :invalid="costlimitInvalid"
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
    <Button :loading="loading" :label="submitLabel" @click="submit" />
  </div>
</template>

<script setup lang="ts">
import { inject, ref } from 'vue'
import type { Project } from '@/backend/interfaces'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

const advanced = inject('advanced')

const props = defineProps<{
  submitLabel: string
  project: Project
  loading: boolean
}>()
const emit = defineEmits<{
  submit: [
    name: string,
    description: string,
    co2limit: number,
    costlimit: number,
  ]
}>()

const name = ref(props.project.name)
const description = ref(props.project.description)
const co2limit = ref(props.project.co2limit)
const costlimit = ref(props.project.costlimit)

const nameInvalid = ref(false)
const co2limitInvalid = ref(false)
const costlimitInvalid = ref(false)

function submit() {
  let error = false
  if (!name.value) {
    error = true
    nameInvalid.value = true
  } else {
    nameInvalid.value = false
  }
  if (!co2limit.value || co2limit.value < 0) {
    error = true
    co2limitInvalid.value = true
  } else {
    co2limitInvalid.value = false
  }
  if (!costlimit.value || costlimit.value < 0) {
    error = true
    costlimitInvalid.value = true
  } else {
    costlimitInvalid.value = false
  }

  if (error) {
    toast.add({
      summary: 'Error',
      detail: 'Not all fields have been filled properly',
      severity: 'error',
      life: 2000,
    })
    return
  }

  emit('submit', name.value, description.value, co2limit.value, costlimit.value)
}
</script>

<style scoped></style>
