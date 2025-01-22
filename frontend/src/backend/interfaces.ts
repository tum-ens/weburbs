export interface Project {
  name: string
  description: string
  co2limit: number
  costlimit: number
}

export interface Site {
  name: string
  area?: number
  lon: number
  lat: number
}

export enum CommodityType {
  SupIm = 1,
  Demand = 2,
  Stock = 3,
  Env = 4,
  Buy = 5,
  Sell = 6,
}

export const CommodityTypes = ['SupIm', 'Demand', 'Stock', 'Env', 'Buy', 'Sell']

export function commodityTypeToName(type: CommodityType): string {
  return CommodityTypes[type - 1]
}

export interface Commodity {
  site: string
  name: string
  type: CommodityType
  price: number | undefined
  max: number | undefined
  maxperhour: number | undefined
}

export interface ProcessCommodity {
  name: string
  ratio: number
  ratiomin: number
}

export interface Process {
  name: string
  description: string
  instcap: number
  caplo: number
  capup: number
  maxgrad: number
  minfraction: number
  invcost: number
  fixcost: number
  varcost: number
  wacc: number
  depreciation: number
  areapercap: number | undefined
  in: ProcessCommodity[]
  out: ProcessCommodity[]
}

export interface Storage {
  name: string
  description: string
  instcapc: number
  caploc: number
  capupc: number
  instcapp: number
  caplop: number
  capupp: number
  effin: number
  effout: number
  invcostp: number
  invcostc: number
  fixcostp: number
  fixcostc: number
  varcostp: number
  varcostc: number
  wacc: number
  depreciation: number
  init: number
  discharge: number
  epratio: number | null
  commodity: string
}

export interface Steps {
  data?: number[]
}

export interface Demand {
  name: string
  description: string
}

export interface DemandConfig extends Demand {
  quantity: number
}

export interface DemandProfile extends DemandConfig {
  steps: number[]
}

export enum SimulationResultStatus {
  Optimal = 1,
  Infeasible = 2,
  Error = 3,
}

export interface SimulationResult {
  id: string
  timestamp: Date
  completed: boolean
  status: SimulationResultStatus | null
}

export interface SimulationDetails extends SimulationResult {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  result: any
}
