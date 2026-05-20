import { useState } from 'react'
import { Button } from '../shared/Button'

export function ContractInput({ onSubmit, loading, onReset, hasResult }) {
  const [text, setText] = useState('')
  const charCount = text.length
  const isValid = charCount >= 50 && charCount <= 50000

  function handleSubmit() {
    if (isValid) onSubmit(text)
  }

  function getCharCountClass() {
    if (charCount < 50 || charCount > 50000) return 'text-red-500'
    return 'text-gray-400'
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="text-base font-semibold text-gray-900 mb-1">
        Paste Loan Agreement
      </h2>
      <p className="text-sm text-gray-500 mb-4">
        Paste the full text of a loan agreement (50 to 50,000 characters)
      </p>

      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="Paste loan agreement text here..."
        rows={10}
        className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
      />

      <div className="flex items-center justify-between mt-3">
        <span className={getCharCountClass() + ' text-xs'}>
          {charCount} / 50,000 characters
          {charCount < 50 && charCount > 0 ? ' (minimum 50)' : ''}
        </span>

        <div className="flex gap-2">
          {hasResult && (
            <Button variant="secondary" onClick={onReset}>
              Reset
            </Button>
          )}
          <Button onClick={handleSubmit} disabled={!isValid || loading}>
            {loading ? 'Analysing...' : 'Analyse'}
          </Button>
        </div>
      </div>
    </div>
  )
}