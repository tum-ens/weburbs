import type { ToastServiceMethods } from 'primevue'
import * as XLSX from 'xlsx'

export function checkUploadFile(
  toast: ToastServiceMethods,
  file: File,
): Promise<number[]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = async e => {
      if (e.target) {
        try {
          if (file.name.endsWith('.json')) {
            const parsed = JSON.parse(<string>e.target.result)
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
              reject()
            }
            resolve(parsed)
          } else if (file.name.endsWith('.xlsx')) {
            const workbook = XLSX.read(e.target.result, { type: 'array' })
            const sheet = workbook.Sheets[workbook.SheetNames[0]]
            const result: number[] = []
            for (let i = 1; i <= 8760; i++) {
              const value = sheet[`A${i}`]?.v
              if (typeof value === 'number') {
                result.push(value)
              } else {
                toast.add({
                  summary: 'Upload error',
                  detail: `JSON needs to contain an error with exactly 8760 numbers`,
                  severity: 'error',
                  life: 2000,
                })
                reject()
              }
            }
            resolve(result)
          }
        } catch (error) {
          toast.add({
            summary: 'Upload error',
            detail: `Uploaded an invalid file`,
            severity: 'error',
            life: 2000,
          })
          console.log(error)
          reject()
        }
      } else {
        toast.add({
          summary: 'Upload error',
          detail: `Something went wrong when reading file ${file.name}`,
          severity: 'error',
          life: 2000,
        })
      }
    }
    if (file.name.endsWith('.json')) reader.readAsText(file)
    else if (file.name.endsWith('.xlsx')) reader.readAsArrayBuffer(file)
    else reject()
  })
}
