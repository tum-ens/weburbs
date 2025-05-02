import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import axios from 'axios'
import type { Transmission } from '@/backend/interfaces'
import type { RouteLocationNormalized } from 'vue-router'
import { computed } from 'vue'
import { useCSRF } from '@/backend/security'
import type { Transition } from 'plotly.js'

export function useTransmission(route: RouteLocationNormalized) {
  return useQuery({
    queryKey: ['transmissions', computed(() => route.params.proj)],
    queryFn: () =>
      axios
        .get<Transition[]>(`/api/project/${route.params.proj}/transmission/`)
        .then(response => response.data),
  })
}

export function useUpdateTransmission(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      sitein_name: string
      siteout_name: string
      com_name: string
      transmission: Transmission
    }) =>
      axios.post(
        `/api/project/${route.params.proj}/transmission/${data.sitein_name}/${data.siteout_name}/${data.com_name}/update/`,
        data.transmission,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess() {
      client.invalidateQueries({
        queryKey: ['transmissions', route.params.proj],
      })
    },
  })
}

export function useDeleteTransmission(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      sitein_name: string
      siteout_name: string
      com_name: string
    }) =>
      axios.post(
        `/api/project/${route.params.proj}/transmission/${data.sitein_name}/${data.siteout_name}/${data.com_name}/delete/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess(data, vars) {
      client.invalidateQueries({
        queryKey: ['transmission', route.params.proj],
      })
    },
  })
}
