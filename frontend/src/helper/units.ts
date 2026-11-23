export type DisplayScale = 'kW' | 'MW'

type UnitPrefix = 'k' | 'M'

type CommodityLike = {
  Type?: string
  type?: string | number
  unitR?: string
  unitC?: string
}

function strip(unit?: string | null): string {
  return (unit || '').replace(/\s/g, '')
}

/** kW family → 'k', MW family → 'M'. Energy units (kWh/MWh) return null. */
export function powerPrefix(unit?: string | null): UnitPrefix | null {
  const u = strip(unit)
  if (!u || /^kWh/i.test(u) || /^MWh/i.test(u)) return null
  if (/^kW/i.test(u)) return 'k'
  if (/^MW/i.test(u)) return 'M'
  return null
}

export function energyPrefix(unit?: string | null): UnitPrefix | null {
  const u = strip(unit)
  if (/^kWh/i.test(u)) return 'k'
  if (/^MWh/i.test(u)) return 'M'
  return null
}

export function massPrefix(unit?: string | null): UnitPrefix | null {
  const u = (unit || '').toLowerCase()
  if (!u) return null
  if (u.includes('kg')) return 'k'
  if (u.includes('tonne') || /(^|[^a-z])t([^a-z]|$)/i.test(u)) return 'M'
  return null
}

function scaleFactor(from: UnitPrefix | null, to: UnitPrefix): number | null {
  if (!from) return null
  if (from === to) return 1
  if (from === 'M' && to === 'k') return 1000
  if (from === 'k' && to === 'M') return 0.001
  return 1
}

function applyScale(
  value: number,
  from: UnitPrefix | null,
  display?: DisplayScale,
): number {
  if (!display) return value
  const factor = scaleFactor(from, display === 'kW' ? 'k' : 'M')
  return factor == null ? value : value * factor
}

export function convertToDisplayPower(
  value: number,
  nativeUnit: string | undefined,
  display?: DisplayScale,
): number {
  return applyScale(value, powerPrefix(nativeUnit), display)
}

export function convertToDisplayEnergy(
  value: number,
  nativeUnit: string | undefined,
  display?: DisplayScale,
): number {
  return applyScale(value, energyPrefix(nativeUnit), display)
}

export function convertToDisplayMass(
  value: number,
  nativeUnit: string | undefined,
  display?: DisplayScale,
): number {
  return applyScale(value, massPrefix(nativeUnit), display)
}

export function displayPowerLabel(
  nativeUnit: string | undefined,
  display?: DisplayScale,
): string {
  const prefix = powerPrefix(nativeUnit)
  if (!prefix) return nativeUnit || display || 'MW'
  if (!display) return nativeUnit || 'MW'
  return display + (nativeUnit || '').replace(/^\s*(kW|MW)/i, '')
}

export function displayEnergyLabel(
  nativeUnit: string | undefined,
  display?: DisplayScale,
): string {
  const prefix = energyPrefix(nativeUnit)
  if (!prefix) return nativeUnit || (display === 'kW' ? 'kWh' : 'MWh')
  if (!display) return nativeUnit || 'MWh'
  return (display === 'kW' ? 'kWh' : 'MWh') +
    (nativeUnit || '').replace(/^\s*(kWh|MWh)/i, '')
}

export function displayMassLabel(
  nativeUnit: string | undefined,
  display?: DisplayScale,
): string {
  const prefix = massPrefix(nativeUnit)
  if (!prefix) return nativeUnit || (display === 'kW' ? 'kg' : 'tonnes')
  if (!display) return nativeUnit || 'tonnes'
  return display === 'kW' ? 'kg' : 'tonnes'
}

export function processOutputUnit(
  procConf:
    | { commodity?: Record<string, { Direction?: string }> }
    | undefined,
  commodities: Record<string, CommodityLike>,
): { unitR?: string; unitC?: string } {
  if (!procConf?.commodity) return {}
  const outs = Object.entries(procConf.commodity).filter(
    ([, spec]) => spec?.Direction === 'Out',
  )
  const pick = (name: string) => {
    const com = commodities[name]
    return com ? { unitR: com.unitR, unitC: com.unitC } : {}
  }
  const demand = outs.find(([name]) => {
    const t = commodities[name]?.Type || commodities[name]?.type
    return t === 'Demand' || t === 2
  })
  if (demand) return pick(demand[0])
  const withUnit = outs.find(([name]) => commodities[name]?.unitR)
  if (withUnit) return pick(withUnit[0])
  return {}
}

export function siteDemandPowerUnit(
  commodities: Record<string, CommodityLike>,
  preferred?: 'elec' | 'heat',
): string | undefined {
  const names = Object.entries(commodities)
  const isDemand = (com: CommodityLike) =>
    com.Type === 'Demand' || com.type === 'Demand' || com.type === 2
  const matchCarrier = (name: string) => {
    const n = name.toUpperCase()
    if (preferred === 'heat') {
      return (
        n.includes('HEAT') ||
        n.includes('THERMAL') ||
        n.includes('MJ') ||
        n.includes('GJ') ||
        n.includes('KWH_TH')
      )
    }
    return n.includes('ELEC')
  }
  if (preferred) {
    const hit = names.find(([name, com]) => isDemand(com) && matchCarrier(name))
    if (hit?.[1]?.unitR) return hit[1].unitR
  }
  const elec = names.find(
    ([name, com]) => isDemand(com) && name.toUpperCase().includes('ELEC'),
  )
  if (elec?.[1]?.unitR) return elec[1].unitR
  const any = names.find(([, com]) => isDemand(com) && com.unitR)
  return any?.[1]?.unitR
}

export function findCarrierUnits(
  config:
    | {
        site?: Record<
          string,
          { commodity?: Record<string, CommodityLike> }
        >
      }
    | undefined,
  carrier: 'elec' | 'heat' | 'co2',
): { unitR?: string; unitC?: string } {
  if (!config?.site) return {}
  const match = (name: string) => {
    const n = name.toUpperCase()
    if (carrier === 'elec') return n.includes('ELEC')
    if (carrier === 'co2') return n.includes('CO2')
    return (
      n.includes('HEAT') ||
      n.includes('THERMAL') ||
      n.includes('MJ') ||
      n.includes('GJ') ||
      n.includes('KWH_TH')
    )
  }
  for (const site of Object.values(config.site)) {
    for (const [name, com] of Object.entries(site.commodity || {})) {
      if (match(name)) return { unitR: com.unitR, unitC: com.unitC }
    }
  }
  return {}
}

export function inferDisplayScale(
  config: Parameters<typeof findCarrierUnits>[0],
): DisplayScale {
  const unitR = findCarrierUnits(config, 'elec').unitR
  return powerPrefix(unitR) === 'k' ? 'kW' : 'MW'
}

export function processOutputsCarrier(
  procConf:
    | { commodity?: Record<string, { Direction?: string }> }
    | undefined,
  carrier?: string,
): boolean {
  if (!carrier || !procConf?.commodity) return true
  const linked = Object.entries(procConf.commodity)
  if (!linked.length) return false
  return linked.some(([name]) => {
    const n = name.toUpperCase()
    if (carrier === 'heat') {
      return (
        n.includes('HEAT') ||
        n.includes('THERMAL') ||
        n.includes('MJ') ||
        n.includes('GJ') ||
        n.includes('KWH_TH')
      )
    }
    if (carrier === 'elec') return n.includes('ELEC')
    return true
  })
}
