import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import axios from 'axios'
import type { Site, Storage } from '@/backend/interfaces'
import type { RouteLocationNormalized } from 'vue-router'
import { computed } from 'vue'
import { useCSRF } from '@/backend/security'

export function useDefStorage() {
  return useQuery({
    queryKey: ['defStorage'],
    queryFn: () =>
      axios.get<Storage[]>(`/api/def_storage/`).then(response => response.data),
  })
}

export function useStorage(route: RouteLocationNormalized, site: Site) {
  return useQuery({
    queryKey: ['storage', computed(() => route.params.proj), site.name],
    queryFn: () =>
      axios
        .get<
          Storage[]
        >(`/api/project/${route.params.proj}/site/${site.name}/storage/`)
        .then(response => response.data),
  })
}

export function useAddDefStorage(route: RouteLocationNormalized) {
  const queryClient = useQueryClient()
  const { data: csrf } = useCSRF()
  return useMutation({
    mutationFn: (data: { site_name: string; def_storage_name: string }) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${data.site_name}/def_storage/${data.def_storage_name}/add/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess(data, vars) {
      queryClient.invalidateQueries({
        queryKey: ['storage', route.params.proj, vars.site_name],
      })
    },
  })
}
