import type { RouteLocationNormalized } from 'vue-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useCSRF } from '@/backend/security'
import axios from 'axios'
import { computed } from 'vue'
import type { Commodity, Site, SupIm } from '@/backend/interfaces'

export function useGetSupIm(
  route: RouteLocationNormalized,
  site: Site,
  commodity: Commodity,
) {
  return useQuery({
    queryKey: [
      'SupIm',
      computed(() => route.params.proj),
      site.name,
      commodity.name,
    ],
    queryFn: () =>
      axios
        .get<SupIm>(
          `/api/project/${route.params.proj}/site/${site.name}/supim/${commodity.name}/`,
        )
        .then(response => response.data),
  })
}

export function useGenerateSupIm(
  route: RouteLocationNormalized,
  site: Site,
  commodity: Commodity,
) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: { type: string }) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${site.name}/supim/${commodity.name}/query/${data.type}/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    async onSuccess() {
      await client.invalidateQueries({
        queryKey: ['SupIm', route.params.proj, site.name, commodity.name],
      })
    },
  })
}
