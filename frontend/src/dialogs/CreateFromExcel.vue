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
        @select="onFileSelect"
        accept=".xls,.xlsx"
        pt:root:class="justify-start"
      />
      <FloatLabel variant="on">
        <InputText fluid id="title" v-model="title" />
        <label for="name">Title</label>
      </FloatLabel>
      <Button label="Upload" @click="upload" />
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { FileUpload, type FileUploadSelectEvent } from 'primevue'
import { ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useUploadExcel } from '@/backend/excelupload'

const toast = useToast()
const { mutate: uploadExcel } = useUploadExcel()

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

  uploadExcel({ project_name: title.value, file })
  visible.value = false
}

watch(visible, () => {
  // @ts-expect-error Wrong type description
  if (excelUpload.value) excelUpload.value.clear()
  title.value = ''
})
</script>

<style scoped></style>
