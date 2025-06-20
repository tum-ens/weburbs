<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Create from Config"
    class=""
  >
    <div class="flex flex-col gap-3">
      <Tabs v-model:value="method">
        <TabList>
          <Tab :value="0"> Upload </Tab>
          <Tab :value="1"> Paste </Tab>
        </TabList>
        <TabPanels>
          <TabPanel :value="0">
            <FileUpload
              ref="configUpload"
              mode="basic"
              custom-upload
              choose-icon="pi pi-upload"
              choose-label="Select"
              :disabled="uploading"
              @select="onFileSelect"
              accept=".urbs"
              pt:root:class="justify-start"
            />
          </TabPanel>
          <TabPanel :value="1">
            <TextArea v-model="content" placeholder="Paste your config here" />
          </TabPanel>
        </TabPanels>
      </Tabs>
      <FloatLabel variant="on">
        <InputText fluid id="title" v-model="title" :disabled="uploading" />
        <label for="name">Title</label>
      </FloatLabel>
      <Button label="Upload" @click="upload" :loading="uploading" />
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { FileUpload, type FileUploadSelectEvent } from 'primevue'
import { ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useUploadConfig } from '@/backend/upload'
import { useRouter } from 'vue-router'

const toast = useToast()
const router = useRouter()
const { mutate: uploadConfig } = useUploadConfig()

const uploading = ref(false)

const configUpload = ref<InstanceType<typeof FileUpload>>()
const visible = defineModel<boolean>('visible', { default: false })

const method = ref(0)

const title = ref('')
const content = ref('')
let file: Blob | null = null

async function onFileSelect(event: FileUploadSelectEvent) {
  file = <Blob>event.files[0]
  // @ts-expect-error event.files has weird format
  title.value = file.name.split('.').slice(0, -1).join('.')
}

async function upload() {
  if (!file) {
    toast.add({
      summary: 'Upload error',
      detail: `No file selected`,
      severity: 'error',
      life: 2000,
    })
    return
  }
  if (!title.value) {
    toast.add({
      summary: 'Upload error',
      detail: `Title is missing`,
      severity: 'error',
      life: 2000,
    })
    return
  }

  uploading.value = true
  uploadConfig(
    {
      project_name: title.value,
      content: method.value === 0 ? await file.text() : content.value,
    },
    {
      onSuccess() {
        router.push({
          name: 'ProjectSimulation',
          params: {
            proj: title.value,
          },
        })
        uploading.value = false
        visible.value = false
      },
      onError(error) {
        toast.add({
          summary: 'Upload failed',
          // @ts-expect-error Axios error is the only error possible
          detail: error.response.data,
          severity: 'error',
          life: 2000,
        })
        uploading.value = false
      },
    },
  )
}

watch(visible, () => {
  // @ts-expect-error Wrong type description
  if (configUpload.value) configUpload.value.clear()
  title.value = ''
  uploading.value = false
})
</script>

<style scoped></style>
