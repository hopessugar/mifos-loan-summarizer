import { useState } from 'react'
import { AppProvider } from './context/AppContext'
import { useAnalysis } from './hooks/useAnalysis'
import { useLanguage } from './hooks/useLanguage'
import { ContractInput } from './components/ContractInput/ContractInput'
import { MifosProductPicker } from './components/MifosProductPicker/MifosProductPicker'
import { ResultsSection } from './components/AnalysisView/ResultsSection'
import { Header } from './components/shared/Header'
import { Spinner } from './components/shared/Spinner'

function Main() {
  const { status, result, error, submit, reset } = useAnalysis()
  const { language, setLanguage } = useLanguage()
  const [inputMode, setInputMode] = useState('paste')

  return (
    <div style={{ minHeight: '100vh', background: '#F7F6F2' }}>
      <Header language={language} setLanguage={setLanguage} result={result} />

      <main style={{ maxWidth: '760px', margin: '0 auto', padding: '40px 24px' }}>
        <div style={{ marginBottom: '32px' }}>
          <p style={{ fontSize: '11px', fontWeight: '500', color: '#888', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '6px' }}>
            Loan analysis
          </p>
          <h1 style={{ fontSize: '24px', fontWeight: '600', color: '#111', marginBottom: '6px', letterSpacing: '-0.02em' }}>
            Understand your loan agreement
          </h1>
          <p style={{ fontSize: '14px', color: '#666', lineHeight: '1.6' }}>
            Paste any loan contract or select a Mifos X product to get a plain-language summary, extracted terms, and risk analysis.
          </p>
        </div>

        <div style={{
          display: 'flex',
          gap: '0',
          borderBottom: '0.5px solid #E5E5E3',
          marginBottom: '16px',
        }}>
          {[
            { key: 'paste', label: 'Paste text' },
            { key: 'mifos', label: 'Mifos X product' },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => { setInputMode(tab.key); reset(); }}
              style={{
                padding: '8px 16px',
                fontSize: '13px',
                color: inputMode === tab.key ? '#111' : '#999',
                background: 'none',
                border: 'none',
                borderBottom: inputMode === tab.key ? '1.5px solid #111' : '1.5px solid transparent',
                cursor: 'pointer',
                fontWeight: inputMode === tab.key ? '500' : '400',
                marginBottom: '-0.5px',
                transition: 'all 0.15s',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {inputMode === 'paste' ? (
          <ContractInput
            onSubmit={(text) => submit({ text, language })}
            loading={status === 'loading'}
            onReset={reset}
            hasResult={!!result}
          />
        ) : (
          <MifosProductPicker
            onSubmit={(id) => submit({ loan_product_id: id, language })}
            loading={status === 'loading'}
          />
        )}

        {status === 'loading' && (
          <div style={{ marginTop: '48px', textAlign: 'center' }}>
            <Spinner />
            <p style={{ marginTop: '12px', fontSize: '13px', color: '#888' }}>
              Analysing contract...
            </p>
          </div>
        )}

        {status === 'error' && (
          <div style={{
            marginTop: '16px',
            padding: '12px 16px',
            background: '#FEF2F2',
            border: '0.5px solid #FECACA',
            borderRadius: '10px',
            fontSize: '13px',
            color: '#DC2626',
          }}>
            {error}
          </div>
        )}

        {status === 'success' && result && (
          <ResultsSection result={result} />
        )}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AppProvider>
      <Main />
    </AppProvider>
  )
}