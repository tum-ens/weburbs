import type { ToastServiceMethods } from 'primevue'

export function checkUploadFile(
  toast: ToastServiceMethods,
  file: string | ArrayBuffer | null,
) {
  try {
    const parsed = JSON.parse(<string>file)
    if (
      !Array.isArray(parsed) ||
      parsed.length !== 8760 ||
      !parsed.every(item => typeof item === 'number')
    ) {
      toast.add({
        summary: 'Upload error',
        detail: `JSON needs to contain an error with exactly 8760 numbers`,
        severity: 'error',
        life: 2000,
      })
      return false
    }
  } catch (error) {
    toast.add({
      summary: 'Upload error',
      detail: `File needs to be a JSON`,
      severity: 'error',
      life: 2000,
    })
    console.log(error)
    return false
  }
  return true
}
