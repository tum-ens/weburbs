<template>
  <Card>
    <template #title>Buy-Sell-Price</template>
    <template #content>
      <div class="flex flex-col">
        <BuySellPriceOverview
          v-for="bsp in buysellprices"
          :key="bsp.name"
          :bsp="bsp"
        />
      </div>
      <divider />
      <div class="grid grid-cols-1 md:grid-cols-6 lg:grid-cols-8 gap-3">
        <div class="flex flex-col gap-3">
          <h1>Add BuySellPrice</h1>
          <Select
            :disabled="!com_names"
            v-model="com_name"
            :options="com_names"
          />
          <FileUpload
            :disabled="!com_name && !checkUploadFile"
            mode="basic"
            custom-upload
            choose-icon="pi pi-upload"
            class="w-full"
            choose-label="Upload"
            @select="event => upload(event)"
          >
            <!-- hide label -->
            <template #filelabel>
              <template />
            </template>
          </FileUpload>
        </div>
      </div>

      <div class="mt-3 flex justify-end gap-3">
        <Button
          @click="
            router.push({
              name: 'ProjectTimeVarEff',
              params: {
                proj: route.params.proj,
              },
            })
          "
        >
          TimeVarEff >>
        </Button>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import BuySellPriceOverview from '@/components/BuySellPriceOverview.vue'
import {
  useGetBuySellPrices,
  useUploadBuySellPrice,
} from '@/backend/buysellprice'
import { FileUpload, type FileUploadSelectEvent } from 'primevue'
import { useProjectCommodities } from '@/backend/commodities'
import { ref } from 'vue'
import { checkUploadFile } from '@/helper/upload'
import { useToast } from 'primevue/usetoast'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const bsp = {
  name: '',
  steps: [],
}

const { data: buysellprices } = useGetBuySellPrices(route)
const { data: com_names } = useProjectCommodities(route)
const { mutate: uploadBSP } = useUploadBuySellPrice(route, bsp)

const checkingUpload = ref(false)

const com_name = ref<string | undefined>(undefined)

async function upload(event: FileUploadSelectEvent) {
  if (!com_name.value) return
  checkingUpload.value = true
  const file = event.files[0]
  bsp.name = com_name.value

  checkUploadFile(toast, file)
    .then(res => {
      uploadBSP(res)
    })
    .catch(() => {})
    .finally(() => {
      // @ts-expect-error Wrong type description
      if (profileUpload.value) profileUpload.value.clear()
      checkingUpload.value = false
    })
}
</script>

<style scoped></style>
