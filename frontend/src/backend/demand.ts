import type { RouteLocationNormalized } from 'vue-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useCSRF } from '@/backend/security'
import axios from 'axios'
import type {Commodity, Demand, Process, Site} from '@/backend/interfaces'
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
        .get<Steps>(
          `/api/project/${route.params.proj}/site/${site.name}/demand/${commodity.name}/`,
        )
        .then(response => response.data),
  })
}

export function useGenerateDemand(
  route: RouteLocationNormalized,
  site: Site,
  commodity: Commodity,
) {
  const client = useQueryClient()
  const { data: csrf } = useCSRF()
  return useMutation({
    mutationFn: () =>
      axios.post(
        `/api/project/${route.params.proj}/site/${site.name}/demand/${commodity.name}/generate/`,
        {},
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

export function useDeleteDemand(
  route: RouteLocationNormalized,
  site: Site,
  commodity: Commodity,
) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: () =>
      axios.delete(
        `/api/project/${route.params.proj}/site/${site.name}/demand/${commodity.name}/`,
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
