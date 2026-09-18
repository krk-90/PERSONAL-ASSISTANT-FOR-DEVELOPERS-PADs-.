# PADs

PADs (Personal Assistant for Developers) is a local-first AI developer control room. The current safe-mode MVP includes a chat surface, session task manager, code scratchpad, capability requests, and an explicit approval queue.

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

## MCP Git tools

PADs also includes a read-only MCP server for Git and GitHub operations:

```powershell
python mcp_server.py
```

Configure that command in an MCP client such as VS Code or Claude Desktop. It exposes `git_status`, `git_log`, `git_diff_stat`, `github_repository`, `github_open_issues`, and `github_open_pull_requests`. Pull and push use an approval flow:

1. Call `request_git_pull` or `request_git_push`.
2. Review the returned command and call `approve_git_request` with its ID.
3. Call `execute_approved_git_request` with the same ID.

Requests expire after ten minutes and can execute only once. No commit, merge, delete, or email-send tools are exposed.

The model adapter uses LangChain and works offline with a clear fallback. Set `GROQ_API_KEY` in `.env` to enable Groq responses. The default model is `openai/gpt-oss-20b`; override it with `GROQ_MODEL` if your Groq account uses another model. The GitHub tab supports read-only local Git inspection and public GitHub repository, issue, and pull request queries; set `GITHUB_TOKEN` only when authenticated API access is needed.

The assistant is orchestrated by LangGraph in `agent_graph.py`. A supervisor routes requests to task, Git, GitHub, web, or general specialists. Memory is bounded and local; external writes remain disabled.

External integrations are intentionally not enabled yet. Read [decision_file.md](decision_file.md), [workflow.md](workflow.md), and [code improvement.md](code%20improvement.md) for the security boundary, request lifecycle, and promotion criteria.
