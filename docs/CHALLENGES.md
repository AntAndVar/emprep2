# Client onboarding rehearsal: challenge brief

Build a small, coherent onboarding workflow for a fictional wealth-services team. The supplied application combines a multi-step form with a document review board. All applicants, documents and rules are synthetic. Document review changes metadata; it does not upload or inspect real identity documents.

This is a second independent rehearsal based on the invitation and public research. It is **not Electric Mind's actual challenge, a prediction of its feature list or an official scorecard**. Vue 3, TypeScript, Vite and the small Python API are this project's preparation choices; they are not claims about Electric Mind's mandated stack.

## Start and set the timebox

From `electric-mind-onboarding`:

```text
npm install
npm run dev
```

Open http://localhost:5174. The API runs on port 4001. The development launcher uses an available bundled Python runtime or a `PYTHON` environment setting; the API uses Python's standard library and needs no pip packages.

| Round | Choose | Outcome |
| --- | --- | --- |
| 60 minutes | Ticket 01 or Ticket 02 | One carefully verified form or review interaction |
| 90 minutes | Tickets 01 and 02 | Prepare an application, review its required documents and demonstrate the resulting submission path |
| 120 minutes | Core tickets first; consider Ticket 03 if time remains | Add draft persistence only if its async behavior can be finished and checked |

Estimates: **Ticket 01: 25 minutes; Ticket 02: 35 minutes; Ticket 03: 30 minutes; backend stretch: 10–15 minutes.** Planning, verification and a demo require additional time. Optional work can also be a separate rehearsal. Completing everything is not the objective.

## Ticket 01 — Guide the applicant through a conditional form

**User story:** As a team member preparing an application, I want the form to ask for the information relevant to this applicant and explain what needs correction before I continue.

**Work areas:** `src/practice/wizard.ts`, `validateStep(draft, step)`; and the supplied `StepProfile.vue` and `StepGoals.vue` components. The validation function starts as an empty-error stub. Implement the conditional fields in the existing step components and use the host's validation and navigation flow.

The draft has these fields:

| Group | Fields |
| --- | --- |
| Profile | `legalName`, `email`, `accountType`, `jointApplicantName`, `employmentStatus` |
| Goals and funding | `annualIncomeBand`, `fundingSource`, `sourceDetails`, `objective`, `riskComfort`, `horizonYears` |
| Review | `consent` |

The controls supply the enum choices: account type `individual`/`joint`; employment `employed`/`self-employed`/`retired`; annual income `under-50k`/`50k-100k`/`100k-plus`; funding `salary`/`business-sale`/`inheritance`; objective `growth`/`income`/`preservation`; risk comfort `low`/`medium`/`high`. Preserve those exact values and the existing typed contracts.

**Acceptance criteria:**

1. **Step 0, profile:** legal name has a trimmed length of **2–80 characters**. Email is required, passes a basic email-format check and is at most **254 characters**. This is practical form validation, not proof that an address exists.
2. Show `jointApplicantName` only for a joint account. It then requires a trimmed length of **2–80 characters**. It must not block an individual application.
3. **Step 1, goals:** `horizonYears` must be an integer from **1 through 50**, inclusive. Reject fractional, missing or out-of-range values rather than silently accepting them.
4. Show `sourceDetails` only when the funding source is `business-sale` or `inheritance`. It then requires a trimmed length of **10–500 characters**. It must not block salary funding.
5. **Step 2, review:** require `consent === true` and revalidate earlier steps. Navigating through the form once must not exempt later edits from validation.
6. Return field errors using the supplied `FieldErrors` contract. Invalid input must prevent the associated Continue or Submit action and produce clear inline feedback tied to the relevant field.
7. Keep inputs labeled and keyboard usable. Move focus sensibly after an invalid action. If review finds an error from an earlier step, help the user locate and correct it.
8. Preserve entered values when navigating Back. Conditional rendering should have a predictable policy for retaining hidden values; hidden, irrelevant fields must not block navigation.

**Verify:** Run `npm run test:practice` for the supplied acceptance checks. They intentionally fail until the exercise is implemented. In the browser, switch individual/joint and salary/non-salary several times, navigate backward, try whitespace and boundary values, and revisit review after changing an earlier answer.

**Design discussion:** Which questions belong together? Should optional context be explained with short help text? How does the applicant understand why a conditional question appears? Explain your policy for hidden values and error recovery before writing a larger abstraction.

## Ticket 02 — Review the document checklist

**User story:** As a reviewer, I want to see which required documents are complete, verify received items or reject them with a useful explanation, and understand what still blocks the application.

**Work area:** `src/practice/DocumentReviewBoard.vue`. The component takes an `application` prop and emits **`updated` with the saved `Application`**. Use `api.reviewDocument(appId, docId, status, comment, expectedVersion)`; it returns `{ application }`.

Required document kinds follow these fictional rules:

- `identity` and `address` are always required.
- `joint-identity` is additionally required for a joint account.
- `source-of-funds` is additionally required when funding is not salary.

**Acceptance criteria:**

1. Render every required document kind, including a clear incomplete state when its record is absent. Extra, unrelated records must not inflate completion.
2. Derive progress from the current application and its required kinds. Only a recognized required record marked `verified` counts as complete. Requested, received, rejected, missing and unknown states remain incomplete.
3. Provide keyboard-operable controls for reviewing received documents as `verified` or `rejected`. The API also permits `rejected` → `received` for a resubmitted sample and same-status changes; you may expose resubmission as an extension. Requested samples await receipt, and actual uploads are outside scope. Drag and drop is unnecessary.
4. A rejection requires a trimmed comment of **3–500 characters**, with specific feedback when invalid. Do not send an invalid rejection request.
5. Show which item is being saved and prevent duplicate review actions. Use the application's current `version` as `expectedVersion`.
6. On success, emit `updated` with the returned saved application. Derive the new board and progress from that response; do not claim that a change was saved before confirmation.
7. On failure, keep the board usable and preserve the rejection explanation for retry. Explain a conflict as a newer version, rather than silently overwriting it.
8. Make review status and progress understandable through text and semantic controls as well as color. A completed checklist should be legible without requiring the reviewer to count rows.

**Verify:** Review one received document, reject another with a valid comment and try a too-short comment. Compare progress for an individual/salary applicant and a joint/non-salary applicant. Confirm a missing required document prevents a complete result. Test duplicate clicks, keyboard operation and a network failure.

## Ticket 03 — Optional alternative: save and restore a draft

**User story:** As a team member, I want edits to persist without losing my work or accidentally replacing another person's newer application.

**Work area:** `src/practice/useDraftAutosave.ts`.

The supplied hook takes `{ application, draft, paused, onUpdated }`, where `application` is a computed reference to the selected application or null, `draft` is the local draft reference, `paused` is a boolean reference controlled by the host during final submission, and `onUpdated` receives a saved application. It returns:

- `state`: a reference with `idle`, `saving`, `saved`, `error` or `conflict`.
- `message`: a reference containing useful feedback.
- `saveNow()`: an asynchronous explicit save.
- `restore()`: an asynchronous restore of the server's saved draft.

The starter hook only displays messages. Persistence is deliberately unfinished. Use `api.saveDraft(id, draft, expectedVersion)`, which returns `{ application }`. Restore through `api.applications()` and find the selected ID; there is no dedicated restore route.

Draft storage deliberately permits incomplete answers. Do not require the complete step/submission criteria before saving an in-progress draft. The API still validates the draft's structure, enums and storage limits; those broader storage limits are described in `server/README.md`.

**Acceptance criteria:**

1. Save after **800 ms** without further edits, with an explicit Save action also available. Do not save simply because the hook mounts or a different applicant is selected.
2. Snapshot the outgoing draft when a save begins. Keep later local edits intact, and make pending, saved and error states visible without treating a queued edit as already saved.
3. Use the current `expectedVersion`. Apply a confirmed response through `onUpdated`, updating application metadata without replacing newer local input.
4. When selection changes, reset the relevant hook state. A slow response for the old applicant must never replace the newly selected applicant's metadata or draft.
5. Preserve local input after failures. A **409 conflict** requires an explicit choice: reload the saved version or keep the local draft for reconciliation. Keeping local work must not automatically overwrite a newer server version.
6. Restore deliberately: fetch current server data and explicitly replace the local draft with a fresh copy of its saved draft. Make the effect on unsaved work understandable.
7. Watch `paused` and cancel any queued debounce when it becomes true. Suppress autosave and explicit hook saves while paused or after submission. Submitted applications remain immutable; do not present a misleading successful draft-save state.

**Verify:** Type several quick edits, then pause; switch applicants during a slow save; fail a request; restore; and create a stale-version conflict with two tabs. Start final submission while a debounce timer is queued and confirm that no autosave write races it. Explain the version you are saving and what the interface does with later local edits.

This hook is distinct from the host's supplied **final save before submission**. Core submission first saves the current draft, then submits using the saved application's version. The host disables Submit while the hook's state is `saving` and checks that guard before submitting. It then pauses the hook during the final save-and-submit sequence; no autosave writes may occur during that sequence. Ticket 03 improves draft work between those actions; it is not required merely to avoid submitting an older draft.

## Backend stretch — Enforce submission readiness at the API boundary

**Work area:** `server/rules.py`, `submission_issues`. It starts as an empty-list stub so the server-side guard is an explicit exercise.

Enforce the profile and goals limits above, consent, and verified required document kinds. Identity and address are always required; joint identity and source-of-funds follow the same conditional rules as the board. Missing or unrecognized required records must not pass readiness checks. Preserve existing version/conflict and submitted-immutability handling.

The host checks readiness for the normal UI flow. The backend stretch makes direct API calls obey the same rules. Do not describe frontend checks alone as server enforcement. Use the existing response format and report useful issues instead of adding a separate policy framework.

## Checks and scope

| API route | Payload / response |
| --- | --- |
| GET `/api/applications` | `{ applications }` |
| PUT `/api/applications/{id}/draft` | `{ draft, expectedVersion }` → `{ application }` |
| PATCH `/api/applications/{id}/documents/{documentId}` | `{ status, comment, expectedVersion }` → `{ application }` |
| POST `/api/applications/{id}/submit` | `{ expectedVersion }` → `{ application }` |

Errors contain `{ error: { code, message } }`. A version conflict returns HTTP 409 and `currentApplication`; submission-readiness errors use HTTP 422 and `issues`. Every successful write increments the application version. GET `/api/applications?fail=1` simulates a temporary service error; remove the parameter to recover.

Run `npm test` for supplied baseline API and formatting checks, `npm run test:practice` for intentionally unfinished exercises, and `npm run build` for Vue/TypeScript and Vite build validation. Baseline checks passing means the starter's plumbing works; it does not prove unfinished business rules are implemented.

Keep the local servers running while testing integration. Use the typed API client rather than duplicating request contracts. Preserve version handling and submitted immutability. No authentication system, real file uploads, OCR, payment operation or live AI feature is needed for this rehearsal.

KYC means “know your client”: gathering enough information to understand a client and their circumstances. The synthetic document and consent rules here are exercise requirements, not legal guidance.

For research context, read the original [company research](../../electric-mind-practice/docs/RESEARCH.md) and [technology and culture report](../../electric-mind-practice/docs/TECH-AND-CULTURE.md). Electric Mind's August 2026 [wealth-management podcast](https://www.electricmind.com/whats-on-our-mind/electric-mindset-episode-11-wealth-managements-ai-credibility-gap) discusses onboarding and advisor work; it supports the domain choice without revealing an assessment specification.
