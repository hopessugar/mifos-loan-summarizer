import { useState } from 'react'

export function ContractInput({ onSubmit, loading, onReset, hasResult }) {
  const [text, setText] = useState('')
  const charCount = text.length
  const isValid = charCount >= 50 && charCount <= 50000

  function getCountColor() {
    if (charCount === 0) return '#CCC'
    if (charCount < 50 || charCount > 50000) return '#DC2626'
    return '#999'
  }

  return (
    <div style={{
      background: '#fff',
      border: '0.5px solid #E5E5E3',
      borderRadius: '12px',
      overflow: 'hidden',
      marginBottom: '12px',
    }}>
      <div style={{
        padding: '16px 20px 0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <span style={{ fontSize: '13px', fontWeight: '500', color: '#111' }}>
          Paste loan agreement
        </span>
        <span style={{ fontSize: '12px', color: '#BBB' }}>
          50 – 50,000 characters
        </span>
      </div>

      <div style={{ padding: '12px 20px 0' }}>
        <textarea
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Paste the full text of a loan agreement here..."
          rows={8}
          style={{
            width: '100%',
            background: 'none',
            border: 'none',
            outline: 'none',
            fontSize: '13px',
            color: '#333',
            resize: 'none',
            lineHeight: '1.7',
            fontFamily: 'inherit',
          }}
        />
      </div>

      <div style={{
        padding: '12px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderTop: '0.5px solid #F0F0EE',
        marginTop: '8px',
      }}>
        <span style={{ fontSize: '12px', color: getCountColor(), fontVariantNumeric: 'tabular-nums' }}>
          {charCount.toLocaleString()} / 50,000
          {charCount > 0 && charCount < 50 ? ' — need at least 50' : ''}
        </span>

        <div style={{ display: 'flex', gap: '8px' }}>
          {hasResult && (
            <button
              onClick={onReset}
              style={{
                padding: '7px 14px',
                border: '0.5px solid #E5E5E3',
                borderRadius: '7px',
                fontSize: '13px',
                color: '#666',
                background: 'none',
                cursor: 'pointer',
              }}
            >
              Reset
            </button>
          )}
          <button
            onClick={() => isValid && onSubmit(text)}
            disabled={!isValid || loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '7px 16px',
              background: isValid && !loading ? '#111' : '#E5E5E3',
              color: isValid && !loading ? '#fff' : '#AAA',
              border: 'none',
              borderRadius: '7px',
              fontSize: '13px',
              fontWeight: '500',
              cursor: isValid && !loading ? 'pointer' : 'not-allowed',
              transition: 'all 0.15s',
            }}
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 1L13 7L7 13M1 7h12" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {loading ? 'Analysing...' : 'Analyse contract'}
          </button>
        </div>
      </div>
    </div>
  )
}