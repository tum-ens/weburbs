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
