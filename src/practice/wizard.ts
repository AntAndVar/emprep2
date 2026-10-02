import type { Draft, FieldErrors, WizardStep } from '../types';

/** TICKET 01 — implement step validation using the supplied acceptance criteria.
 * Steps 0 and 1 validate their own fields; step 2 includes both earlier steps
 * and requires explicit consent. All rules are fictional practice constraints.
 */
export function validateStep(draft: Draft, step: WizardStep): FieldErrors {
  // TODO(ticket-01): return field-specific messages for the current step.
  void draft;
  void step;
  return {};
}
