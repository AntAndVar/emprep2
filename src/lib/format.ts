import type { Application, DocKind, Draft } from '../types';

const dateFormatter = new Intl.DateTimeFormat('en-CA', {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
  timeZone: 'UTC',
});

/** Show the recorded calendar date consistently across computers. */
export function dateLabel(iso: string): string {
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? '—' : dateFormatter.format(date);
}

export function initials(name: string): string {
  const words = name.trim().split(/\s+/).filter(Boolean);
  if (!words.length) return '';
  const first = words[0][0];
  const last = words.length > 1 ? words[words.length - 1][0] : '';
  return `${first}${last}`.toUpperCase();
}

/** Supplied fictional checklist, shared by the UI and its progress display. */
export function requiredDocumentKinds(draft: Draft): DocKind[] {
  const required: DocKind[] = ['identity', 'address'];
  if (draft.accountType === 'joint') required.push('joint-identity');
  if (draft.fundingSource !== 'salary') required.push('source-of-funds');
  return required;
}

/** Count required kinds, not files: duplicate uploads cannot inflate progress. */
export function documentProgress(application: Application): {
  verified: number;
  total: number;
  percent: number;
} {
  const required = requiredDocumentKinds(application.draft);
  const verifiedKinds = new Set(
    application.documents.filter(document => document.status === 'verified').map(document => document.kind),
  );
  const verified = required.filter(kind => verifiedKinds.has(kind)).length;
  const total = required.length;
  return { verified, total, percent: total === 0 ? 0 : Math.round((verified / total) * 100) };
}
