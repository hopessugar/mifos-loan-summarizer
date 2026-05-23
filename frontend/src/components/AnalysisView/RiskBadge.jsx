export function RiskBadge({ risk }) {
  if (!risk) return null
  const score = risk.score || 0
  const color = score >= 7 ? '#DC2626' : score >= 4 ? '#D97706' : '#1D9E75'
  const bg = score >= 7 ? '#FEF2F2' : score >= 4 ? '#FFFBEB' : '#F0FDF4'
  const label = score >= 7 ? 'High risk' : score >= 4 ? 'Moderate risk' : 'Low risk'
  const barWidth = `${Math.round((score / 10) * 100)}%`

  return (
    <div style={{
      background: '#fff',
      border: '0.5px solid #E5E5E3',
      borderRadius: '12px',
      padding: '16px 20px',
      display: 'flex',
      alignItems: 'center',
      gap: '20px',
    }}>
      <div>
        <div style={{ fontSize: '11px', color: '#999', marginBottom: '2px' }}>Risk score</div>
        <div style={{ fontSize: '28px', fontWeight: '600', color, letterSpacing: '-0.03em', lineHeight: '1' }}>
          {score}<span style={{ fontSize: '14px', color: '#CCC', fontWeight: '400' }}>/10</span>
        </div>
      </div>

      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{
            fontSize: '12px', fontWeight: '500',
            padding: '2px 8px',
            background: bg,
            color,
            borderRadius: '4px',
          }}>{label}</span>
        </div>
        <div style={{ height: '4px', background: '#F0F0EE', borderRadius: '2px' }}>
          <div style={{ height: '4px', width: barWidth, background: color, borderRadius: '2px', transition: 'width 0.5s ease' }} />
        </div>
        {risk.factors?.[0] && (
          <div style={{ fontSize: '12px', color: '#888', marginTop: '6px' }}>
            {risk.factors[0]}
          </div>
        )}
      </div>
    </div>
  )
}