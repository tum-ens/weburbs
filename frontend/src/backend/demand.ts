import type { RouteLocationNormalized } from 'vue-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useCSRF } from '@/backend/security'
import axios from 'axios'
import type {
  Commodity,
  Demand,
  DemandConfig,
  DemandProfile,
  Process,
  Site,
} from '@/backend/interfaces'
import { computed } from 'vue'

export function useGetDefDemand() {
  return useQuery({
    queryKey: ['defDemand'],
    queryFn: () =>
      axios
        .get<Process[]>(`/api/def_demands/`)
        .then<Demand[]>(response => response.data),
  })
}

export function useGetDemand(
  route: RouteLocationNormalized,
  site: Site,
  commodity: Commodity,
) {
  return useQuery({
    queryKey: [
      'Demand',
      computed(() => route.params.proj),
      site.name,
      commodity.name,
    ],
    queryFn: () =>
      axios
        .get(
          `/api/project/${route.params.proj}/site/${site.name}/demand/${commodity.name}/`,
        )
        .then<DemandProfile[]>(response => response.data),
  })
}

export function useUpdateDemand(
  route: RouteLocationNormalized,
  site: Site,
  commodity: Commodity,
) {
  const client = useQueryClient()
  const { data: csrf } = useCSRF()
  return useMutation({
    mutationFn: (config: DemandConfig[]) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${site.name}/demand/${commodity.name}/update/`,
        config,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    async onSuccess() {
      await client.invalidateQueries({
        queryKey: ['Demand', route.params.proj, site.name, commodity.name],
      })
    },
  })
}
