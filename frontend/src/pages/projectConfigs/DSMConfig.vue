<template>
  <Card>
    <template #title>DSM</template>
    <template #content>
      My DSM

      <div class="mt-3 flex justify-end gap-3">
        <Button
          @click="
            router.push({
              name: 'ProjectBuySell',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          Buy-Sell-Price >>
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
