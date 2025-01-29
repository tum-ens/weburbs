import type { RouteLocationNormalized } from 'vue-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useCSRF } from '@/backend/security'
import axios from 'axios'
import { computed } from 'vue'
import type { Simulation, SimulationInfo } from '@/backend/interfaces'

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
        .then<SimulationInfo[]>(response => {
          return response.data.map((res: SimulationInfo) => {
            return {
              ...res,
              timestamp: new Date(res.timestamp),
            }
          })
        }),
  })
}

export function useGetSimulation(route: RouteLocationNormalized) {
  const queryClient = useQueryClient()
  return useQuery({
    queryKey: [
      'simulation',
      computed(() => route.params.proj),
      computed(() => route.params.simId),
    ],
    enabled: computed(() => !!route.params.simId),
    retry: true,
    retryDelay: 2000,
    queryFn: () =>
      axios
        .get(
          `/api/project/${route.params.proj}/simulate/result/${route.params.simId}/`,
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
        .then<Simulation>(response => {
          return {
            ...response.data,
            timestamp: new Date(response.data.timestamp),
          }
        }),
  })
}

export function useGetSimulationLogs(route: RouteLocationNormalized) {
  const queryClient = useQueryClient()
  return useQuery({
    queryKey: [
      'simulationLogs',
      computed(() => route.params.proj),
      computed(() => route.params.simId),
    ],
    enabled: computed(() => !!route.params.simId),
    retry: true,
    retryDelay: 2000,
    queryFn: () =>
      axios
        .get(
          `/api/project/${route.params.proj}/simulate/result/${route.params.simId}/logs`,
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

export function useGetSimulationConfig(route: RouteLocationNormalized) {
  const queryClient = useQueryClient()
  return useQuery({
    queryKey: [
      'simulationConfig',
      computed(() => route.params.proj),
      computed(() => route.params.simId),
    ],
    enabled: computed(() => !!route.params.simId),
    retry: true,
    retryDelay: 2000,
    queryFn: () =>
      axios
        .get(
          `/api/project/${route.params.proj}/simulate/result/${route.params.simId}/config`,
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
