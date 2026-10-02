// Executable acceptance criteria. This suite intentionally fails until Ticket 01 is implemented.
import { describe, expect, it } from 'vitest';
import type { Draft } from '../types';
import { validateStep } from './wizard';

const validDraft: Draft = {
  legalName: 'Avery Patel', email: 'avery@example.test', accountType: 'individual', jointApplicantName: '',
  employmentStatus: 'employed', annualIncomeBand: '50k-100k', fundingSource: 'salary', sourceDetails: '',
  objective: 'growth', riskComfort: 'medium', horizonYears: 10, consent: true,
};

const withFields = (fields: Partial<Draft>): Draft => ({ ...validDraft, ...fields });

describe('Ticket 01: onboarding wizard validation', () => {
  it('accepts trimmed names of 2–80 characters and rejects names outside those bounds', () => {
    expect(validateStep(withFields({ legalName: '  Al  ' }), 0)).toEqual({});
    expect(validateStep(withFields({ legalName: 'A'.repeat(80) }), 0)).toEqual({});
    for (const legalName of [' ', 'A', 'A'.repeat(81)]) {
      expect(validateStep(withFields({ legalName }), 0).legalName).toEqual(expect.any(String));
    }
  });

  it('requires a basic email with non-whitespace text around @ and a domain dot', () => {
    expect(validateStep(withFields({ email: 'avery@example.test' }), 0)).toEqual({});
    for (const email of ['', 'averyexample.test', 'avery@example', '@example.test', 'avery@.test', 'avery @example.test']) {
      expect(validateStep(withFields({ email }), 0).email).toEqual(expect.any(String));
    }
  });

  it('requires a 2–80 character joint applicant name only for a joint account', () => {
    expect(validateStep(withFields({ jointApplicantName: '' }), 0)).toEqual({});
    expect(validateStep(withFields({ accountType: 'joint', jointApplicantName: '  Jo  ' }), 0)).toEqual({});
    expect(validateStep(withFields({ accountType: 'joint', jointApplicantName: 'J'.repeat(80) }), 0)).toEqual({});
    for (const jointApplicantName of ['', 'J', 'J'.repeat(81)]) {
      expect(validateStep(withFields({ accountType: 'joint', jointApplicantName }), 0).jointApplicantName).toEqual(expect.any(String));
    }
  });

  it('collects all current-step errors without validating later-step fields early', () => {
    const errors = validateStep(withFields({ legalName: '', email: '', horizonYears: 0, consent: false }), 0);
    expect(Object.keys(errors).sort()).toEqual(['email', 'legalName']);
  });

  it('requires a whole-number horizon between 1 and 50 inclusive', () => {
    for (const horizonYears of [1, 50]) expect(validateStep(withFields({ horizonYears }), 1)).toEqual({});
    for (const horizonYears of [0, 51, 1.5, Number.NaN, Number.POSITIVE_INFINITY]) {
      expect(validateStep(withFields({ horizonYears }), 1).horizonYears).toEqual(expect.any(String));
    }
  });

  it('requires trimmed source details of 10–500 characters for either non-salary funding source', () => {
    for (const fundingSource of ['business-sale', 'inheritance'] as const) {
      expect(validateStep(withFields({ fundingSource, sourceDetails: '  ' + 'a'.repeat(10) + '  ' }), 1)).toEqual({});
      expect(validateStep(withFields({ fundingSource, sourceDetails: 'a'.repeat(500) }), 1)).toEqual({});
      for (const sourceDetails of ['', 'a'.repeat(9), 'a'.repeat(501)]) {
        expect(validateStep(withFields({ fundingSource, sourceDetails }), 1).sourceDetails).toEqual(expect.any(String));
      }
    }
  });

  it('does not require source details for salary or revalidate step 0 while editing step 1', () => {
    expect(validateStep(withFields({ fundingSource: 'salary', sourceDetails: '', legalName: '', email: '', consent: false }), 1)).toEqual({});
    const errors = validateStep(withFields({ horizonYears: 0, fundingSource: 'inheritance', sourceDetails: '' }), 1);
    expect(Object.keys(errors).sort()).toEqual(['horizonYears', 'sourceDetails']);
  });

  it('requires consent at the final step and accepts a fully valid draft', () => {
    expect(validateStep(validDraft, 2)).toEqual({});
    expect(validateStep(withFields({ consent: false }), 2).consent).toEqual(expect.any(String));
  });

  it('revalidates earlier steps at final review and preserves the original draft', () => {
    const draft = withFields({ legalName: '', email: '', accountType: 'joint', jointApplicantName: '', horizonYears: 0, fundingSource: 'inheritance', sourceDetails: '', consent: false });
    const before = JSON.stringify(draft);
    expect(Object.keys(validateStep(draft, 2)).sort()).toEqual([
      'consent', 'email', 'horizonYears', 'jointApplicantName', 'legalName', 'sourceDetails',
    ]);
    expect(JSON.stringify(draft)).toBe(before);
  });
});
