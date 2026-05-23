export function Header({ language, setLanguage, result }) {
  return (
    <header style={{
      background: '#fff',
      borderBottom: '0.5px solid #E5E5E3',
      padding: '0 24px',
      height: '52px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: '26px', height: '26px',
          background: '#111',
          borderRadius: '7px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M2 3h10M2 7h7M2 11h5" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </div>
        <span style={{ fontSize: '14px', fontWeight: '600', color: '#111', letterSpacing: '-0.01em' }}>
           Smart Contract & Loan Agreement Analyzer
        </span>
        <span style={{
          fontSize: '10px', padding: '2px 7px',
          background: '#F3F2EE', border: '0.5px solid #E5E5E3',
          borderRadius: '4px', color: '#888', fontWeight: '500',
        }}>
          THE MIFOS INITATIVE
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {result && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '5px',
            fontSize: '12px', color: '#888',
            padding: '4px 10px',
            border: '0.5px solid #E5E5E3',
            borderRadius: '6px',
          }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#1D9E75' }}></div>
            {result.provider_used}
          </div>
        )}
        <div style={{
          display: 'flex',
          border: '0.5px solid #E5E5E3',
          borderRadius: '7px',
          overflow: 'hidden',
        }}>
          {['en', 'hi'].map(lang => (
            <button
              key={lang}
              onClick={() => setLanguage(lang)}
              style={{
                padding: '5px 12px',
                fontSize: '12px',
                fontWeight: '500',
                background: language === lang ? '#111' : 'transparent',
                color: language === lang ? '#fff' : '#888',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.15s',
              }}
            >
              {lang.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
    </header>
  )
}