export function dmsToDecimal(dms: string) {
  const regex = /([NSEW])(\d+)°(\d+)'([\d.]+)''/
  const matches = dms.match(regex)
  if (!matches) {
    throw new Error('Invalid DMS format')
  }
  const [, direction, degrees, minutes, seconds] = matches
  let decimal =
    parseInt(degrees) + parseInt(minutes) / 60 + parseFloat(seconds) / 3600
  if (direction === 'W' || direction === 'S') {
    decimal = -decimal
  }
  return decimal
}

export function decimalToDms(decimal: number, lon: boolean) {
  const direction = decimal < 0 ? (lon ? 'W' : 'S') : lon ? 'E' : 'N'
  decimal = Math.abs(decimal)
  const degrees = Math.floor(decimal)
  const minutesDecimal = (decimal - degrees) * 60
  const minutes = Math.floor(minutesDecimal)
  const seconds = (minutesDecimal - minutes) * 60
  return `${direction}${degrees.toString().padStart(lon ? 3 : 2, '0')}°${minutes.toString().padStart(2, '0')}'${seconds < 10 ? '0' : ''}${seconds.toFixed(3)}''`
}
