export interface Project {
  name: string
  description: string
  co2limit: number
  costlimit: number
}

export interface Site {
  name: string
  area: number
  long: number
  lat: number
}

export interface Commodity {
  site: string
  name: string
  type: string
  price: number
  max: number
  maxperhour: number
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
