/**
 * SectionErrorFallback - Smaller error UI for section-level errors.
 * 
 * Used when a specific section fails but the rest of the app should continue working.
 */
function SectionErrorFallback({ error, resetError }) {
  const isDevelopment = import.meta.env.DEV

  return (
    <div className="my-8 p-6 bg-red-50 border border-red-200 rounded-lg">
      <div className="flex items-start gap-4">
        {/* Error Icon */}
        <div className="flex-shrink-0">
          <svg
            className="w-6 h-6 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>

        {/* Error Content */}
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-red-900 mb-2">
            This section encountered an error
          </h3>
          <p className="text-sm text-red-700 mb-4">
            Something went wrong while loading this section. The rest of the app should
            still work normally.
          </p>

          {/* Action Button */}
          {resetError && (
            <button
              onClick={resetError}
              className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              Try Again
            </button>
          )}

          {/* Error Details (Development Only) */}
          {isDevelopment && error && (
            <details className="mt-4">
              <summary className="cursor-pointer text-sm font-medium text-red-800 hover:text-red-900">
                Error Details (Development Only)
              </summary>
              <pre className="mt-2 text-xs text-red-600 bg-white p-3 rounded border border-red-200 overflow-auto max-h-40">
                {error.toString()}
              </pre>
            </details>
          )}
        </div>
      </div>
    </div>
  )
}

export default SectionErrorFallback
