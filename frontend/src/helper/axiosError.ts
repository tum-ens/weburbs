import axios from 'axios'

export function axiosErrorMessage(
  error: unknown,
  fallback = 'Request failed',
): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data
    if (typeof data === 'string' && data.trim()) return data
    if (data && typeof data === 'object') {
      const record = data as { detail?: string; message?: string }
      if (record.detail) return record.detail
      if (record.message) return record.message
    }
    if (error.response?.status === 403) {
      return 'Session expired or invalid security token. Refresh the page and try again.'
    }
    if (error.response?.status === 409) {
      return 'A project with this name already exists. Choose a different title.'
    }
    if (error.response?.status === 502 || error.response?.status === 504) {
      return 'The server timed out while processing the file. Try again in a moment.'
    }
    if (error.code === 'ECONNABORTED') {
      return 'The upload timed out. Large Excel files can take several minutes.'
    }
    if (error.message) return error.message
  }
  if (error instanceof Error && error.message) return error.message
  return fallback
}
