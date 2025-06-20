<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    modal
    header="Create from Excel"
    class=""
  >
    <div class="flex flex-col gap-3">
      <FileUpload
        ref="excelUpload"
        mode="basic"
        custom-upload
        choose-icon="pi pi-upload"
        choose-label="Select"
        :disabled="uploading"
        @select="onFileSelect"
        accept=".xls,.xlsx"
        pt:root:class="justify-start"
      />
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
import { useUploadExcel } from '@/backend/upload'
import { useRouter } from 'vue-router'

const toast = useToast()
const router = useRouter()
const { mutate: uploadExcel } = useUploadExcel()

const uploading = ref(false)

const excelUpload = ref<InstanceType<typeof FileUpload>>()
const visible = defineModel<boolean>('visible', { default: false })

const title = ref('')
let file: Blob | null = null

async function onFileSelect(event: FileUploadSelectEvent) {
  file = <Blob>event.files[0]
  // @ts-expect-error event.files has weird format
  title.value = file.name.split('.').slice(0, -1).join('.')
}

function upload() {
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
  uploadExcel(
    { project_name: title.value, file },
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
  if (excelUpload.value) excelUpload.value.clear()
  title.value = ''
  uploading.value = false
})
</script>

<style scoped></style>
