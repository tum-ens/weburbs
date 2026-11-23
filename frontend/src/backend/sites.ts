import type { RouteLocationNormalized } from 'vue-router'
import { useCSRF } from '@/backend/security'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import type { Site } from '@/backend/interfaces'
import axios from 'axios'
import { computed } from 'vue'

export function useUpdateSite(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: { name: string; site: Site }) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${data.name}/`,
        data.site,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess() {
      client.invalidateQueries({
        queryKey: ['projects', 'sites', computed(() => route.params.proj)],
      })
    },
  })
}

export function useDeleteSite(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (site_name: string) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${site_name}/delete/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess(_data, site_name) {
      client.invalidateQueries({
        queryKey: ['projects', 'sites', computed(() => route.params.proj)],
      })
      client.invalidateQueries({
        queryKey: ['transmissions', route.params.proj],
      })
      client.removeQueries({
        queryKey: ['commodities', route.params.proj, site_name],
      })
      client.removeQueries({
        queryKey: ['processes', route.params.proj, site_name],
      })
      client.removeQueries({
        queryKey: ['storage', route.params.proj, site_name],
      })
    },
  })
}

export function useSites(route: RouteLocationNormalized) {
  return useQuery({
    queryKey: ['projects', 'sites', computed(() => route.params.proj)],
    queryFn: () =>
      axios
        .get<Site[]>(`/api/project/${route.params.proj}/sites/`)
        .then(res => res.data),
  })
}
