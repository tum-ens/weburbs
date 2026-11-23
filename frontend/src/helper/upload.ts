import type { ToastServiceMethods } from 'primevue'
import * as XLSX from 'xlsx'

const TIMESERIES_LENGTH = 8760

function safeFilePart(name: string) {
  return name.replace(/[\\/:*?"<>|]/g, '_').trim() || 'timeseries'
}

export function timeseriesFilename(projectName: string, seriesName: string) {
  return `${safeFilePart(projectName)}_${safeFilePart(seriesName)}.xlsx`
}

export function seriesNameFromUpload(
  fileName: string,
  projectName: string,
  siteName?: string,
  commodityName?: string,
) {
  let base = fileName.split('.').slice(0, -1).join('.')
  for (const part of [projectName, siteName, commodityName]) {
    if (!part) continue
    const prefix = `${safeFilePart(part)}_`
    if (base.startsWith(prefix)) base = base.slice(prefix.length)
  }
  return base
}

export function downloadTimeseriesExcel(
  values: number[],
  projectName: string,
  seriesName: string,
  quantity?: number,
) {
  const sheet = XLSX.utils.aoa_to_sheet(values.map(value => [value]))
  if (quantity !== undefined) {
    sheet['B1'] = { t: 'n', v: quantity }
    const range = XLSX.utils.decode_range(sheet['!ref'] || 'A1')
    if (range.e.c < 1) range.e.c = 1
    sheet['!ref'] = XLSX.utils.encode_range(range)
  }
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, sheet, 'Timeseries')
  XLSX.writeFile(workbook, timeseriesFilename(projectName, seriesName))
}

export function downloadTimeseriesExcels(
  files: { values: number[]; seriesName: string; quantity?: number }[],
  projectName: string,
) {
  files.forEach((file, index) => {
    window.setTimeout(() => {
      downloadTimeseriesExcel(
        file.values,
        projectName,
        file.seriesName,
        file.quantity,
      )
    }, index * 250)
  })
}

export function projectLabel(proj: string | string[]) {
  return Array.isArray(proj) ? proj.join('_') : proj
}

export function checkUploadFile(
  toast: ToastServiceMethods,
  file: File,
): Promise<number[]> {
  return readTimeseriesUpload(toast, file).then(result => result.steps)
}

export function readTimeseriesUpload(
  toast: ToastServiceMethods,
  file: File,
): Promise<{ steps: number[]; quantity: number }> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = async e => {
      if (e.target) {
        try {
          if (file.name.endsWith('.json')) {
            const parsed = JSON.parse(<string>e.target.result)
            if (
              !Array.isArray(parsed) ||
              parsed.length !== TIMESERIES_LENGTH ||
              !parsed.every(item => typeof item === 'number')
            ) {
              toast.add({
                summary: 'Upload error',
                detail: `JSON needs to contain an error with exactly 8760 numbers`,
                severity: 'error',
                life: 2000,
              })
              reject()
              return
            }
            resolve({ steps: parsed, quantity: 1 })
          } else if (file.name.endsWith('.xlsx')) {
            const workbook = XLSX.read(e.target.result, { type: 'array' })
            const sheet = workbook.Sheets[workbook.SheetNames[0]]
            const result: number[] = []
            for (let i = 1; i <= TIMESERIES_LENGTH; i++) {
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
                return
              }
            }
            const quantityCell = sheet['B1']?.v
            const quantity =
              typeof quantityCell === 'number' && quantityCell > 0
                ? quantityCell
                : 1
            resolve({ steps: result, quantity })
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
