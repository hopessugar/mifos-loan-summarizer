import { AppProvider } from './context/AppContext'
import { useAnalysis } from './hooks/useAnalysis'
import { useLanguage } from './hooks/useLanguage'
import { ContractInput } from './components/ContractInput/ContractInput'
import { ResultsSection } from './components/AnalysisView/ResultsSection'
import { Spinner } from './components/shared/Spinner'
import { ErrorBanner } from './components/shared/ErrorBanner'

function Main() {
  const { status, result, error, submit, reset } = useAnalysis()
  const { language, setLanguage } = useLanguage()

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">
              Mifos Loan Summarizer
            </h1>
            <p className="text-sm text-gray-500">
              LLM-powered loan agreement analysis
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex rounded-lg border border-gray-200 overflow-hidden">
              <button
                onClick={() => setLanguage('en')}
                className={language === 'en'
                  ? 'px-3 py-1.5 text-sm font-medium bg-blue-600 text-white'
                  : 'px-3 py-1.5 text-sm font-medium bg-white text-gray-600 hover:bg-gray-50'}
              >
                EN
              </button>
              <button
                onClick={() => setLanguage('hi')}
                className={language === 'hi'
                  ? 'px-3 py-1.5 text-sm font-medium bg-blue-600 text-white'
                  : 'px-3 py-1.5 text-sm font-medium bg-white text-gray-600 hover:bg-gray-50'}
              >
                HI
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <ContractInput
          onSubmit={(text) => submit({ text, language })}
          loading={status === 'loading'}
          onReset={reset}
          hasResult={!!result}
        />

        {status === 'loading' && (
          <div className="mt-8">
            <Spinner />
            <p className="text-center text-sm text-gray-500 mt-2">
              Analysing contract...
            </p>
          </div>
        )}

        {status === 'error' && (
          <div className="mt-6">
            <ErrorBanner message={error} />
          </div>
        )}

        {status === 'success' && result && (
          <div className="mt-8">
            <ResultsSection result={result} />
          </div>
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