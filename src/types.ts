/** Fictional practice fields. These do not encode legal or suitability rules. */
export interface Draft {
  legalName: string;
  email: string;
  accountType: 'individual' | 'joint';
  jointApplicantName: string;
  employmentStatus: 'employed' | 'self-employed' | 'retired';
  annualIncomeBand: 'under-50k' | '50k-100k' | '100k-plus';
  fundingSource: 'salary' | 'business-sale' | 'inheritance';
  sourceDetails: string;
  objective: 'growth' | 'income' | 'preservation';
  riskComfort: 'low' | 'medium' | 'high';
  horizonYears: number;
  consent: boolean;
}

export type DocKind = 'identity' | 'address' | 'joint-identity' | 'source-of-funds';
export type DocumentStatus = 'requested' | 'received' | 'verified' | 'rejected';

export interface DocumentRecord {
  id: string;
  kind: DocKind;
  name: string;
  status: DocumentStatus;
  comment: string;
  updatedAt: string;
}

export interface Application {
  id: string;
  clientName: string;
  assignedAdvisor: string;
  status: 'draft' | 'submitted';
  version: number;
  updatedAt: string;
  draft: Draft;
  documents: DocumentRecord[];
}

export type FieldErrors = Partial<Record<keyof Draft, string>>;
export type WizardStep = 0 | 1 | 2;
