/**
 * ErrorFallback component - User-friendly error UI.
 * 
 * Displayed when ErrorBoundary catches an error.
 * Provides clear messaging and recovery options.
 */
function ErrorFallback({ error, errorInfo, resetError }) {
  const isDevelopment = import.meta.env.DEV

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50 p-4">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-xl p-8">
        {/* Error Icon */}
        <div className="flex items-center justify-center w-16 h-16 mx-auto mb-6 bg-red-100 rounded-full">
          <svg
            className="w-8 h-8 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>

        {/* Error Title */}
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-4">
          Something went wrong
        </h1>

        {/* Error Message */}
        <p className="text-center text-gray-600 mb-6">
          We're sorry, but something unexpected happened. This error has been logged
          and we'll look into it. Please try again or refresh the page.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
          <button
            onClick={resetError}
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Try Again
          </button>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          >
            Refresh Page
          </button>
        </div>

        {/* Error Details (Development Only) */}
        {isDevelopment && error && (
          <details className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <summary className="cursor-pointer font-semibold text-gray-700 hover:text-gray-900">
              Error Details (Development Only)
            </summary>
            <div className="mt-4 space-y-4">
              {/* Error Message */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Error Message:</h3>
                <pre className="text-sm text-red-600 bg-red-50 p-3 rounded overflow-auto">
                  {error.toString()}
                </pre>
              </div>

              {/* Error Stack */}
              {error.stack && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Stack Trace:</h3>
                  <pre className="text-xs text-gray-600 bg-gray-100 p-3 rounded overflow-auto max-h-64">
                    {error.stack}
                  </pre>
                </div>
              )}

              {/* Component Stack */}
              {errorInfo?.componentStack && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Component Stack:</h3>
                  <pre className="text-xs text-gray-600 bg-gray-100 p-3 rounded overflow-auto max-h-64">
                    {errorInfo.componentStack}
                  </pre>
                </div>
              )}
            </div>
          </details>
        )}

        {/* Help Text */}
        <div className="mt-6 pt-6 border-t border-gray-200 text-center text-sm text-gray-500">
          <p>
            If this problem persists, please contact support or{' '}
            <a
              href="https://github.com/hopessugar/mifos-loan-summarizer/issues"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-700 underline"
            >
              report an issue
            </a>
            .
          </p>
        </div>
      </div>
    </div>
  )
}

export default ErrorFallback
