import { createContext, useContext, useState, useEffect } from 'react'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [language, setLanguageState] = useState(
    () => localStorage.getItem('language') || 'en'
  )
  const [activeProvider, setActiveProvider] = useState('hf_inference')
  const [fineractStatus, setFineractStatus] = useState('unknown')

  // Persist language choice & update <html lang>
  const setLanguage = (lang) => {
    setLanguageState(lang)
    localStorage.setItem('language', lang)
    document.documentElement.lang = lang
  }

  // Set <html lang> on mount
  useEffect(() => {
    document.documentElement.lang = language
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <AppContext.Provider value={{
      language, setLanguage,
      activeProvider, setActiveProvider,
      fineractStatus, setFineractStatus,
    }}>
      {children}
    </AppContext.Provider>
  )
}

export function useAppContext() {
  return useContext(AppContext)
}
