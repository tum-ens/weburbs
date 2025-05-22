import type { RouteLocationNormalized } from 'vue-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useCSRF } from '@/backend/security'
import axios from 'axios'
import { computed } from 'vue'
import { type BuySellPrice, BuySellPriceType } from '@/backend/interfaces'

export function useGetBuySellPrices(route: RouteLocationNormalized) {
  return useQuery({
    queryKey: ['BuySellPrice', computed(() => route.params.proj)],
    queryFn: () =>
      axios
        .get<BuySellPrice[]>(`/api/project/${route.params.proj}/buysellprice/`)
        .then(response => response.data),
  })
}

export function useUploadBuySellPrice(
  route: RouteLocationNormalized,
  bsp: BuySellPrice,
) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: (steps: number[]) =>
      axios.post(
        `/api/project/${route.params.proj}/buysellprice/${bsp.name}/upload/${BuySellPriceType[bsp.type]}/`,
        steps,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    async onSuccess() {
      await client.invalidateQueries({
        queryKey: ['BuySellPrice', route.params.proj],
      })
    },
  })
}

export function useDeleteBuySellPrice(
  route: RouteLocationNormalized,
  bsp: BuySellPrice,
) {
  const { data: csrf } = useCSRF()
  const client = useQueryClient()
  return useMutation({
    mutationFn: () =>
      axios.delete(
        `/api/project/${route.params.proj}/buysellprice/${bsp.name}/delete/${BuySellPriceType[bsp.type]}/`,
        {
          headers: {
            'X-CSRFToken': csrf.value,
          },
        },
      ),
    async onSuccess() {
      await client.invalidateQueries({
        queryKey: ['BuySellPrice', route.params.proj],
      })
    },
  })
}
