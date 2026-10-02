# Onboarding rehearsal playbook

Use this round to practice turning conditional requirements into a clear interface, collaborating with a partner and explaining a saved result. The exercise is frontend focused, with a small persistence boundary that makes validation, pending states and conflicting edits visible.

The invitation says the assessment considers how you think, build, work with others and articulate a solution, with AI available and no expectation to finish. The practices below are inferred preparation, **not an official assessment rubric or a prediction of its challenge**.

## Event context

The invitation gives **Saturday, October 3, 2026**, doors at **10:30 a.m.**, welcome at **11 a.m.**, and closing remarks at **3:30 p.m.**, Toronto time. It requests a laptop and an RSVP with your preferred development domain and AI subscription. The location is **35 John Street, second floor, Toronto**.

The 4.5-hour event also includes a demo, AMA, conversations, networking and lunch. Coding time is unknown. Rehearse a bounded feature session with time reserved for discussion, verification and demonstration.

## Prepare a useful starting position

Run the project before the timer. Check that the page and Python API start together, a sample application loads, baseline checks run and your chosen AI tool is available. No Python packages or external account are required for this scaffold. Learn the main data types and API calls; you should be able to describe the difference between the local draft, the saved application and its version.

Vue 3, TypeScript, Vite and Python are chosen for this second rehearsal. Do not infer that Electric Mind uses this exact stack or that the assessment will require it. The original [research](../../electric-mind-practice/docs/RESEARCH.md) and [technology/culture report](../../electric-mind-practice/docs/TECH-AND-CULTURE.md) remain the evidence base.

## Agree the user journey with your partner

Before typing, say what each of you understands and where you need context. Pick one primary user: someone preparing an application, or someone reviewing documents. Connect the feature to the person's next action rather than treating it as a list of components.

A 90-minute core journey is: **enter the applicant's relevant information, resolve validation errors, review required documents and demonstrate submission readiness**. Start with a joint applicant funded through an inheritance or business sale to expose conditional requirements. Also test an individual/salary applicant so irrelevant fields do not block progress.

Ask about ambiguities that affect behavior. For this fictional exercise, the answers are in [CHALLENGES.md](CHALLENGES.md); at an actual assessment, ask the facilitator when a rule is unclear. Identify the minimum acceptance checks and sketch the profile step, goals step, review state and document card together.

## Keep a realistic timebox

| Time | 90-minute core round |
| --- | --- |
| 0–10 minutes | Clarify rules, sketch and agree work ownership |
| 10–35 minutes | Ticket 01: conditional fields and validation |
| 35–70 minutes | Ticket 02: document review and saved updates |
| 70–80 minutes | Verify the complete journey and one failure path |
| 80–90 minutes | Demonstrate, explain tradeoffs and note the next improvement |

For a 60-minute round, choose one core ticket and leave enough time to verify it. For 120 minutes, protect the final 20–25 minutes for verification and demonstration. Ticket 03 needs roughly 30 minutes: start it only if the core is stable early, or use it as a separate round. The backend guard is a small stretch, not a reason to abandon a usable frontend midway.

When the plan slips, reduce scope consciously. Keep the current working slice runnable and explain what remains. A simple document card with clear review controls can be a complete user interaction; adding drag and drop does not make that interaction more valuable.

## Pair effectively with AI

Use a driver/navigator arrangement and rotate every **15–20 minutes** or after a natural task boundary. The driver operates the editor and AI. The navigator tracks the rules, challenges assumptions and tries the flow. Share the intended AI request before sending it, and review the output together.

Assign file ownership if you divide implementation. Agree prop/event/API contracts first, and integrate early enough to test the full flow. Avoid two people or agents rewriting the same component at once. Both partners should understand the code that controls validation, saved callbacks and conflicts.

Electric Mind's own [AI Cook-off](https://www.electricmind.com/whats-on-our-mind/ai-cook-off-how-electric-mind-is-rewiring-teamwork-with-generative-ai) discusses rotating drivers and smaller chunks. Its [bootcamp reflections](https://www.electricmind.com/whats-on-our-mind/why-ai-bootcamps-actually-work) emphasize clear context and human-led requirements. Apply those habits while keeping prompts bounded to this rehearsal.

## Scoped AI prompts

These prompts help you rehearse; they do not include solved exercise code.

**Read the contract:**

> Read the draft and application types, wizard host, API client and Ticket 01. Summarize how step validation connects to navigation and where conditional fields belong. Identify ambiguities before editing. Do not implement or change tests yet.

**Design one interaction:**

> We have 35 minutes for Ticket 02. Propose a simple document checklist that shows required kinds, completion and keyboard-operable review controls. Use existing visual conventions. Explain one choice about rejection comments and one failure state. Do not add drag and drop, uploads or libraries.

**Implement a bounded ticket:**

> Implement only Ticket 01's validation and conditional fields in the agreed files. Use the exact synthetic rules in CHALLENGES.md and the supplied error contract. Preserve input when navigating backward. Explain assumptions and list the browser behaviors my partner and I should verify.

**Review the change:**

> Review this diff against Ticket 02. Focus on missing required records, incorrect progress, duplicate requests, version handling and emitting the confirmed saved application. For each concrete issue, describe its trigger and user impact. Do not rewrite unrelated files.

**Reason about persistence:**

> Read the supplied autosave interface and Ticket 03. Describe the states when edits occur during a save, selection changes or a 409 conflict occurs. Propose an observable manual check for each. Do not implement until we agree which states fit our remaining time.

**Verify coverage:**

> Suggest five high-value checks for our implemented onboarding journey, including boundaries, conditional requirements and one failed API request. Distinguish supplied automated coverage from behavior we must inspect in the UI. Do not weaken acceptance tests to match the implementation.

## What deserves your attention

For the wizard, inspect both sides of each condition. A joint applicant needs a joint name; an individual should be able to proceed without one. Non-salary funding needs source details; salary does not. Horizon values of 1 and 50 are valid; a fractional year is not. Going Back must retain work, and review must catch invalid changes to earlier steps.

For the document board, progress must reflect required kinds rather than total records. Received is different from verified; an absent requirement is still incomplete. After saving, use the returned application and its current version. A useful rejection explains the correction needed, with the comment retained if saving fails.

For autosave, a visible Saved state must correspond to the draft actually sent. A later local edit is not already saved merely because an older request succeeded. Changing applicants should not let an old response replace the current applicant's state. A conflict needs an explicit recovery choice.

Use meaningful labels, associated errors, visible focus and readable status text. A color or percentage alone does not explain which item needs action.

## Verify before the demo

Run `npm test` and `npm run build`; use `npm run test:practice` for the intentional exercise checks. Then walk the relevant browser journey with your partner. Test at least one invalid input, one conditional switch, a valid save and a failure. Keep both local servers running.

If you attempt submission, confirm that the supplied host saves the current draft first and then submits its saved version. The optional autosave hook serves draft persistence during editing. Server-side submission readiness remains the explicit backend stretch until implemented, so describe the boundary accurately.

For a conflict test, use two tabs on the same application: save a change in one, then attempt an update using the stale version in the other. Demonstrate that the interface explains the newer state rather than silently overwriting it.

## A concise demonstration

Adapt this to what you actually completed:

> We focused on preparing an application without unnecessary questions or ambiguous review status. This applicant's account and funding choices reveal the relevant fields and required documents. Here is a validation error and how it helps the user correct their input. Here is a received document being reviewed, with progress changing only after the server confirms the save. We checked [specific behaviors]. We chose [one tradeoff] to keep the workflow clear within the timebox. Our next improvement would be [one concrete step and its user benefit].

If a feature remains unfinished, name the remaining acceptance criterion and the next step. Explain which code AI helped draft and how you checked it. Do not claim that a test passed or a rule is enforced at the server when you only verified the interface.

## Reflect and repeat

After each round, discuss one thing that helped collaboration and one habit to change. Did both partners shape the design? Were prompts small enough to inspect? Did you notice a conditional edge case early? Could you explain the saved data and version without consulting the prompt history?

The wealth domain is context for the exercise. KYC means “know your client”; the applicant, consent and document rules are fictional requirements. Ask for domain context plainly when needed. Practicing good product judgment, reliable interactions and clear explanation is the purpose of this round.
