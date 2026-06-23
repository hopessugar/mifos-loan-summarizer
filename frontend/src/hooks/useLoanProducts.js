import { useState, useEffect, useCallback } from 'react'
import { getLoanProducts, refreshLoanProducts } from '../services/api'

export function useLoanProducts() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchProducts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getLoanProducts()
      setProducts(data)
    } catch (err) {
      setError(err.message || 'Could not load Mifos X loan products')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProducts()
  }, [fetchProducts])

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await refreshLoanProducts()
      setProducts(data.products || [])
    } catch (err) {
      setError(err.message || 'Could not refresh loan products')
    } finally {
      setLoading(false)
    }
  }, [])

  return { products, loading, error, refresh, retry: fetchProducts }
}
