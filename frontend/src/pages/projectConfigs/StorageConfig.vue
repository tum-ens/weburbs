<template>
  <Card>
    <template #title>Storage</template>
    <template #content>
      My storage

      <div class="mt-3 flex justify-end">
        <Button
          @click="
            router.push({
              name: 'ProjectDemand',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Demand >>
        </Button>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
</script>

<style scoped></style>
