import { useState, useRef, useCallback } from 'react'

/* ---------- file type config ---------- */
const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg']
const ACCEPT_STRING = '.pdf,.docx,.doc,.txt,.png,.jpg,.jpeg,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword,text/plain,image/png,image/jpeg'

const FILE_TYPE_META = {
  '.pdf':  { label: 'PDF',  color: '#DC2626', bg: '#FEF2F2' },
  '.docx': { label: 'DOCX', color: '#2563EB', bg: '#EFF6FF' },
  '.doc':  { label: 'DOC',  color: '#2563EB', bg: '#EFF6FF' },
  '.txt':  { label: 'TXT',  color: '#059669', bg: '#ECFDF5' },
  '.png':  { label: 'PNG',  color: '#7C3AED', bg: '#F5F3FF' },
  '.jpg':  { label: 'JPG',  color: '#7C3AED', bg: '#F5F3FF' },
  '.jpeg': { label: 'JPG',  color: '#7C3AED', bg: '#F5F3FF' },
}

function getExtension(name) {
  if (!name) return ''
  const dot = name.lastIndexOf('.')
  return dot === -1 ? '' : name.slice(dot).toLowerCase()
}

/* ---------- component ---------- */
export function PdfUpload({ onSubmit, loading, onReset, hasResult }) {
  const [file, setFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  const MAX_SIZE = 10 * 1024 * 1024 // 10MB

  function formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  function validateFile(f) {
    if (!f) return 'No file selected.'
    const ext = getExtension(f.name)
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return `Unsupported file type "${ext || '(none)'}". Accepted: PDF, DOCX, TXT, PNG, JPG`
    }
    if (f.size === 0) return 'File is empty.'
    if (f.size > MAX_SIZE) return `File is too large (${formatSize(f.size)}). Maximum is 10 MB.`
    return ''
  }

  function handleFile(f) {
    const err = validateFile(f)
    if (err) {
      setError(err)
      setFile(null)
    } else {
      setError('')
      setFile(f)
    }
  }

  const onDragOver = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const onDragLeave = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    const dropped = e.dataTransfer.files?.[0]
    if (dropped) handleFile(dropped)
  }, [])

  const onInputChange = (e) => {
    const selected = e.target.files?.[0]
    if (selected) handleFile(selected)
  }

  const removeFile = () => {
    setFile(null)
    setError('')
    if (inputRef.current) inputRef.current.value = ''
  }

  /* derive badge style from file extension */
  const ext = file ? getExtension(file.name) : ''
  const meta = FILE_TYPE_META[ext] || FILE_TYPE_META['.txt']

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
          Upload document
        </span>
        <span style={{ fontSize: '12px', color: '#BBB' }}>
          Max 10 MB
        </span>
      </div>

      <div style={{ padding: '12px 20px 0' }}>
        {!file ? (
          /* Drop zone */
          <div
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            style={{
              border: `1.5px dashed ${isDragging ? '#111' : '#D5D5D3'}`,
              borderRadius: '10px',
              padding: '32px 20px',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              background: isDragging ? '#FAFAF8' : 'transparent',
            }}
          >
            {/* Document icon */}
            <div style={{
              width: '40px',
              height: '40px',
              margin: '0 auto 12px',
              background: '#F5F5F3',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#888" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
            </div>

            <p style={{ fontSize: '13px', color: '#666', margin: '0 0 4px' }}>
              {isDragging ? (
                <span style={{ color: '#111', fontWeight: '500' }}>Drop file here</span>
              ) : (
                <>
                  <span style={{ color: '#111', fontWeight: '500', textDecoration: 'underline', textUnderlineOffset: '2px' }}>
                    Click to browse
                  </span>
                  {' '}or drag and drop
                </>
              )}
            </p>
            <p style={{ fontSize: '11px', color: '#BBB', margin: 0 }}>
              PDF, DOCX, TXT, or image (PNG/JPG) · Up to 10 MB
            </p>

            <input
              ref={inputRef}
              type="file"
              accept={ACCEPT_STRING}
              onChange={onInputChange}
              style={{ display: 'none' }}
            />
          </div>
        ) : (
          /* File preview */
          <div style={{
            border: '1px solid #E5E5E3',
            borderRadius: '10px',
            padding: '14px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}>
            {/* File-type badge */}
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: meta.bg,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}>
              <span style={{ fontSize: '10px', fontWeight: '700', color: meta.color, letterSpacing: '0.02em' }}>
                {meta.label}
              </span>
            </div>

            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{
                fontSize: '13px',
                fontWeight: '500',
                color: '#111',
                margin: 0,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {file.name}
              </p>
              <p style={{ fontSize: '11px', color: '#999', margin: '2px 0 0' }}>
                {formatSize(file.size)}
              </p>
            </div>

            {/* Remove button */}
            <button
              onClick={removeFile}
              disabled={loading}
              style={{
                background: 'none',
                border: 'none',
                cursor: loading ? 'not-allowed' : 'pointer',
                padding: '4px',
                borderRadius: '6px',
                color: '#999',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'color 0.15s',
              }}
              onMouseEnter={e => e.currentTarget.style.color = '#DC2626'}
              onMouseLeave={e => e.currentTarget.style.color = '#999'}
              title="Remove file"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        )}

        {error && (
          <p style={{
            fontSize: '12px',
            color: '#DC2626',
            margin: '8px 0 0',
            padding: '6px 10px',
            background: '#FEF2F2',
            borderRadius: '6px',
          }}>
            {error}
          </p>
        )}
      </div>

      <div style={{
        padding: '12px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        borderTop: '0.5px solid #F0F0EE',
        marginTop: '8px',
        gap: '8px',
      }}>
        {hasResult && (
          <button
            onClick={() => { removeFile(); onReset(); }}
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
          onClick={() => file && onSubmit(file)}
          disabled={!file || loading}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '7px 16px',
            background: file && !loading ? '#111' : '#E5E5E3',
            color: file && !loading ? '#fff' : '#AAA',
            border: 'none',
            borderRadius: '7px',
            fontSize: '13px',
            fontWeight: '500',
            cursor: file && !loading ? 'pointer' : 'not-allowed',
            transition: 'all 0.15s',
          }}
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 1L13 7L7 13M1 7h12" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          {loading ? 'Analysing...' : 'Analyse document'}
        </button>
      </div>
    </div>
  )
}
