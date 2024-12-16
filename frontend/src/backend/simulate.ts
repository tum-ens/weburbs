import type { RouteLocationNormalized } from 'vue-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useCSRF } from '@/backend/security'
import axios from 'axios'
import { computed, type Ref } from 'vue'
import type { SimulationDetails, SimulationResult } from '@/backend/interfaces'

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
        queryKey: ['simulations', <string>route.params.proj],
      })
    },
  })
}

export function useListSimulations(route: RouteLocationNormalized) {
  return useQuery({
    queryKey: ['simulations', computed(() => route.params.proj)],
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
      computed(() => route.params.proj),
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
            queryKey: ['simulations', <string>route.params.proj],
          })
          return response
        })
        .then<SimulationDetails>(response => response.data),
  })
}

export function useGetSimulationLogs(
  route: RouteLocationNormalized,
  result: SimulationResult,
) {
  const queryClient = useQueryClient()
  return useQuery({
    queryKey: [
      'simulationLogs',
      computed(() => route.params.proj),
      computed(() => result.id),
    ],
    enabled: computed(() => !!result),
    retry: true,
    retryDelay: 2000,
    queryFn: () =>
      axios
        .get(
          `/api/project/${route.params.proj}/simulate/result/${result.id}/logs`,
          {},
        )
        .then(response => {
          if (response.status === 204)
            throw new Error(
              'Fail if no data available to enable automatic refetch',
            )
          queryClient.invalidateQueries({
            queryKey: ['simulations', <string>route.params.proj],
          })
          return response
        })
        .then<string>(response => response.data),
  })
}

export function useGetSimulationConfig(
  route: RouteLocationNormalized,
  result: SimulationResult,
) {
  const queryClient = useQueryClient()
  return useQuery({
    queryKey: [
      'simulationConfig',
      computed(() => route.params.proj),
      computed(() => result.id),
    ],
    enabled: computed(() => !!result),
    retry: true,
    retryDelay: 2000,
    queryFn: () =>
      axios
        .get(
          `/api/project/${route.params.proj}/simulate/result/${result.id}/config`,
          {},
        )
        .then(response => {
          if (response.status === 204)
            throw new Error(
              'Fail if no data available to enable automatic refetch',
            )
          queryClient.invalidateQueries({
            queryKey: ['simulations', <string>route.params.proj],
          })
          return response
        })
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .then<any>(response => response.data),
  })
}
