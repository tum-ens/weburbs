import type { RouteLocationNormalized } from 'vue-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useCSRF } from '@/backend/security'
import axios from 'axios'
import { computed } from 'vue'
import { type Process, type Site, type Steps } from '@/backend/interfaces'

export function useGetTimeVarEff(
  route: RouteLocationNormalized,
  site: Site,
  process: Process,
) {
  return useQuery({
    queryKey: [
      'TimeVarEff',
      computed(() => route.params.proj),
      site.name,
      process.name,
    ],
    queryFn: () =>
      axios
        .get<Steps>(
          `/api/project/${route.params.proj}/site/${site.name}/timevareff/${process.name}/`,
        )
        .then(response => response.data),
  })
}

export function useUploadTimeVarEff(
  route: RouteLocationNormalized,
  site: Site,
  process: Process,
) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (steps: number[]) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${site.name}/timevareff/${process.name}/upload/`,
        steps,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    async onSuccess() {
      await client.invalidateQueries({
        queryKey: ['TimeVarEff', route.params.proj, site.name, process.name],
      })
    },
  })
}

export function useDeleteTimeVarEff(
  route: RouteLocationNormalized,
  site: Site,
  process: Process,
) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: () =>
      axios.delete(
        `/api/project/${route.params.proj}/site/${site.name}/timevareff/${process.name}/`,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    async onSuccess() {
      await client.invalidateQueries({
        queryKey: ['TimeVarEff', route.params.proj, site.name, process.name],
      })
    },
  })
}
