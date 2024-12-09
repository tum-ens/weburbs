import type { RouteLocationNormalized } from 'vue-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useCSRF } from '@/backend/security'
import axios from 'axios'
import { computed, type Ref } from 'vue'
import type { SimulationResult } from '@/backend/interfaces'

export function useTriggerSimulation(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const queryClient = useQueryClient()
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
        .then(response => response.data)
        .then(res => {
          return {
            ...res,
            timestamp: new Date(res.timestamp),
          }
        }),
    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: ['simulations', <string>route.params.projId],
      })
    },
  })
}

export function useListSimulations(route: RouteLocationNormalized) {
  return useQuery({
    queryKey: ['simulations', computed(() => route.params.projId)],
    queryFn: () =>
      axios
        .get(`/api/project/${route.params.proj}/simulate/results/`, {})
        .then<SimulationResult[]>(response => {
          return response.data.map((res: SimulationResult) => {
            return {
              ...res,
              timestamp: new Date(res.timestamp),
            }
          })
        }),
  })
}

export function useGetSimulation(
  route: RouteLocationNormalized,
  result: Ref<SimulationResult | undefined>,
) {
  const queryClient = useQueryClient()
  return useQuery({
    queryKey: [
      'simulation',
      computed(() => route.params.projId),
      computed(() => result.value?.id),
    ],
    enabled: computed(() => !!result.value),
    retry: true,
    retryDelay: 2000,
    queryFn: () =>
      axios
        .get(
          `/api/project/${route.params.proj}/simulate/result/${result.value?.id}/`,
          {},
        )
        .then(response => {
          if (response.status === 204)
            throw new Error(
              'Fail if no data available to enable automatic refetch',
            )
          queryClient.invalidateQueries({
            queryKey: ['simulations', <string>route.params.projId],
          })
          return response
        })
        .then(response => response.data),
  })
}
