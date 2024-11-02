<template>
  <Card>
    <template #title>Transmission</template>
    <template #content>
      My Transmission

      <div class="mt-3 flex justify-end gap-3">
        <Button
          @click="
            router.push({
              name: 'ProjectDSM',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          DSM >>
        </Button>
      </div></template
    >
  </Card>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
</script>

<style scoped></style>
