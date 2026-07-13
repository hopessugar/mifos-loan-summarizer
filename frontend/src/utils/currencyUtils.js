/**
 * Currency utilities for international loan contract analysis.
 * Mirrors the backend's pipeline/currency.py for consistent formatting.
 */

// ISO 4217 currency code → display symbol
const CURRENCY_SYMBOLS = {
  INR: '₹', USD: '$', EUR: '€', GBP: '£', JPY: '¥', CNY: '¥',
  KES: 'KSh', UGX: 'USh', TZS: 'TSh', NGN: '₦', GHS: 'GH₵',
  ZAR: 'R', BRL: 'R$', MXN: 'MX$', AUD: 'A$', CAD: 'C$',
  CHF: 'CHF', SEK: 'kr', NOK: 'kr', DKK: 'kr', PLN: 'zł',
  CZK: 'Kč', HUF: 'Ft', RUB: '₽', TRY: '₺', KRW: '₩',
  THB: '฿', IDR: 'Rp', MYR: 'RM', PHP: '₱', VND: '₫',
  PKR: 'Rs', BDT: '৳', LKR: 'Rs', NPR: 'Rs', MMK: 'K',
  AED: 'د.إ', SAR: '﷼', EGP: 'E£', XOF: 'CFA', XAF: 'FCFA',
  RWF: 'RF', MWK: 'MK', ZMW: 'ZK', ETB: 'Br',
  COP: 'COL$', PEN: 'S/', ARS: 'AR$', CLP: 'CL$',
}

// Currency code → locale for correct number grouping
// e.g. USD uses "en-US" (100,000) not "en-IN" (1,00,000)
const CURRENCY_LOCALES = {
  USD: 'en-US', EUR: 'de-DE', GBP: 'en-GB', JPY: 'ja-JP', CNY: 'zh-CN',
  INR: 'en-IN', KES: 'en-KE', UGX: 'en-UG', TZS: 'sw-TZ', NGN: 'en-NG',
  GHS: 'en-GH', ZAR: 'en-ZA', BRL: 'pt-BR', MXN: 'es-MX', AUD: 'en-AU',
  CAD: 'en-CA', CHF: 'de-CH', SEK: 'sv-SE', NOK: 'nb-NO', DKK: 'da-DK',
  PLN: 'pl-PL', CZK: 'cs-CZ', HUF: 'hu-HU', RUB: 'ru-RU', TRY: 'tr-TR',
  KRW: 'ko-KR', THB: 'th-TH', IDR: 'id-ID', MYR: 'ms-MY', PHP: 'en-PH',
  VND: 'vi-VN', PKR: 'en-PK', BDT: 'bn-BD', LKR: 'si-LK', NPR: 'ne-NP',
  AED: 'ar-AE', SAR: 'ar-SA', EGP: 'ar-EG', RWF: 'rw-RW', ETB: 'am-ET',
  COP: 'es-CO', PEN: 'es-PE', ARS: 'es-AR', CLP: 'es-CL',
}

/**
 * Get the display symbol for a currency code.
 * Falls back to the code itself for unknown currencies.
 */
export function getCurrencySymbol(currencyCode) {
  if (!currencyCode) return '$'
  return CURRENCY_SYMBOLS[currencyCode.toUpperCase()] || currencyCode.toUpperCase()
}

/**
 * Get the appropriate locale for a currency code.
 * Uses the currency's home locale for correct number grouping.
 * Falls back to 'en-US' (standard Western grouping) for unknown currencies.
 */
function getLocaleForCurrency(currencyCode) {
  if (!currencyCode) return 'en-US'
  return CURRENCY_LOCALES[currencyCode.toUpperCase()] || 'en-US'
}

/**
 * Format a monetary value with the correct currency symbol and number grouping.
 *
 * Uses Intl.NumberFormat with a locale matched to the currency so that
 * number grouping follows the currency's convention:
 *   - USD → "en-US" → $100,000  (not $1,00,000)
 *   - INR → "en-IN" → ₹1,00,000
 *   - EUR → "de-DE" → 100.000 €
 *
 * @param {number|string|null} value - The monetary value
 * @param {string|null} currencyCode - ISO 4217 currency code (e.g. 'USD', 'INR')
 * @returns {string} Formatted string like "$100,000" or "₹1,00,000"
 */
export function formatCurrency(value, currencyCode) {
  if (value === null || value === undefined) return '—'

  const num = Number(value)
  if (isNaN(num)) return String(value)

  const code = (currencyCode || 'USD').toUpperCase()
  const locale = getLocaleForCurrency(code)

  // Try Intl.NumberFormat with the currency's native locale
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: code,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num)
  } catch {
    // Intl doesn't recognize this currency code — fall back to symbol + commas
    const symbol = getCurrencySymbol(code)
    const formatted = num.toLocaleString(locale, {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })
    return `${symbol}${formatted}`
  }
}
