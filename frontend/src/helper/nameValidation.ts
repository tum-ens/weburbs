export const FORBIDDEN_NAME_CHARS_LABEL = '/ \\ ? # %'

const FORBIDDEN_NAME_CHARS_PATTERN = /[/\\?#%]/

export function getNameValidationError(
  name: string | null | undefined,
): string | null {
  if (!name || name.trim() === '') {
    return null
  }
  if (FORBIDDEN_NAME_CHARS_PATTERN.test(name)) {
    return `These characters are not allowed: ${FORBIDDEN_NAME_CHARS_LABEL}`
  }
  return null
}

export function isValidName(name: string | null | undefined): boolean {
  return getNameValidationError(name) === null
}
