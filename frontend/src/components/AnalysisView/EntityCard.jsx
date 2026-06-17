import { useState } from 'react'

export function EntityCard({ fieldName, entity }) {
  const [expanded, setExpanded] = useState(false)

  const label = fieldName
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase())

  const conf = entity.confidence || 0
  let trafficLight = '🔴 Uncertain'
  let confColor = '#DC2626'
  
  if (entity.is_verified || conf >= 0.90) {
    trafficLight = '🟢 Verified'
    confColor = '#1D9E75'
  } else if (conf >= 0.50) {
    trafficLight = '🟡 Needs Review'
    confColor = '#D97706'
  }

  const renderSourceClause = () => {
    if (!entity.source_clause) return null;
    if (entity.value === null || entity.value === undefined) return `"${entity.source_clause}"`;
    
    const valStr = String(entity.value);
    const parts = entity.source_clause.split(new RegExp(`(${valStr})`, 'gi'));
    return (
      <>
        "{parts.map((part, i) => 
          part.toLowerCase() === valStr.toLowerCase() 
            ? <span key={i} style={{backgroundColor: '#FEF08A', fontWeight: 'bold', color: '#000'}}>{part}</span> 
            : part
        )}"
      </>
    );
  }

  return (
    <div style={{
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

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '8px' }}>
        <span style={{ fontSize: '12px', fontWeight: '500', color: confColor }}>
          {trafficLight}
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
          {renderSourceClause()}
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