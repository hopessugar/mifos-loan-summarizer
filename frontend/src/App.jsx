import { useState } from 'react'
import { AppProvider } from './context/AppContext'
import { ErrorBoundary, SectionErrorFallback } from './components/ErrorBoundary'
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
    <div className="min-h-screen bg-[#F7F6F2]">
      <Header language={language} setLanguage={setLanguage} result={result} />

      <main className="max-w-3xl mx-auto px-6 py-10">
        <div className="mb-8">
          <p className="text-[11px] font-medium text-[#888] uppercase tracking-[0.08em] mb-1.5">
            Loan analysis
          </p>
          <h1 className="text-2xl font-semibold text-[#111] mb-1.5 tracking-[-0.02em]">
            Understand your loan agreement
          </h1>
          <p className="text-sm text-[#666] leading-relaxed">
            Paste any loan contract or select a Mifos X product to get a plain-language summary, extracted terms, and risk analysis.
          </p>
        </div>

        <div 
          role="tablist"
          className="flex gap-0 border-b border-[#E5E5E3] mb-4"
        >
          {[
            { key: 'paste', label: 'Paste text' },
            { key: 'mifos', label: 'Mifos X product' },
          ].map(tab => (
            <button
              key={tab.key}
              role="tab"
              aria-selected={inputMode === tab.key}
              onClick={() => { setInputMode(tab.key); reset(); }}
              className={`px-4 py-2 text-[13px] bg-none border-none border-b-[1.5px] cursor-pointer -mb-[0.5px] transition-all duration-150 ${
                inputMode === tab.key ? 'text-[#111] border-[#111] font-medium' : 'text-[#999] border-transparent font-normal'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {inputMode === 'paste' ? (
          <ErrorBoundary fallback={<SectionErrorFallback />}>
            <ContractInput
              onSubmit={(text) => submit({ text, language })}
              loading={status === 'loading'}
              onReset={reset}
              hasResult={!!result}
            />
          </ErrorBoundary>
        ) : (
          <ErrorBoundary fallback={<SectionErrorFallback />}>
            <MifosProductPicker
              onSubmit={(id) => submit({ loan_product_id: id, language })}
              loading={status === 'loading'}
            />
          </ErrorBoundary>
        )}

        {status === 'loading' && (
          <div className="mt-12 text-center">
            <Spinner />
            <p className="mt-3 text-[13px] text-[#888]">
              Analysing contract...
            </p>
          </div>
        )}

        {status === 'error' && (
          <div className="mt-4 px-4 py-3 bg-[#FEF2F2] border border-[#FECACA] rounded-xl text-[13px] text-[#DC2626]">
            {error}
          </div>
        )}

        {status === 'success' && result && (
          <ErrorBoundary fallback={<SectionErrorFallback />}>
            <ResultsSection result={result} />
          </ErrorBoundary>
        )}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <AppProvider>
        <Main />
      </AppProvider>
    </ErrorBoundary>
  )
}