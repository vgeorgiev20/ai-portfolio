import type { ExtractionResponse } from '../types/extractions';

interface Props {
  result: ExtractionResponse | null
  loading: boolean
  error: string | null
}

function renderValue(value: unknown): React.ReactNode {
  if (value === null || value === undefined) {
    return <span style={{ color: '#9ca3af' }}>—</span>
  }

  if (Array.isArray(value)) {
    if (value.length === 0) return <span style={{ color: '#9ca3af' }}>—</span>

    if (typeof value[0] === 'string') {
      return (
        <ul style={{ margin: '4px 0 0 0', paddingLeft: '18px' }}>
          {value.map((item, i) => (
            <li key={i} style={{ fontSize: '13px', color: '#374151', marginBottom: '2px' }}>{item}</li>
          ))}
        </ul>
      )
    }

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '6px' }}>
        {value.map((item, i) => (
          <div key={i} style={{
            background: '#f9fafb',
            border: '1px solid #e5e7eb',
            borderRadius: '6px',
            padding: '10px 12px',
          }}>
            {Object.entries(item as Record<string, unknown>).map(([k, v]) => (
              <div key={k} style={{ display: 'flex', gap: '8px', marginBottom: '4px', fontSize: '13px' }}>
                <span style={{ color: '#6b7280', minWidth: '120px', flexShrink: 0 }}>
                  {k.replace(/_/g, ' ')}
                </span>
                <span style={{ color: '#111827' }}>{renderValue(v)}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    )
  }

  if (typeof value === 'object') {
    return (
      <div style={{ marginTop: '4px' }}>
        {Object.entries(value as Record<string, unknown>).map(([k, v]) => (
          <div key={k} style={{ fontSize: '13px', marginBottom: '2px' }}>
            <span style={{ color: '#6b7280' }}>{k.replace(/_/g, ' ')}: </span>
            <span style={{ color: '#111827' }}>{String(v)}</span>
          </div>
        ))}
      </div>
    )
  }

  return <span style={{ fontSize: '13px', color: '#111827' }}>{String(value)}</span>
}

export default function ResultCard({ result, loading, error }: Props) {
  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '300px', gap: '12px' }}>
        <div style={{
          width: '32px', height: '32px', borderRadius: '50%',
          border: '3px solid #e5e7eb', borderTopColor: '#1a56db',
          animation: 'spin 0.8s linear infinite',
        }} />
        <p style={{ color: '#6b7280', fontSize: '14px' }}>Extracting structured data...</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{
        background: '#fef2f2', border: '1px solid #fecaca',
        borderRadius: '8px', padding: '16px',
      }}>
        <p style={{ color: '#dc2626', fontSize: '14px', margin: 0 }}>⚠ {error}</p>
      </div>
    )
  }

  if (!result) {
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', height: '300px', gap: '8px',
        border: '2px dashed #e5e7eb', borderRadius: '8px',
      }}>
        <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>Extraction results will appear here</p>
        <p style={{ color: '#d1d5db', fontSize: '12px', margin: 0 }}>Paste text and click Extract Data</p>
      </div>
    )
  }

  const { result: data, character_count } = result
  const confidenceNotes = data.confidence_notes as string | null

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        marginBottom: '16px',
      }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, margin: 0, color: '#111827' }}>
          Extracted Fields
        </h2>
        <span style={{
          fontSize: '12px', color: '#6b7280',
          background: '#f3f4f6', padding: '3px 8px', borderRadius: '4px',
        }}>
          {character_count.toLocaleString()} chars processed
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {Object.entries(data)
          .filter(([key]) => key !== 'confidence_notes')
          .map(([key, value]) => (
            <div key={key} style={{
              borderBottom: '1px solid #f3f4f6',
              paddingBottom: '12px',
            }}>
              <div style={{
                fontSize: '11px', fontWeight: 600, textTransform: 'uppercase',
                letterSpacing: '0.05em', color: '#6b7280', marginBottom: '4px',
              }}>
                {key.replace(/_/g, ' ')}
              </div>
              {renderValue(value)}
            </div>
          ))}
      </div>

      {confidenceNotes && (
        <div style={{
          marginTop: '16px', background: '#fffbeb',
          border: '1px solid #fcd34d', borderRadius: '6px', padding: '12px',
        }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#92400e', marginBottom: '4px' }}>
            MODEL CONFIDENCE NOTES
          </div>
          <p style={{ fontSize: '13px', color: '#78350f', margin: 0 }}>{confidenceNotes}</p>
        </div>
      )}
    </div>
  )
}