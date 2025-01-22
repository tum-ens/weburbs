import type { RouteLocationNormalized } from 'vue-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed } from 'vue'
import axios from 'axios'
import type { Commodity, Site } from '@/backend/interfaces'
import { useCSRF } from '@/backend/security'

export function useDefCommodities() {
  return useQuery({
    queryKey: ['defCommodities'],
    queryFn: () =>
      axios
        .get<Commodity[]>(`/api/def_commodities/`)
        .then(response => response.data),
  })
}

export function useCommodities(route: RouteLocationNormalized, site: Site) {
  return useProjectSiteCommodities(route, site.name)
}

export function useProjectSiteCommodities(
  route: RouteLocationNormalized,
  site: string,
) {
  return useQuery({
    queryKey: ['commodities', computed(() => route.params.proj), site],
    queryFn: () =>
      axios
        .get<
          Commodity[]
        >(`/api/project/${route.params.proj}/site/${site}/commodities/`)
        .then(res => res.data),
  })
}

export function useAddDefCommodity(route: RouteLocationNormalized) {
  const queryClient = useQueryClient()
  const { data: csrf } = useCSRF()
  return useMutation({
    mutationFn: (data: { site_name: string; def_com_name: string }) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${data.site_name}/def_commodities/${data.def_com_name}/add/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess(data, vars) {
      queryClient.invalidateQueries({
        queryKey: ['commodities', route.params.proj, vars.site_name],
      })
    },
  })
}

export function useUpdateCommodity(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      site_name: string
      commodity_name: string
      commodity: Commodity
    }) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${data.site_name}/commodity/${data.commodity_name}/update/`,
        data.commodity,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess(data, vars) {
      client.invalidateQueries({
        queryKey: ['commodities', route.params.proj, vars.site_name],
      })
    },
  })
}

export function useDeleteCommodity(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: { site_name: string; commodity_name: string }) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${data.site_name}/commodity/${data.commodity_name}/delete/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess(data, vars) {
      client.invalidateQueries({
        queryKey: ['commodities', route.params.proj, vars.site_name],
      })
    },
  })
}
