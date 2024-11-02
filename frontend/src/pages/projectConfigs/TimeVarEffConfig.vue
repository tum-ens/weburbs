<template>
  <Card>
    <template #title>TimeVarEff</template>
    <template #content>
      My TimeVarEff

      <div class="mt-3 flex justify-end gap-3">
        <Button
          @click="
            router.push({
              name: 'ProjectSimulation',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Simulation >>
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
