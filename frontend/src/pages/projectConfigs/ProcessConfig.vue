<template>
  <Card>
    <template #title>Processes</template>
    <template #content>
      My processes

      <div class="mt-3 flex justify-end">
        <Button
          @click="
            router.push({
              name: 'ProjectStorage',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Storage >>
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
