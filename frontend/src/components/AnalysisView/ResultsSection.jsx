export function ResultsSection({ result }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="text-base font-semibold text-gray-900 mb-4">
        Analysis Results
      </h2>

      {/* Summary */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Summary</h3>
        <p className="text-sm text-gray-600 leading-relaxed">
          {result.summary || 'No summary generated yet.'}
        </p>
      </div>

      {/* Provider + timing meta */}
      <div className="flex gap-4 text-xs text-gray-400 border-t border-gray-100 pt-4">
        <span>Provider: {result.provider_used || 'stub'}</span>
        <span>Segments: {result.segment_count}</span>
        <span>Time: {result.processing_time_ms}ms</span>
      </div>
    </div>
  )
}
