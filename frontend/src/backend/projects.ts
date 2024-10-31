import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import axios from 'axios'
import { useCSRF } from '@/backend/security'

export function useCreateProject() {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: { name: string; description: string }) =>
      axios.post('/api/project/create/', data, {
        headers: {
          'X-CSRFToken': csrf.value,
        },
      }),
    onSuccess() {
      client.invalidateQueries({ queryKey: ['projects'] })
    },
  })
}

export function useProjectList() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => axios.get('/api/project/list/').then(res => res.data),
  })
}
