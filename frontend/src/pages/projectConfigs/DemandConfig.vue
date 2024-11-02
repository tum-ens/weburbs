<template>
  <Card>
    <template #title>Demand</template>
    <template #content>
      My demand

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

const route = useRoute()
const router = useRouter()
</script>

<style scoped></style>
