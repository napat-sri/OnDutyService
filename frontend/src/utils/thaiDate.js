const DATE_ONLY_OPTIONS = {
  day: '2-digit',
  month: 'long',
  year: 'numeric',
}

const DATE_SHORT_OPTIONS = {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
}

function toDate(dateValue) {
  if (!dateValue) return null
  if (dateValue instanceof Date) return dateValue
  if (typeof dateValue === 'string') {
    const normalized = dateValue.includes('T') ? dateValue : `${dateValue}T00:00:00`
    const parsed = new Date(normalized)
    if (Number.isNaN(parsed.getTime())) return null
    return parsed
  }
  const parsed = new Date(dateValue)
  if (Number.isNaN(parsed.getTime())) return null
  return parsed
}

export function formatThaiDate(dateValue, options = DATE_ONLY_OPTIONS) {
  const parsed = toDate(dateValue)
  if (!parsed) return '-'
  return parsed.toLocaleDateString('th-TH-u-ca-buddhist', options)
}

export function formatThaiDateShort(dateValue) {
  return formatThaiDate(dateValue, DATE_SHORT_OPTIONS)
}

export function formatThaiYear(gregorianYear) {
  if (!Number.isInteger(gregorianYear)) return '-'
  return gregorianYear + 543
}

export function toIsoDateString(dateValue = new Date()) {
  const parsed = toDate(dateValue)
  if (!parsed) return ''
  const year = parsed.getFullYear()
  const month = String(parsed.getMonth() + 1).padStart(2, '0')
  const day = String(parsed.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}