import { useCallback } from 'react'
import { useAppContext } from '../context/AppContext'
import translations from '../i18n/translations'

/**
 * Hook that provides translation helpers for the current language.
 *
 * Usage:
 *   const { t, language, setLanguage } = useTranslation()
 *   <span>{t('header.title')}</span>
 *
 * Supports simple interpolation:
 *   t('stat.months', { n: 12 })      →  "12 months"
 *   t('pdf.tooLarge', { size: '15 MB' })
 */
export function useTranslation() {
  const { language, setLanguage } = useAppContext()

  const t = useCallback(
    (key, params) => {
      // Look up the key in the current language, fall back to English
      let str =
        translations[language]?.[key] ??
        translations['en']?.[key] ??
        key // ultimate fallback: show the key itself

      // Simple interpolation: replace {name} tokens with params
      if (params) {
        Object.entries(params).forEach(([k, v]) => {
          str = str.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v))
        })
      }
      return str
    },
    [language],
  )

  return { t, language, setLanguage }
}
