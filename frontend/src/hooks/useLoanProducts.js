import { useState, useEffect } from 'react'
import { getLoanProducts } from '../services/api'

export function useLoanProducts() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetch() {
      setLoading(true)
      try {
        const data = await getLoanProducts()
        setProducts(data)
      } catch (err) {
        setError('Could not load Mifos X loan products')
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  return { products, loading, error }
}
