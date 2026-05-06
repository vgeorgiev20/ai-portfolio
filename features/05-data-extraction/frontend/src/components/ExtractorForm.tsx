import type { SchemaType, SchemaOption } from '../types/extractions';

interface Props {
  text: string
  schemaType: SchemaType
  schemas: SchemaOption[]
  loading: boolean
  onTextChange: (text: string) => void
  onSchemaChange: (schema: SchemaType) => void
  onSubmit: () => void
}

const PLACEHOLDERS: Record<SchemaType, string> = {
  legal_contract: `SERVICE AGREEMENT\n\nThis Service Agreement is entered into as of January 15, 2025, between Nexus Consulting Pty Ltd ABN 45 123 456 789 ("Service Provider") and Brightfield Holdings Pty Ltd ("Client").\n\nThe Service Provider agrees to deliver software development services. The Client agrees to pay a monthly retainer of $12,500 AUD...`,
  invoice: `TAX INVOICE\n\nAcme Web Solutions Pty Ltd\nABN: 55 234 567 890\n\nInvoice Number: INV-2025-0047\nDate: 15 March 2025\nDue Date: 14 April 2025\n\nWebsite redesign: $3,500.00\nFrontend development (40hrs): $5,800.00\n\nSubtotal: $9,300.00\nGST: $930.00\nTotal: $10,230.00`,
  resume: `SARAH CHEN\nsarah.chen@email.com | 0412 345 678 | Melbourne, VIC\n\nSENIOR SOFTWARE ENGINEER\n\nSKILLS\nPython, TypeScript, React, FastAPI, PostgreSQL, Docker, AWS\n\nEXPERIENCE\nSenior Engineer — Canva, Sydney\nJan 2022 – Present\n- Led migration of legacy monolith to microservices`,
}

export default function ExtractorForm({
  text,
  schemaType,
  schemas,
  loading,
  onTextChange,
  onSchemaChange,
  onSubmit,
}: Props) {
  const charCount = text.length
  const atLimit = charCount > 8000

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div>
        <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, marginBottom: '6px', color: '#374151' }}>
          Schema Type
        </label>
        <select
          value={schemaType}
          onChange={e => onSchemaChange(e.target.value as SchemaType)}
          style={{
            width: '100%',
            padding: '8px 12px',
            borderRadius: '6px',
            border: '1px solid #d1d5db',
            fontSize: '14px',
            backgroundColor: '#fff',
            cursor: 'pointer',
          }}
        >
          {schemas.map(s => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
      </div>

      <div>
        <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, marginBottom: '6px', color: '#374151' }}>
          Raw Document Text
        </label>
        <textarea
          value={text}
          onChange={e => onTextChange(e.target.value)}
          placeholder={PLACEHOLDERS[schemaType]}
          rows={16}
          style={{
            width: '100%',
            padding: '10px 12px',
            borderRadius: '6px',
            border: `1px solid ${atLimit ? '#ef4444' : '#d1d5db'}`,
            fontSize: '13px',
            fontFamily: 'monospace',
            resize: 'vertical',
            boxSizing: 'border-box',
            lineHeight: 1.6,
          }}
        />
        <div style={{
          fontSize: '12px',
          marginTop: '4px',
          textAlign: 'right',
          color: atLimit ? '#ef4444' : '#6b7280',
        }}>
          {charCount.toLocaleString()} / 8,000 characters
        </div>
      </div>

      <button
        onClick={onSubmit}
        disabled={!text.trim() || loading || atLimit}
        style={{
          padding: '10px 20px',
          backgroundColor: !text.trim() || loading || atLimit ? '#93c5fd' : '#1a56db',
          color: '#fff',
          border: 'none',
          borderRadius: '6px',
          fontSize: '14px',
          fontWeight: 500,
          cursor: !text.trim() || loading || atLimit ? 'not-allowed' : 'pointer',
          transition: 'background-color 0.2s',
        }}
      >
        {loading ? 'Extracting...' : 'Extract Data'}
      </button>
    </div>
  )
}