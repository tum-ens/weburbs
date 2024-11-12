import type { RouteLocationNormalized } from 'vue-router'
import { useMutation } from '@tanstack/vue-query'
import { useCSRF } from '@/backend/security'
import axios from 'axios'

export function useGenerateDemand(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  return useMutation({
    mutationFn: (data: { site_name: string; com_name: string }) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${data.site_name}/demand/${data.com_name}/generate/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    // TODO invalidate caches
  })
}
