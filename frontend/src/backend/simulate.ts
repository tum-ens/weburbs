import type { RouteLocationNormalized } from 'vue-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useCSRF } from '@/backend/security'
import axios from 'axios'
import { computed } from 'vue'
import type {
  Simulation,
  SimulationInfo,
  SimulationProgress,
} from '@/backend/interfaces'

export enum GenerateReport {
  SUMMARY = 'summary',
  FULL = 'full',
}

export enum Solver {
  GUROBI = 'gurobi',
  GLPK = 'glpk',
}

export function useGetSimulationInfo(route: RouteLocationNormalized) {
  return useQuery({
    queryKey: ['simulationInfo', computed(() => route.params.proj)],
    queryFn: () =>
      axios
        .get(`/api/project/${route.params.proj}/simulate/info/`, {})
        .then<{ c_timesteps: number }>(response => response.data),
  })
}

export function useTriggerSimulation(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      generate_report,
      generate_h5,
      solver,
      timestep_from,
      timestep_to,
      timeseries_commodity_types,
    }: {
      generate_report: GenerateReport | undefined
      generate_h5: boolean | undefined
      solver: Solver | undefined
      timestep_from?: number
      timestep_to?: number
      timeseries_commodity_types?: string[]
    }) => {
      const body: Record<string, unknown> = {
        generate_report: !!generate_report ? generate_report : undefined,
        generate_h5: !!generate_h5 ? generate_h5 : undefined,
        solver: !!solver ? solver : undefined,
      }
      if (timestep_from !== undefined) body.timestep_from = timestep_from
      if (timestep_to !== undefined) body.timestep_to = timestep_to
      if (timeseries_commodity_types !== undefined) {
        body.timeseries_commodity_types = timeseries_commodity_types
      }
      return axios
        .post(`/api/project/${route.params.proj}/simulate/trigger/`, body, {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        })
        .then(response => response.data)
        .then(res => {
          return {
            ...res,
            timestamp: new Date(res.timestamp),
          }
        })
    },
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

export function useGetSimulationProgress(
  route: RouteLocationNormalized,
  enabled: { value: boolean } = { value: true },
) {
  return useQuery({
    queryKey: [
      'simulationProgress',
      computed(() => route.params.proj),
      computed(() => route.params.simId),
    ],
    enabled: computed(() => !!route.params.simId && enabled.value),
    refetchInterval: query => {
      if (query.state.data?.cancelled) return false
      if (query.state.data?.failed_at) return false
      return enabled.value ? 1500 : false
    },
    retry: false,
    queryFn: () =>
      axios
        .get(
          `/api/project/${route.params.proj}/simulate/result/${route.params.simId}/progress/`,
          {},
        )
        .then(response => {
          if (response.status === 204) return null
          return response.data as SimulationProgress
        })
        .catch(error => {
          if (axios.isAxiosError(error) && error.response?.status === 204) {
            return null
          }
          throw error
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
    retryDelay: 1000,
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
          `/api/project/${route.params.proj}/simulate/result/${route.params.simId}/logs/`,
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
          `/api/project/${route.params.proj}/simulate/result/${route.params.simId}/config/`,
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

export function useStopSimulation(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (simId: string) =>
      axios
        .post(
          `/api/project/${route.params.proj}/simulate/result/${simId}/stop/`,
          {},
          {
            headers: {
              'X-CSRFToken': csrf.value,
            },
          },
        )
        .then(response => response.data),
    onSuccess(_data, simId) {
      queryClient.invalidateQueries({
        queryKey: ['simulations', <string>route.params.proj],
      })
      queryClient.invalidateQueries({
        queryKey: ['simulation', <string>route.params.proj, simId],
      })
      queryClient.invalidateQueries({
        queryKey: ['simulationLogs', <string>route.params.proj, simId],
      })
      queryClient.invalidateQueries({
        queryKey: ['simulationProgress', <string>route.params.proj, simId],
      })
    },
  })
}

export function useComputeIIS(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  return useMutation({
    mutationFn: (simId: string) =>
      axios
        .post(
          `/api/project/${route.params.proj}/simulate/result/${simId}/compute_iis/`,
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

export function useUpdateSimulationName(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (name: string) =>
      axios
        .post(
          `/api/project/${route.params.proj}/simulate/result/${route.params.simId}/name/${name}/`,
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
      queryClient.invalidateQueries({
        queryKey: [
          'simulation',
          <string>route.params.proj,
          <string>route.params.simId,
        ],
      })
    },
  })
}
