export const groupOptions = [
  {
    name: 'Monthly',
    groupSize: 730,
    groups: 12,
  },
  {
    name: 'Weekly',
    groupSize: 169,
    groups: 52,
  },
  {
    name: 'Daily',
    groupSize: 24,
    groups: 365,
  },
  {
    name: 'Hourly',
    groupSize: 1,
    groups: 8760,
  },
]

export function chunkAdd(data: number[], chunkSize: number) {
  const res = []
  let buffer = 0
  for (let i = 0; i < data.length; i++) {
    buffer += data[i]
    if ((i + 1) % chunkSize === 0) {
      res.push(buffer)
      buffer = 0
    }
  }
  if (buffer > 0) res.push(buffer)
  return res
}

export function chunkAvg(data: number[], chunkSize: number) {
  const res = []
  let buffer = 0
  let ctr = 0
  for (let i = 0; i < data.length; i++) {
    buffer += data[i]
    ctr++
    if ((i + 1) % chunkSize === 0) {
      res.push(buffer / ctr)
      buffer = 0
      ctr = 0
    }
  }
  if (buffer > 0) res.push(buffer / ctr)
  return res
}
