from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class SchemaType(str, Enum):
    legal_contract = "legal_contract"
    invoice = "invoice"
    resume = "resume"


# ── Legal Contract ────────────────────────────────────────────────────────────

class Party(BaseModel):
    name: str = Field(description="Full legal name of the party")
    role: str = Field(description="Role in the contract, e.g. Landlord, Tenant, Vendor, Client")

class KeyClause(BaseModel):
    title: str = Field(description="Short clause title or section name")
    summary: str = Field(description="One-sentence summary of what the clause says")

class LegalContractExtraction(BaseModel):
    document_type: str = Field(description="Type of legal document, e.g. Lease Agreement, Service Contract, NDA")
    parties: list[Party] = Field(description="All named parties in the document")
    effective_date: Optional[str] = Field(default=None, description="Contract start date if mentioned")
    expiry_date: Optional[str] = Field(default=None, description="Contract end or expiry date if mentioned")
    jurisdiction: Optional[str] = Field(default=None, description="Governing law or jurisdiction stated in the document")
    total_value: Optional[str] = Field(default=None, description="Total monetary value if stated")
    key_clauses: list[KeyClause] = Field(description="Most important clauses identified")
    obligations: list[str] = Field(description="Key obligations of each party as plain statements")
    confidence_notes: Optional[str] = Field(default=None, description="Any ambiguities or fields the model is uncertain about")


# ── Invoice ───────────────────────────────────────────────────────────────────

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[str] = None
    total: Optional[str] = None

class InvoiceExtraction(BaseModel):
    invoice_number: Optional[str] = Field(default=None, description="Invoice or reference number")
    vendor_name: Optional[str] = Field(default=None, description="Name of the business issuing the invoice")
    vendor_abn: Optional[str] = Field(default=None, description="ABN or tax ID of the vendor if present")
    client_name: Optional[str] = Field(default=None, description="Name of the client being billed")
    issue_date: Optional[str] = Field(default=None, description="Date the invoice was issued")
    due_date: Optional[str] = Field(default=None, description="Payment due date")
    line_items: list[LineItem] = Field(description="Individual line items or services billed")
    subtotal: Optional[str] = Field(default=None, description="Subtotal before tax")
    tax_amount: Optional[str] = Field(default=None, description="GST or tax amount")
    total_amount: Optional[str] = Field(default=None, description="Total amount due including tax")
    payment_terms: Optional[str] = Field(default=None, description="Payment terms if stated")
    confidence_notes: Optional[str] = Field(default=None, description="Any ambiguities or fields the model is uncertain about")


# ── Resume ────────────────────────────────────────────────────────────────────

class WorkExperience(BaseModel):
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsibilities: list[str] = Field(description="Key responsibilities or achievements")

class Education(BaseModel):
    institution: str
    qualification: str
    year: Optional[str] = None

class ResumeExtraction(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = Field(default=None, description="Professional summary if present")
    skills: list[str] = Field(description="Technical and professional skills listed")
    work_experience: list[WorkExperience] = Field(description="Work history in reverse chronological order")
    education: list[Education] = Field(description="Educational qualifications")
    certifications: list[str] = Field(default_factory=list, description="Professional certifications or licences")
    confidence_notes: Optional[str] = Field(default=None, description="Any ambiguities or fields the model is uncertain about")