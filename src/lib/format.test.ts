import { describe, expect, it } from 'vitest';
import type { Application, DocumentRecord, Draft } from '../types';
import { dateLabel, documentProgress, initials, requiredDocumentKinds } from './format';

const draft: Draft = {
  legalName: 'Avery Patel', email: 'avery@example.test', accountType: 'individual', jointApplicantName: '',
  employmentStatus: 'employed', annualIncomeBand: '50k-100k', fundingSource: 'salary', sourceDetails: '',
  objective: 'growth', riskComfort: 'medium', horizonYears: 10, consent: false,
};

function record(kind: DocumentRecord['kind'], status: DocumentRecord['status'], id = `${kind}-${status}`): DocumentRecord {
  return { id, kind, name: `${kind}.pdf`, status, comment: '', updatedAt: '2026-10-03T12:00:00Z' };
}

function application(documents: DocumentRecord[], changes: Partial<Draft> = {}): Application {
  return {
    id: 'app-practice', clientName: 'Avery Patel', assignedAdvisor: 'Jordan Lee', status: 'draft',
    version: 1, updatedAt: '2026-10-03T12:00:00Z', draft: { ...draft, ...changes }, documents,
  };
}

describe('supplied formatting and checklist helpers', () => {
  it('formats ISO dates without moving midnight to the previous calendar day', () => {
    expect(dateLabel('2026-10-03T00:00:00Z')).toBe(dateLabel('2026-10-03T12:00:00Z'));
    expect(dateLabel('2026-10-03T00:00:00Z')).toContain('3');
    expect(dateLabel('invalid')).toBe('—');
  });

  it('uses first and last initials and handles single or empty names', () => {
    expect(initials('  avery Morgan patel  ')).toBe('AP');
    expect(initials('Avery')).toBe('A');
    expect(initials('   ')).toBe('');
  });

  it('starts with identity and address and adds only the applicable document kinds', () => {
    expect(requiredDocumentKinds(draft)).toEqual(['identity', 'address']);
    expect(requiredDocumentKinds({ ...draft, accountType: 'joint' })).toEqual(['identity', 'address', 'joint-identity']);
    expect(requiredDocumentKinds({ ...draft, fundingSource: 'inheritance' })).toEqual(['identity', 'address', 'source-of-funds']);
    expect(requiredDocumentKinds({ ...draft, accountType: 'joint', fundingSource: 'business-sale' })).toEqual([
      'identity', 'address', 'joint-identity', 'source-of-funds',
    ]);
  });

  it('shows zero verified progress when required documents are missing', () => {
    expect(documentProgress(application([]))).toEqual({ verified: 0, total: 2, percent: 0 });
    expect(documentProgress(application([], { accountType: 'joint', fundingSource: 'inheritance' }))).toEqual({
      verified: 0, total: 4, percent: 0,
    });
  });

  it('counts only verified required kinds rather than received, rejected or requested files', () => {
    const documents = [record('identity', 'verified'), record('address', 'received'), record('address', 'rejected'), record('address', 'requested')];
    expect(documentProgress(application(documents))).toEqual({ verified: 1, total: 2, percent: 50 });
  });

  it('ignores duplicate and irrelevant verified files', () => {
    const documents = [record('identity', 'verified', 'one'), record('identity', 'verified', 'two'), record('joint-identity', 'verified')];
    expect(documentProgress(application(documents))).toEqual({ verified: 1, total: 2, percent: 50 });
  });

  it('requires all conditional kinds for full progress and does not mutate documents', () => {
    const documents = [record('identity', 'verified'), record('address', 'verified'), record('joint-identity', 'verified')];
    const item = application(documents, { accountType: 'joint', fundingSource: 'business-sale' });
    const before = JSON.stringify(item);
    expect(documentProgress(item)).toEqual({ verified: 3, total: 4, percent: 75 });
    expect(JSON.stringify(item)).toBe(before);
    expect(documentProgress({ ...item, documents: [...documents, record('source-of-funds', 'verified')] })).toEqual({
      verified: 4, total: 4, percent: 100,
    });
  });
});
