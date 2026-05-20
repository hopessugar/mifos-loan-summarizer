import { useState, useEffect } from 'react'

export function useLanguage() {
  const [language, setLanguage] = useState(
    () => localStorage.getItem('language') || 'en'
  )

  useEffect(() => {
    localStorage.setItem('language', language)
  }, [language])

  return { language, setLanguage }
}
