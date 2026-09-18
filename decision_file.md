# PADs Decision File

## Product decision

Build PADs as a local-first personal developer assistant. The assistant may plan, explain, draft, and manage local session tasks. It must ask for explicit approval before network access, external communication, file writes, commits, pushes, merges, or destructive commands.

## Current decision

The project is at **MVP / safe-mode**, not production-ready. The UI exposes capability requests and records approval state, but approved items do not execute integrations yet. This prevents an approval button from being mistaken for a complete security system.

## Risk policy

- Read-only local inspection: low risk, allowed within a selected workspace.
- Code/file changes: medium risk, show a diff and require approval per operation.
- Web crawling, GitHub, email, and other network operations: high risk, require explicit approval, scoped credentials, timeout, and an audit record.
- Send email, push code, merge PRs, delete data, or run shell commands: critical risk, require a second confirmation with an exact preview.
- Secrets belong in environment variables or an OS credential store, never in chat history or source files.

## Authorization model

Use deny-by-default capability scopes: `tasks:write`, `workspace:read`, `workspace:write`, `git:read`, `github:read`, `github:write`, `email:draft`, `email:send`, and `web:fetch`. A user approval grants one operation with a short expiry, not permanent access.

## Promotion threshold

Do not finalize as production until all of these are true:

1. Authentication and identity ownership are implemented.
2. Every tool validates authorization and scope server-side.
3. Secrets are stored outside source and logs are redacted.
4. High-risk actions have preview, approval, cancellation, timeout, and audit events.
5. Unit tests cover allow, deny, expired approval, replay, and malformed input paths.
6. Integration tests use sandbox GitHub/email/web accounts.
7. A security review finds no unresolved critical or high findings.

Until then, keep improving in safe mode.
