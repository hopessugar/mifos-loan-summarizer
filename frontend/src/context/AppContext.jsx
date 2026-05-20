import { createContext, useContext, useState } from 'react'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [language, setLanguage] = useState('en')
  const [activeProvider, setActiveProvider] = useState('hf_inference')
  const [fineractStatus, setFineractStatus] = useState('unknown')

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
