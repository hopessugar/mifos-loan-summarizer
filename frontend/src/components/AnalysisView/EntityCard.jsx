import { useState } from 'react'

export function EntityCard({ fieldName, entity }) {
  const [expanded, setExpanded] = useState(false)

  const label = fieldName
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase())

  const conf = entity.confidence || 0
  const confColor = conf >= 0.7 ? '#1D9E75' : conf >= 0.5 ? '#D97706' : '#DC2626'
  const confWidth = `${Math.round(conf * 100)}%`

  return (
    <div style={{
      background: '#fff',
      border: entity.flag ? '0.5px solid #FDE68A' : '0.5px solid #E5E5E3',
      borderRadius: '10px',
      padding: '14px 16px',
      background: entity.flag ? '#FFFDF0' : '#fff',
    }}>
      <div style={{ fontSize: '11px', color: '#999', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        {label}
      </div>
      <div style={{ fontSize: '16px', fontWeight: '500', color: '#111', marginBottom: '8px', letterSpacing: '-0.01em' }}>
        {entity.value !== null && entity.value !== undefined ? String(entity.value) : '—'}
      </div>

      <div style={{ height: '2px', background: '#F0F0EE', borderRadius: '1px', marginBottom: '6px' }}>
        <div style={{ height: '2px', width: confWidth, background: confColor, borderRadius: '1px', transition: 'width 0.3s' }} />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '11px', color: confColor }}>
          {Math.round(conf * 100)}% confidence
        </span>
        {entity.source_clause && (
          <button
            onClick={() => setExpanded(!expanded)}
            style={{
              fontSize: '11px', color: '#999',
              background: 'none', border: 'none',
              cursor: 'pointer', padding: '0',
            }}
          >
            {expanded ? 'Hide source ↑' : 'Source ↓'}
          </button>
        )}
      </div>

      {expanded && entity.source_clause && (
        <div style={{
          marginTop: '8px',
          padding: '8px 10px',
          background: '#F7F6F2',
          borderRadius: '6px',
          fontSize: '12px',
          color: '#666',
          lineHeight: '1.5',
          fontStyle: 'italic',
        }}>
          "{entity.source_clause}"
        </div>
      )}

      {entity.flag && (
        <div style={{ marginTop: '6px', fontSize: '11px', color: '#D97706' }}>
          ⚠ {entity.flag}
        </div>
      )}
    </div>
  )
}