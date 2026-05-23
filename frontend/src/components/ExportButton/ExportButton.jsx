import { useState } from 'react'

export function ExportButton({ whatsappText }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(whatsappText)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      setCopied(false)
    }
  }

  return (
    <div style={{
      background: '#fff',
      border: '0.5px solid #E5E5E3',
      borderRadius: '12px',
      padding: '14px 20px',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
    }}>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: '11px', color: '#999', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          WhatsApp / SMS
        </div>
        <div style={{
          fontSize: '12px',
          color: '#555',
          fontFamily: 'monospace',
          lineHeight: '1.5',
        }}>
          {whatsappText || '—'}
        </div>
      </div>
      <button
        onClick={handleCopy}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '7px 14px',
          border: '0.5px solid #E5E5E3',
          borderRadius: '7px',
          fontSize: '12px',
          fontWeight: '500',
          color: copied ? '#1D9E75' : '#555',
          background: copied ? '#F0FDF4' : 'none',
          cursor: 'pointer',
          whiteSpace: 'nowrap',
          transition: 'all 0.15s',
        }}
      >
        {copied ? '✓ Copied!' : '⎘ Copy'}
      </button>
    </div>
  )
}