# Entry — wealth onboarding practice

A second, independent assessment rehearsal for **October 3, 2026**. This project keeps most work in the frontend while changing the stack and interaction structure. It is not Electric Mind's actual challenge or a claim about its assessment stack.

## What is different

| First project: Advisor Desk | This project: Entry |
| --- | --- |
| React + TypeScript | Vue 3 + TypeScript, Composition API and single-file components |
| Native Node API | Small Python 3.11+ standard-library API |
| Household search and dashboard | Guided, three-step client application |
| Service-request modal | Document checklist/status review with rejection reasons |
| Simulated AI meeting draft | Optional autosave, restore and version-conflict handling |

Vite, npm and plain CSS remain familiar. There is no router, state-management library, authentication setup, live AI service, database installation or pip dependency to learn before the practice round.

## Run it

Dependencies are installed in this workspace. Requires Node.js **22.12+ or 24+** and Python **3.11+**. The launcher discovers the bundled Python on this computer; on another machine use installed Python or set `PYTHON` to its executable.

```powershell
cd C:\emprep\electric-mind-onboarding
npm run dev
```

Open **http://127.0.0.1:5174**. The command starts Vue on port 5174 and Python on port 4001. These differ from the original project so the two can run together. Keep the terminal open; Ctrl+C stops the processes. If PowerShell blocks the npm script wrapper, use `npm.cmd`.

On another machine run `npm ci` first. After dependencies are installed, all practice behavior works offline. To select Python explicitly in PowerShell:

```powershell
$env:PYTHON = 'C:\path\to\python.exe'
npm run dev
```

## Working baseline and intentional exercises

The baseline loads four synthetic applications; lets you choose an applicant, edit fields and move between steps; preserves local edits when moving back or switching applicants; derives a required-document readiness summary; and displays a read-only document preview. Final submission saves the current draft and then submits its returned server version. Submitted applications become read-only. Failure/retry, empty and loading states are supplied.

The exercise slots are deliberately unfinished:

| Ticket | Work area | Coding estimate |
| --- | --- | --- |
| **01: guide a valid application** | `src/practice/wizard.ts`, `StepProfile.vue`, `StepGoals.vue` | 25 min |
| **02: review and save document decisions** | `src/practice/DocumentReviewBoard.vue` | 35 min |
| **03: preserve work through autosave and restore** | `src/practice/useDraftAutosave.ts` | 30 min, optional/alternate |
| Backend stretch: enforce readiness on direct submission | `server/rules.py` | 10–15 min, optional |

In the starter, `validateStep` returns no errors; joint-applicant/funding-context fields always show; document review has no action controls; Save draft/Restore show an exercise message; and server completeness validation is a pass-through. These are explicit practice slots, not accidental defects. **Final submission already saves the draft**, independently of optional autosave.

Before autosave is implemented, local edits survive navigation in the current session but are lost on refresh unless you submit. The interface distinguishes local edits from the saved record. No reference solution is included.

## Pick a realistic round

Recommended: **90 minutes for tickets 01 + 02** — 10 minutes agree/sketch, 60 minutes build, 10 minutes verify, 10 minutes demo. For 60 minutes, choose one ticket. For 120 minutes, add a stretch after the core flow works; completing every ticket is unnecessary.

Read [the detailed challenge briefs](docs/CHALLENGES.md) and [the rehearsal playbook](docs/PLAYBOOK.md). The built-in Practice guide gives you a concise overview.

Useful applications:

- **Olivia Chen:** individual account, one received document to review. Good first end-to-end path.
- **Gabriel & Alex Rivera:** joint account, business-sale funding, rejected/received documents. Tests conditional fields and review states.
- **Elliot Morgan:** all document types verified. Lets you inspect the supplied submission flow before implementing document review.
- **Jamie Park:** incomplete form and documents not yet received. Tests validation and blocked readiness; uploading new documents is outside scope.

The fields and document rules are fictional preparation rules, not legal compliance or investment advice. No actual files are uploaded or inspected; document names are synthetic metadata.

## Verify your work

```text
npm test
npm run build
npm run test:practice
```

`npm test` runs Python API tests and supplied frontend-helper checks. `npm run build` checks Vue/TypeScript and builds the app. Both should pass in the starter.

**`npm run test:practice` intentionally fails until ticket 01 is implemented.** Its nine tests express the wizard validation criteria. Keep those criteria intact while implementing the function. Manually verify conditional visibility, focus, keyboard use, document actions and retained input after failure.

For failure recovery, open **http://127.0.0.1:5174/?fail=1** and choose **Try again**. To simulate a version conflict, open the same application in two browser tabs and save a change in each; the second stale write returns 409.

For a production-bundle preview, run `npm run dev:api` and `npm run preview` after building; the preview uses port 4174. This remains a local training application with no authentication.

## Code map

```text
src/App.vue                    Supplied selection, step navigation and submit flow
src/practice/wizard.ts          Ticket 01: validation function
src/practice/StepProfile.vue    Ticket 01: joint-applicant conditional field
src/practice/StepGoals.vue      Ticket 01: funding-context conditional field
src/practice/DocumentReviewBoard.vue  Ticket 02: reviewed document decisions
src/practice/useDraftAutosave.ts     Ticket 03: autosave/restore composable
src/lib/api.ts                 Typed fetch client and conflict errors
src/lib/format.ts              Required document kinds and derived progress
src/types.ts                   Shared frontend contracts
server/                        Small Python API, seed data, tests and rules TODO
scripts/python.mjs             Cross-machine Python discovery
docs/                          Challenge briefs and rehearsal guidance
```

The API persists changes in ignored `server/data/state.json`. To reset, stop the API, delete only that generated file and restart. It will reseed automatically. See [the API guide](server/README.md).

## Context and a short Vue refresher

The original research remains in [company/client research](../electric-mind-practice/docs/RESEARCH.md) and [technology/culture findings](../electric-mind-practice/docs/TECH-AND-CULTURE.md). Wealth onboarding and advisor workflows informed this second exercise; Vue/Python is chosen to vary your practice, not because public evidence proves it is Electric Mind's standard stack.

Vue components put TypeScript in `<script setup>` and markup in `<template>`. `ref` holds reactive state, `computed` derives values, and `v-model` connects form inputs to state. Parent components receive saved decisions through emitted events. The optional autosave exercise packages stateful behavior in a composable. See the official [form binding guide](https://vuejs.org/guide/essentials/forms.html) and [composable guide](https://vuejs.org/guide/reusability/composables.html) when needed.
