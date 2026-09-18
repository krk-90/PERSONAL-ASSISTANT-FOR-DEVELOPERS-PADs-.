"""Approval-aware MCP server for PADs Git and GitHub operations."""

from mcp.server.fastmcp import FastMCP

from dev_tools import (approve_git_operation, execute_approved_git_operation, github_read, request_git_operation, run_git_read)

mcp = FastMCP("pads-developer-tools")


@mcp.tool()
def git_status() -> str:
    """Return the current workspace branch and changed files."""
    return run_git_read("status")


@mcp.tool()
def git_log() -> str:
    """Return the latest eight workspace commits."""
    return run_git_read("log")


@mcp.tool()
def git_diff_stat() -> str:
    """Return a summary of unstaged workspace changes."""
    return run_git_read("diff")


@mcp.tool()
def request_git_pull(remote: str = "origin", branch: str = "") -> str:
    """Request approval before pulling a validated remote branch into the workspace."""
    return request_git_operation("pull", remote, branch)


@mcp.tool()
def request_git_push(remote: str = "origin", branch: str = "") -> str:
    """Request approval before pushing a validated local branch to a remote."""
    return request_git_operation("push", remote, branch)


@mcp.tool()
def approve_git_request(approval_id: str) -> str:
    """Approve one unexpired Git pull or push request by its exact ID."""
    return approve_git_operation(approval_id)


@mcp.tool()
def execute_approved_git_request(approval_id: str) -> str:
    """Execute one approved Git request exactly once."""
    return execute_approved_git_operation(approval_id)


@mcp.tool()
def github_repository(repository: str) -> str:
    """Read public or authenticated metadata for owner/name."""
    return github_read(repository, "repository")


@mcp.tool()
def github_open_issues(repository: str) -> str:
    """List up to ten open issues for owner/name."""
    return github_read(repository, "issues")


@mcp.tool()
def github_open_pull_requests(repository: str) -> str:
    """List up to ten open pull requests for owner/name."""
    return github_read(repository, "pulls")


if __name__ == "__main__":
    mcp.run()
