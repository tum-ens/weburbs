<template>
  <Card class="w-80">
    <template #content>
      <ScrollPanel>
        <PanelMenu :model="items" v-model:expanded-keys="expandedKey" />
      </ScrollPanel>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const expandedKey = ref<{ [key: string]: boolean }>({})
watch(
  route,
  () => {
    expandedKey.value = {}
    if (route.name) expandedKey.value[<string>route.name] = true
    for (const parent of <string[]>route.meta.parents) {
      expandedKey.value[parent] = true
    }
    if (route.params.projId)
      expandedKey.value[<string>route.params.projId] = true
  },
  { immediate: true },
)
const items = ref([
  {
    key: 'Home',
    label: 'Home',
    icon: 'pi pi-home',
    command: () => router.push({ name: 'Home' }),
  },
  {
    key: 'ProjectList',
    label: 'Projects',
    icon: 'pi pi-folder',
    command: () => router.push({ name: 'ProjectList' }),
    items: [
      {
        key: 'Project A',
        label: 'Project A',
        icon: 'pi pi-receipt',
        command: () =>
          router.push({
            name: 'Project',
            params: {
              projId: 'Project A',
            },
          }),
      },
    ],
  },
])
</script>

<style scoped></style>
