<template>
  <Card>
    <template #title>
      <div class="flex flex-row justify-between">
        <span>Transmissions</span>
        <Button label="Add transmission" @click="createVisible = true" />
      </div>
    </template>
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
      </div>
    </template>
  </Card>
  <CreateTransmissionDialog site_name="None" :visible="createVisible" />
  <!--  <EditTransmissionDialog site_name="None"-->
  <!--                          :visible="editVisible"/>-->
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import CreateTransmissionDialog from '@/dialogs/CreateTransmissionDialog.vue'
import { ref } from 'vue'
import EditTransmissionDialog from '@/dialogs/EditTransmissionDialog.vue'

const route = useRoute()
const router = useRouter()

const createVisible = ref(false)
const editVisible = ref(false)
</script>

<style scoped></style>
