import type { RouteLocationNormalized } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'
import axios from 'axios'
import type { Commodity } from '@/backend/interfaces'

export function useDefCommodities() {
  return useQuery({
    queryKey: ['defCommodities'],
    queryFn: () =>
      axios
        .get<Commodity[]>(`/api/def_commodities/`)
        .then(response => response.data),
  })
}

export function useProjectSiteCommodities(
  route: RouteLocationNormalized,
  site: string,
) {
  return useQuery({
    queryKey: [
      'projects',
      'commodities',
      computed(() => route.params.proj),
      site,
    ],
    queryFn: () =>
      axios
        .get<
          Commodity[]
        >(`/api/project/${route.params.proj}/site/${site}/commodities`)
        .then(res => res.data),
  })
}
