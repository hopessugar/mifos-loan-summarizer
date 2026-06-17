export function RiskBadge({ risk }) {
  if (!risk) return null
  const bps = risk.bps_score || 100.0
  const color = bps < 50 ? '#DC2626' : bps < 80 ? '#D97706' : '#1D9E75'
  const bg = bps < 50 ? '#FEF2F2' : bps < 80 ? '#FFFBEB' : '#F0FDF4'
  const label = bps < 50 ? 'Low Protection' : bps < 80 ? 'Moderate Protection' : 'High Protection'
  const barWidth = `${Math.round(bps)}%`

  return (
    <div style={{
      background: '#fff',
      border: '0.5px solid #E5E5E3',
      borderRadius: '12px',
      padding: '16px 20px',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div>
          <div style={{ fontSize: '11px', color: '#999', marginBottom: '2px', textTransform: 'uppercase' }}>Borrower Protection Score</div>
          <div style={{ fontSize: '28px', fontWeight: '600', color, letterSpacing: '-0.03em', lineHeight: '1' }}>
            {Math.round(bps)}<span style={{ fontSize: '14px', color: '#CCC', fontWeight: '400' }}>/100</span>
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
              Primary issue: {risk.factors[0]}
            </div>
          )}
        </div>
      </div>
      
      {risk.negotiation_tips && risk.negotiation_tips.length > 0 && (
        <div style={{ marginTop: '8px', paddingTop: '12px', borderTop: '1px solid #F0F0EE' }}>
          <div style={{ fontSize: '12px', fontWeight: '600', color: '#333', marginBottom: '8px' }}>Negotiation Tips:</div>
          <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '12px', color: '#666' }}>
            {risk.negotiation_tips.map((tip, idx) => (
              <li key={idx} style={{ marginBottom: '4px' }}>{tip.replace('Negotiation Tip: ', '')}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}