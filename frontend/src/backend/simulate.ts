import type { RouteLocationNormalized } from 'vue-router'
import { useMutation } from '@tanstack/vue-query'
import { useCSRF } from '@/backend/security'
import axios from 'axios'

export function useTriggerSimulation(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  return useMutation({
    mutationFn: () =>
      axios
        .post(
          `/api/project/${route.params.proj}/simulate/trigger/`,
          {},
          {
            headers: {
              'X-CSRFToken': csrf.value,
            },
          },
        )
        .then(response => response.data),
  })
}
