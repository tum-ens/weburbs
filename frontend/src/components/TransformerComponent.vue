<template>
  <div
    class="relative flex flex-col justify-between rounded-2xl border-2 border-primary p-2 gap-3 text-center max-w-xl bg-surface-100 dark:bg-surface-800 select-none hover:shadow-lg hover:cursor-pointer hover:bg-surface-200 dark:hover:bg-surface-700"
  >
    <div class="flex flex-col gap-3">
      <span>{{ title }}</span>
      <span>{{ description }}</span>
    </div>

    <div class="grid grid-cols-3">
      <div class="flex flex-col justify-center">
        <span v-for="i in props.in" :key="i">{{ i }}</span>
      </div>
      <div class="flex flex-col justify-center min-h-20">
        <span
          v-if="props.in.length > 0 || props.out.length > 0"
          class="pi pi-arrow-right"
        ></span>
      </div>
      <div class="flex flex-col justify-center">
        <span v-for="o in props.out" :key="o">{{ o }}</span>
      </div>
    </div>

    <!-- Action Buttons - Bottom Right Corner -->
    <div class="absolute bottom-2 right-2 flex gap-1" v-if="showActions">
      <template v-if="props.componentType === 'project'">
        <Button
          icon="pi pi-download"
          size="small"
          text
          :loading="downloadLoading"
          :disabled="downloadLoading"
          @click.stop="toggleDownloadMenu"
          class="p-button-sm"
          v-tooltip.bottom="
            downloadLoading ? 'Downloading...' : 'Download project'
          "
        />
        <Menu ref="downloadMenu" :model="downloadItems" popup />
      </template>
      <Button
        icon="pi pi-copy"
        size="small"
        text
        @click.stop="emit('duplicate')"
        class="p-button-sm"
        v-tooltip.bottom="
          props.componentType === 'transmission'
            ? 'Create Reverse Transmission'
            : 'Duplicate'
        "
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import Menu from 'primevue/menu'
import { ref } from 'vue'

const props = defineProps<{
  title: string
  description: string
  in: string[]
  out: string[]
  showActions?: boolean
  componentType?:
    | 'commodity'
    | 'process'
    | 'storage'
    | 'transmission'
    | 'project'
  downloadLoading?: boolean
}>()

const emit = defineEmits<{
  duplicate: []
  download: ['config' | 'excel']
}>()

const downloadMenu = ref<InstanceType<typeof Menu>>()

const downloadItems = [
  {
    label: 'Config file',
    icon: 'pi pi-file',
    command: () => emit('download', 'config'),
  },
  {
    label: 'Excel export',
    icon: 'pi pi-file-excel',
    command: () => emit('download', 'excel'),
  },
]

function toggleDownloadMenu(event: Event) {
  if (props.downloadLoading) return
  downloadMenu.value?.toggle(event)
}
</script>

<style scoped></style>
