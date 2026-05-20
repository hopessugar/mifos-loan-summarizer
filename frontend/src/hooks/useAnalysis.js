import { useState } from 'react'
import { analyseContract } from '../services/api'

export function useAnalysis() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function submit(payload) {
    setStatus('loading')
    setError(null)
    setResult(null)
    try {
      const data = await analyseContract(payload)
      setResult(data)
      setStatus('success')
    } catch (err) {
      setError(err.message || 'Something went wrong')
      setStatus('error')
    }
  }

  function reset() {
    setStatus('idle')
    setResult(null)
    setError(null)
  }

  return { status, result, error, submit, reset }
}
