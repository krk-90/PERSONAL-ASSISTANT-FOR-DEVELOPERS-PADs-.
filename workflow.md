# PADs Workflow

## Request lifecycle

1. Parse the user's request into an intent and proposed tool call.
2. Classify the operation as read, write, network, external communication, or destructive.
3. Check identity, capability scope, workspace boundary, and input validation.
4. For low-risk reads, execute with a timeout and return evidence.
5. For every write or external action, show the exact target, inputs, expected effect, and rollback/limit.
6. Wait for explicit approval. Approval must bind to the exact operation and expire.
7. Execute through a narrow adapter with least-privilege credentials.
8. Record requested, approved, executed, denied, failed, and cancelled events without secrets.
9. Return the result and any follow-up action; never claim success without tool evidence.

## LangGraph agent levels

- **Supervisor:** classifies intent and selects exactly one specialist.
- **Specialists:** tasks, read-only Git, read-only GitHub, constrained web fetch, or general LangChain response.
- **Memory:** recent graph checkpoints are held per thread and task notes persist in a bounded local `.pads_memory.json` file.
- **Guardrail:** no graph node exposes commit, push, merge, delete, email-send, or arbitrary shell execution.

## Capability adapters

- **Tasks:** local CRUD first; persistence and reminders are later milestones.
- **Code editor:** scratchpad and diff preview first; workspace writes require approval.
- **Git/GitHub:** read-only workspace status/log/diff and GitHub repository/issues/PRs are available. Pull and push require an expiring request, explicit approval, and one-time execution; commits and merges remain disabled.
- **Email:** draft only by default; sending requires exact-recipient preview and confirmation.
- **Web search/crawler:** URL allowlist, robots policy, size limits, timeouts, and prompt-injection isolation.

## Failure handling

Fail closed on missing credentials, ambiguous targets, expired approval, network errors, policy violations, or unexpected tool output. Preserve the failure event and provide a human-readable next step.
