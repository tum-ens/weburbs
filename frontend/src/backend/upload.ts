import { useMutation, useQueryClient } from '@tanstack/vue-query'
import axios from 'axios'
import { useCSRF } from '@/backend/security'

const UPLOAD_TIMEOUT_MS = 600_000

export function useUploadExcel() {
  const queryClient = useQueryClient()
  const { data: csrf } = useCSRF()
  return useMutation({
    mutationFn: (data: { project_name: string; file: Blob }) => {
      if (!csrf.value) {
        return Promise.reject(
          new Error(
            'Security token not ready yet. Wait a moment and try again.',
          ),
        )
      }
      const formData = new FormData()
      formData.append('file', data.file)
      return axios.post(
        `/api/project/${encodeURIComponent(data.project_name)}/excelupload/`,
        formData,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
          timeout: UPLOAD_TIMEOUT_MS,
        },
      )
    },
    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: ['projects'],
      })
    },
  })
}

export function useUploadConfig() {
  const queryClient = useQueryClient()
  const { data: csrf } = useCSRF()
  return useMutation({
    mutationFn: (data: { project_name: string; content: string }) => {
      if (!csrf.value) {
        return Promise.reject(
          new Error(
            'Security token not ready yet. Wait a moment and try again.',
          ),
        )
      }
      return axios.post(
        `/api/project/${encodeURIComponent(data.project_name)}/configupload/`,
        data.content,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
          timeout: UPLOAD_TIMEOUT_MS,
        },
      )
    },
    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: ['projects'],
      })
    },
  })
}
