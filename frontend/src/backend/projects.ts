import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import axios from 'axios'
import { useCSRF } from '@/backend/security'
import type { Project } from '@/backend/interfaces'
import type { RouteLocationNormalized } from 'vue-router'
import { computed } from 'vue'

export function useUpdateProject(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: Project) =>
      axios.post(
        `/api/project/${route.params.proj || data.name}/update/`,
        data,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    async onSuccess() {
      await client.invalidateQueries({ queryKey: ['projects'] })
    },
  })
}

export function useProjectList() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => axios.get<Project[]>(`/api/projects/`).then(res => res.data),
  })
}

export function useProjectDetails(route: RouteLocationNormalized) {
  return useQuery({
    queryKey: ['projectDetails', computed(() => route.params.proj)],
    queryFn: () =>
      axios
        .get<Project>(`/api/project/${route.params.proj}/`)
        .then(res => res.data),
  })
}
