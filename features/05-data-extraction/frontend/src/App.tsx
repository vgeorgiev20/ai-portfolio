import { useState, useEffect } from 'react'
import axios from 'axios'
import type { SchemaType, SchemaOption, ExtractionResponse } from './types/extractions'
import ExtractorForm from './components/ExtractorForm'
import ResultCard from './components/ResultCard'

const API_BASE = ''

export default function App() {
  const [text, setText] = useState('')
  const [schemaType, setSchemaType] = useState<SchemaType>('legal_contract')
  const [schemas, setSchemas] = useState<SchemaOption[]>([])
  const [result, setResult] = useState<ExtractionResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    axios.get(`${API_BASE}/api/schemas`)
      .then(res => setSchemas(res.data))
      .catch(() => setSchemas([
        { value: 'legal_contract', label: 'Legal Contract' },
        { value: 'invoice', label: 'Invoice' },
        { value: 'resume', label: 'Resume / CV' },
      ]))
  }, [])

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await axios.post(`${API_BASE}/api/extract`, {
        schema_type: schemaType,
        text,
      })
      setResult(res.data)
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail ?? 'Something went wrong.')
      } else {
        setError('Something went wrong.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    }}>
      <div style={{
        maxWidth: '1100px',
        margin: '0 auto',
        padding: '40px 24px',
      }}>
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '24px', fontWeight: 700, margin: '0 0 6px', color: '#111827' }}>
            Data Extraction
          </h1>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
            Paste unstructured text. Get structured data.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '24px',
          alignItems: 'start',
        }}>
          <div style={{
            background: '#fff',
            borderRadius: '10px',
            border: '1px solid #e5e7eb',
            padding: '24px',
          }}>
            <ExtractorForm
              text={text}
              schemaType={schemaType}
              schemas={schemas}
              loading={loading}
              onTextChange={setText}
              onSchemaChange={(s) => { setSchemaType(s); setResult(null); setError(null) }}
              onSubmit={handleSubmit}
            />
          </div>

          <div style={{
            background: '#fff',
            borderRadius: '10px',
            border: '1px solid #e5e7eb',
            padding: '24px',
            minHeight: '400px',
          }}>
            <ResultCard result={result} loading={loading} error={error} />
          </div>
        </div>
      </div>
    </div>
  )
}