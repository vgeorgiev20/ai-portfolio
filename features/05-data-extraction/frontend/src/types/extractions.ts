export type SchemaType = 'legal_contract' | 'invoice' | 'resume'

export interface SchemaOption {
  value: SchemaType
  label: string
}

export interface ExtractionResponse {
  schema_type: string
  result: Record<string, unknown>
  character_count: number
}