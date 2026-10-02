# Small local onboarding API

Python 3.11+ and its standard library are the only requirements. From the project
folder run `python server/server.py`. It listens on `127.0.0.1:4001`; use `--port`
or `API_PORT` to override it. The frontend proxy must use the same port. All
people, records, and document labels are fictional; no document files are stored.

| Route | Contract |
| --- | --- |
| `GET /api/health` | `{status:"ok",mode:"practice"}` |
| `GET /api/applications` | `{applications:[...]}` |
| `PUT /api/applications/:id/draft` | `{draft,expectedVersion}` → `{application}` |
| `PATCH /api/applications/:id/documents/:documentId` | `{status,comment,expectedVersion}` → `{application}` |
| `POST /api/applications/:id/submit` | `{expectedVersion}` → `{application}` |

Draft saves require the full draft object, valid enum values, text fields, an
integer `horizonYears` from 0–100 and boolean `consent`. Blank text is permitted
because drafts can be incomplete. Text is trimmed; storage limits are
`legalName`/`jointApplicantName` 120, `email` 254, and `sourceDetails` 1,000.

Document decisions permit `received` → `verified`/`rejected`, `rejected` →
`received`, and same-status changes. A rejected decision requires a trimmed
comment of 3–500 characters; other comments may be empty and are limited to
500. Document changes take about 100 ms. Requested documents represent samples
still awaiting receipt; document uploading is outside this exercise.

Every write increments the application version and requires its current positive
integer `expectedVersion`. Stale writes return HTTP 409 with
`{error:{code:"VERSION_CONFLICT",message},currentApplication}`. Submitted
applications reject further writes and repeated submission with HTTP 409.
Errors generally use `{error:{code,message}}`. Add `?fail=1` to the application
list endpoint for a repeatable HTTP 503 error, then remove it to recover.

`rules.py` intentionally contains the unfinished `submission_issues` gate.
The optional backend ticket should require legal and joint-applicant names of
2–80 characters (joint name only for joint accounts), a valid basic email of at
most 254 characters, all listed profile choices, an integer horizon of 1–50,
non-salary source details of 10–500 characters, and consent. Require verified
identity and address documents, plus joint-identity for joint accounts and
source-of-funds for non-salary funding. Return readable issues before submission.
Storage validation deliberately permits incomplete drafts; do not replace it
with final-submission validation. The unfinished gate currently permits direct
API submission of incomplete applications.

The service uses a shared lock and persists changes to `server/data/state.json`.
Stop the server and delete only that state file to reset; the next start recreates
four synthetic applications. Keep the data directory ignored in Git.

Run isolated API checks with:

```text
python -m unittest discover -s server -p test_*.py
```
