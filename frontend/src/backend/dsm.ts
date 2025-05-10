import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import axios from 'axios'
import type { DSM, Site } from '@/backend/interfaces'
import type { RouteLocationNormalized } from 'vue-router'
import { computed } from 'vue'
import { useCSRF } from '@/backend/security'

export function useDSM(route: RouteLocationNormalized, site: Site) {
  return useQuery({
    queryKey: ['dsm', computed(() => route.params.proj), site.name],
    queryFn: () =>
      axios
        .get<DSM[]>(`/api/project/${route.params.proj}/site/${site.name}/dsm/`)
        .then(response => response.data),
  })
}

export function useUpdateDSM(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: { site_name: string; com_name: string; dsm: DSM }) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${data.site_name}/dsm/${data.com_name}/update/`,
        data.dsm,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess(data, vars) {
      client.invalidateQueries({
        queryKey: ['dsm', route.params.proj, vars.site_name],
      })
    },
  })
}

export function useDeleteDSM(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: { site_name: string; com_name: string }) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${data.site_name}/dsm/${data.com_name}/delete/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess(data, vars) {
      client.invalidateQueries({
        queryKey: ['dsm', route.params.proj, vars.site_name],
      })
    },
  })
}
