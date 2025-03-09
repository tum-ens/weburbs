import { useMutation, useQueryClient } from '@tanstack/vue-query'
import axios from 'axios'
import { useCSRF } from '@/backend/security'

export function useUploadExcel() {
  const queryClient = useQueryClient()
  const { data: csrf } = useCSRF()
  return useMutation({
    mutationFn: (data: { project_name: string; file: Blob }) => {
      const formData = new FormData()
      formData.append('file', data.file)
      return axios.post(
        `/api/project/${data.project_name}/excelupload`,
        formData,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
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
