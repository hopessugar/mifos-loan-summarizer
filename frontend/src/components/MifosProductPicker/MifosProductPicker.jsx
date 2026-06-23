import { useLoanProducts } from '../../hooks/useLoanProducts'

export function MifosProductPicker({ onSubmit, loading }) {
  const { products, loading: productsLoading, error, refresh, retry } = useLoanProducts()

  function handleChange(e) {
    const id = parseInt(e.target.value)
    if (id) onSubmit(id)
  }

  if (error) {
    return (
      <div style={{
        padding: '16px 20px',
        background: '#FEF9EE',
        border: '0.5px solid #FDE68A',
        borderRadius: '10px',
        fontSize: '13px',
        color: '#92400E',
      }}>
        <div style={{ marginBottom: '8px', fontWeight: '500' }}>
          ⚠ Cannot connect to Mifos X
        </div>
        <div style={{ fontSize: '12px', color: '#A16207', marginBottom: '12px' }}>
          {error}
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={retry}
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              fontWeight: '500',
              background: '#fff',
              border: '1px solid #FDE68A',
              borderRadius: '6px',
              cursor: 'pointer',
              color: '#92400E',
            }}
          >
            ↻ Retry
          </button>
          <button
            onClick={refresh}
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              fontWeight: '500',
              background: '#fff',
              border: '1px solid #FDE68A',
              borderRadius: '6px',
              cursor: 'pointer',
              color: '#92400E',
            }}
          >
            🗑 Clear cache & retry
          </button>
        </div>
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
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px',
      }}>
        <div style={{
          fontSize: '13px',
          fontWeight: '500',
          color: '#111',
        }}>
          Select Mifos X loan product
        </div>
        <button
          onClick={refresh}
          disabled={productsLoading}
          title="Clear cache and refresh products from Fineract"
          style={{
            padding: '4px 10px',
            fontSize: '11px',
            fontWeight: '500',
            background: 'transparent',
            border: '1px solid #E5E5E3',
            borderRadius: '6px',
            cursor: productsLoading ? 'wait' : 'pointer',
            color: '#888',
            transition: 'all 0.15s ease',
          }}
          onMouseEnter={(e) => {
            e.target.style.borderColor = '#CCC'
            e.target.style.color = '#555'
          }}
          onMouseLeave={(e) => {
            e.target.style.borderColor = '#E5E5E3'
            e.target.style.color = '#888'
          }}
        >
          ↻ Refresh
        </button>
      </div>
      <div style={{
        fontSize: '12px',
        color: '#999',
        marginBottom: '12px',
      }}>
        Pulls loan product data directly from Fineract API
      </div>

      {productsLoading ? (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '13px',
          color: '#999',
          padding: '8px 0',
        }}>
          <span style={{
            display: 'inline-block',
            width: '14px',
            height: '14px',
            border: '2px solid #E5E5E3',
            borderTopColor: '#888',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
          }} />
          Loading loan products...
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
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

      {products.length > 0 && !productsLoading && (
        <div style={{
          marginTop: '8px',
          fontSize: '11px',
          color: '#BBB',
        }}>
          {products.length} product{products.length !== 1 ? 's' : ''} available
        </div>
      )}

      {products.length === 0 && !productsLoading && (
        <div style={{
          marginTop: '8px',
          fontSize: '12px',
          color: '#BBB',
        }}>
          No products found — try refreshing or check Fineract connection
        </div>
      )}
    </div>
  )
}