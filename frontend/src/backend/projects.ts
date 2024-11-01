import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import axios from 'axios'
import { useCSRF } from '@/backend/security'
import type { GlobalConfig, Project, Site } from '@/backend/interfaces'
import type { RouteLocationNormalized } from 'vue-router'
import { computed } from 'vue'

export function useCreateProject() {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: Project) =>
      axios.post(`/api/project/create/`, data, {
        headers: {
          'X-CSRFToken': csrf.value,
        },
      }),
    onSuccess() {
      client.invalidateQueries({ queryKey: ['projects'] })
    },
  })
}

export function useProjectList() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () =>
      axios.get<Project[]>(`/api/project/list/`).then(res => res.data),
  })
}

export function useUpdateGlobals(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: GlobalConfig[]) =>
      axios.post(
        `/api/project/details/${route.params.proj}/update_globals/`,
        data,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess() {
      client.invalidateQueries({
        queryKey: ['projects', 'globals', computed(() => route.params.proj)],
      })
    },
  })
}

export function useProjectGlobals(route: RouteLocationNormalized) {
  return useQuery({
    queryKey: ['projects', 'globals', computed(() => route.params.proj)],
    queryFn: () =>
      axios
        .get<
          GlobalConfig[]
        >(`/api/project/details/${route.params.proj}/globals/`)
        .then(res => res.data),
  })
}

export function useCreateSite(route: RouteLocationNormalized) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: Site) =>
      axios.post(
        `/api/project/details/${route.params.proj}/create_site/`,
        data,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess() {
      client.invalidateQueries({
        queryKey: ['projects', 'sites', computed(() => route.params.proj)],
      })
    },
  })
}

export function useUpdateSite(route: RouteLocationNormalized, site: string) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (data: Site) =>
      axios.post(
        `/api/project/details/${route.params.proj}/site/${site}/update/`,
        data,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    onSuccess() {
      client.invalidateQueries({
        queryKey: ['projects', 'sites', computed(() => route.params.proj)],
      })
    },
  })
}

export function useProjectSites(route: RouteLocationNormalized) {
  return useQuery({
    queryKey: ['projects', 'sites', computed(() => route.params.proj)],
    queryFn: () =>
      axios
        .get<Site[]>(`/api/project/details/${route.params.proj}/sites/`)
        .then(res => res.data),
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
          Site[]
        >(`/api/project/details/${route.params.proj}/site/${site}/commodities`)
        .then(res => res.data),
  })
}
