import type { RouteLocationNormalized } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'
import axios from 'axios'
import type { Site } from '@/backend/interfaces'

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
          Site[]
        >(`/api/project/${route.params.proj}/site/${site}/commodities`)
        .then(res => res.data),
  })
}
