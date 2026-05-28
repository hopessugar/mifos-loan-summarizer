import { useLoanProducts } from '../../hooks/useLoanProducts'

export function MifosProductPicker({ onSubmit, loading }) {
  const { products, loading: productsLoading, error } = useLoanProducts()

  function handleChange(e) {
    const id = parseInt(e.target.value)
    if (id) onSubmit(id)
  }

  if (error) {
    return (
      <div style={{
        padding: '12px 16px',
        background: '#FEF9EE',
        border: '0.5px solid #FDE68A',
        borderRadius: '10px',
        fontSize: '13px',
        color: '#92400E',
      }}>
        ⚠ Cannot connect to Mifos X — use manual paste instead.
      </div>
    )
  }

  return (
    <div style={{
      background: '#fff',
      border: '0.5px solid #E5E5E3',
      borderRadius: '12px',
      padding: '16px 20px',
    }}>
      <div style={{
        fontSize: '13px',
        fontWeight: '500',
        color: '#111',
        marginBottom: '8px',
      }}>
        Select Mifos X loan product
      </div>
      <div style={{
        fontSize: '12px',
        color: '#999',
        marginBottom: '12px',
      }}>
        Pulls loan product data directly from Fineract API
      </div>

      {productsLoading ? (
        <div style={{ fontSize: '13px', color: '#999' }}>
          Loading loan products...
        </div>
      ) : (
        <select
          onChange={handleChange}
          disabled={loading}
          style={{
            width: '100%',
            padding: '8px 12px',
            border: '0.5px solid #E5E5E3',
            borderRadius: '8px',
            fontSize: '13px',
            color: '#333',
            background: '#fff',
            cursor: 'pointer',
          }}
        >
          <option value="">— Select a loan product —</option>
          {products.map(p => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      )}

      {products.length === 0 && !productsLoading && (
        <div style={{
          marginTop: '8px',
          fontSize: '12px',
          color: '#BBB',
        }}>
          No products found — check Fineract connection in config.yaml
        </div>
      )}
    </div>
  )
}