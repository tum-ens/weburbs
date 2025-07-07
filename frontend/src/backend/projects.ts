import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import axios from 'axios'
import { useCSRF } from '@/backend/security'
import type { Project, ProjectName } from '@/backend/interfaces'
import type { RouteLocationNormalized } from 'vue-router'
import { computed } from 'vue'

export function useUpdateProject(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: Project) =>
      axios.post(`/api/project/${route.params.proj || '__new'}/update/`, data, {
        headers: {
          'X-CSRFToken': csrf.value,
        },
      }),
    async onSuccess() {
      await client.invalidateQueries({ queryKey: ['projects'] })
    },
  })
}

export function useDefProjects() {
  return useQuery({
    queryKey: ['defProjects'],
    queryFn: () =>
      axios.get<ProjectName[]>(`/api/def_projects/`).then(res => res.data),
  })
}

export function useProjectList() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => axios.get<Project[]>(`/api/projects/`).then(res => res.data),
  })
}

export function useLoadDefProject() {
  const queryClient = useQueryClient()
  const { data: csrf } = useCSRF()
  return useMutation({
    mutationFn: (name: string) =>
      axios.post(
        `/api/def_projects/${name}/load/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: ['projects'],
      })
    },
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

export function useDeleteProject(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: () =>
      axios.post(
        `/api/project/${route.params.proj}/delete/`,
        {},
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
