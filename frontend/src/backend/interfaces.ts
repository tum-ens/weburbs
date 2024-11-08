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
  deprecation: number
  areapercap: number
  in: string[]
  out: string[]
}
