export interface Project {
  name: string
  description: string
}

export interface GlobalConfig {
  property: string
  value: number
  description: string
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
