import type { RouteLocationNormalized } from 'vue-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useCSRF } from '@/backend/security'
import axios from 'axios'
import { computed } from 'vue'
import {
  BuySellPriceType,
  type Commodity,
  type Site,
  type Steps,
} from '@/backend/interfaces'

export function useGetBuySellPrice(
  route: RouteLocationNormalized,
  site: Site,
  commodity: Commodity,
) {
  return useQuery({
    queryKey: [
      'BuySellPrice',
      computed(() => route.params.proj),
      site.name,
      commodity.name,
    ],
    queryFn: () =>
      axios
        .get<Steps>(
          `/api/project/${route.params.proj}/site/${site.name}/buysellprice/${commodity.name}/`,
        )
        .then(response => response.data),
  })
}

export function useUploadBuySellPrice(
  route: RouteLocationNormalized,
  site: Site,
  commodity: Commodity,
  type: BuySellPriceType,
) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (steps: number[]) =>
      axios.post(
        `/api/project/${route.params.proj}/site/${site.name}/buysellprice/${commodity.name}/upload/${BuySellPriceType[type]}/`,
        steps,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    async onSuccess() {
      await client.invalidateQueries({
        queryKey: [
          'BuySellPrice',
          route.params.proj,
          site.name,
          commodity.name,
        ],
      })
    },
  })
}

export function useDeleteBuySellPrice(
  route: RouteLocationNormalized,
  site: Site,
  commodity: Commodity,
) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: () =>
      axios.delete(
        `/api/project/${route.params.proj}/site/${site.name}/buysellprice/${commodity.name}/`,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    async onSuccess() {
      await client.invalidateQueries({
        queryKey: [
          'BuySellPrice',
          route.params.proj,
          site.name,
          commodity.name,
        ],
      })
    },
  })
}
