"""Small, read-only developer tool adapters used by the PADs MVP."""

import json
import os
import re
import subprocess
import time
import uuid
import urllib.error
import urllib.request
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
APPROVAL_FILE = WORKSPACE / ".pads_git_approvals.json"


def web_fetch(url: str) -> str:
    """Fetch a small public page with a strict timeout and response limit."""
    if not re.fullmatch(r"https?://[^\s]+", url) or not url.lower().startswith(("https://", "http://")):
        raise ValueError("Only http and https URLs are allowed")
    request = urllib.request.Request(url, headers={"User-Agent": "PADs-local-assistant"})
    with urllib.request.urlopen(request, timeout=10) as response:
        content_type = response.headers.get("Content-Type", "")
        if "text" not in content_type and "json" not in content_type:
            raise ValueError("URL did not return text content")
        body = response.read(120_000).decode("utf-8", errors="replace")
    return f"Fetched {url}\n\n{body}"


def run_git_read(operation: str) -> str:
    """Run one of the fixed, read-only Git operations in the workspace."""
    commands = {
        "status": ["git", "status", "--short", "--branch"],
        "log": ["git", "log", "-8", "--oneline", "--decorate"],
        "diff": ["git", "diff", "--stat"],
        "remote": ["git", "remote", "-v"],
    }
    if operation not in commands:
        raise ValueError("Unsupported Git operation")
    result = subprocess.run(commands[operation], cwd=WORKSPACE, capture_output=True, text=True, timeout=10, check=False)
    output = (result.stdout or result.stderr).strip()
    return output or "No output."


def _current_branch() -> str:
    result = subprocess.run(["git", "branch", "--show-current"], cwd=WORKSPACE, capture_output=True, text=True, timeout=10, check=False)
    branch = result.stdout.strip()
    if not branch or not re.fullmatch(r"[A-Za-z0-9._/-]+", branch):
        raise ValueError("A named Git branch is required")
    return branch


def request_git_operation(operation: str, remote: str = "origin", branch: str = "") -> str:
    """Create a short-lived approval request for one fixed Git mutation."""
    if operation not in ("pull", "push"):
        raise ValueError("Only pull and push approval requests are supported")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", remote):
        raise ValueError("Invalid Git remote")
    branch = branch or _current_branch()
    if not re.fullmatch(r"[A-Za-z0-9._/-]+", branch):
        raise ValueError("Invalid Git branch")
    approvals = _read_approvals()
    approval_id = uuid.uuid4().hex
    approvals[approval_id] = {"operation": operation, "remote": remote, "branch": branch, "state": "pending", "created_at": time.time()}
    _write_approvals(approvals)
    return f"Approval required: {approval_id}\nProposed command: git {operation} {remote} {branch}\nExpires in 10 minutes."


def approve_git_operation(approval_id: str) -> str:
    approvals = _read_approvals()
    request = approvals.get(approval_id)
    if not request or time.time() - request["created_at"] > 600:
        raise ValueError("Approval not found or expired")
    if request["state"] != "pending":
        raise ValueError(f"Approval is already {request['state']}")
    request["state"] = "approved"
    request["approved_at"] = time.time()
    _write_approvals(approvals)
    return f"Approved {request['operation']} for {request['remote']}/{request['branch']}. Execute with the approval ID."


def execute_approved_git_operation(approval_id: str) -> str:
    approvals = _read_approvals()
    request = approvals.get(approval_id)
    if not request or time.time() - request["created_at"] > 600:
        raise ValueError("Approval not found or expired")
    if request["state"] != "approved":
        raise PermissionError("Git operation requires an approved request")
    command = ["git", request["operation"], request["remote"], request["branch"]]
    result = subprocess.run(command, cwd=WORKSPACE, capture_output=True, text=True, timeout=120, check=False)
    request["state"] = "executed" if result.returncode == 0 else "failed"
    request["result"] = (result.stdout or result.stderr).strip()[-4000:]
    _write_approvals(approvals)
    return request["result"] or f"git {request['operation']} completed."


def _read_approvals() -> dict:
    try:
        return json.loads(APPROVAL_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write_approvals(approvals: dict) -> None:
    APPROVAL_FILE.write_text(json.dumps(approvals, indent=2), encoding="utf-8")


def repository_from_remote() -> str:
    remote = run_git_read("remote")
    match = re.search(r"github\.com[:/]([^/\s]+/[^/\s]+?)(?:\.git)?(?:\s|$)", remote)
    return match.group(1) if match else ""


def github_read(repository: str, resource: str) -> str:
    """Read an allowlisted GitHub resource; never performs mutations."""
    repository = repository.strip().strip("/")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Repository must look like owner/name")
    paths = {
        "repository": f"/repos/{repository}",
        "issues": f"/repos/{repository}/issues?state=open&per_page=10",
        "pulls": f"/repos/{repository}/pulls?state=open&per_page=10",
    }
    if resource not in paths:
        raise ValueError("Unsupported GitHub resource")
    request = urllib.request.Request(
        "https://api.github.com" + paths[resource],
        headers={"Accept": "application/vnd.github+json", "User-Agent": "PADs-local-assistant"},
    )
    token = os.getenv("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code == 401:
            raise RuntimeError("GitHub rejected GITHUB_TOKEN") from error
        if error.code == 403:
            raise RuntimeError("GitHub rate limit or permission denied") from error
        raise RuntimeError(f"GitHub returned HTTP {error.code}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"GitHub request failed: {error.reason}") from error

    if resource == "repository":
        return f"{payload['full_name']}\n{payload.get('description') or 'No description'}\nStars: {payload['stargazers_count']} | Open issues: {payload['open_issues_count']}\nDefault branch: {payload['default_branch']}"
    return "\n".join(f"#{item['number']} {item['title']} ({item['html_url']})" for item in payload) or "None found."
