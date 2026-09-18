# Code Improvement Plan

## Evaluation: current MVP

| Area | Status | Evidence / gap |
| --- | --- | --- |
| Assistant chat | Pass | Flet UI calls the model adapter; offline fallback is explicit. |
| Task manager | Pass | In-memory add and completion state work in the current session. |
| Code editor | Partial | Scratchpad exists; no file picker, diff engine, or approved write path. |
| Git/GitHub | Partial | Read operations are implemented; pull/push now have approval-bound execution, while commit and merge remain disabled. |
| Email drafting | Partial | Capability request exists; no draft store or provider adapter. |
| Web search/crawler | Partial | Capability request exists; no URL policy or fetch adapter. |
| Authentication | Fail | No user identity or login. |
| Authorization | Partial | UI approval state exists; enforcement is not yet server-side. |
| Auditability | Partial | Approval state is session-only; no durable redacted event log. |

## Threshold result

**Keep improving.** The app is useful as a safe-mode prototype, but it does not meet the production threshold in `decision_file.md` because authentication, real authorization enforcement, durable audit logs, and tested integrations are absent.

## Next increments

1. Extract `ApprovalGate` and `Capability` into a tested core module.
2. Add durable local storage with schema versioning and redaction.
3. Add OS-backed authentication and a session timeout.
4. Implement workspace-scoped read-only Git adapter.
5. Add diff preview plus atomic, approved file writes.
6. Add sandboxed GitHub, email, and web adapters with timeouts and allowlists.
7. Add unit, integration, and security tests for denial and replay cases.

## Quality gate

Re-evaluate after each increment. Finalize only when every production threshold passes and no critical/high security findings remain. Do not broaden permissions merely to make a demo appear complete.
