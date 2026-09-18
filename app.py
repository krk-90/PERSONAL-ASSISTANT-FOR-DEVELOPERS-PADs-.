import flet as ft
from agent_graph import run_agent
from dev_tools import github_read, repository_from_remote, run_git_read

CAPABILITIES = {
    "Git / GitHub": "Read status, branches, issues and pull requests",
    "Email drafting": "Prepare a draft only; never send automatically",
    "Web search / crawler": "Fetch and summarize an approved URL",
    "Code changes": "Propose a patch; never write without approval",
}


def main(page: ft.Page):
    page.title = "PADs | Personal Assistant for Developers"
    page.window.width, page.window.height = 1180, 780
    page.bgcolor, page.padding = "#0d1117", 0
    page.theme = ft.Theme(color_scheme_seed="#67e8f9")
    tasks, approvals, messages = [], [], []

    def text_card(title, body, color="#cbd5e1"):
        return ft.Container(ft.Column([ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color="#67e8f9"), ft.Text(body, size=14, color=color, selectable=True)], spacing=6), bgcolor="#151c26", border=ft.Border.all(1, "#273244"), border_radius=8, padding=14)

    input_border = ft.OutlineInputBorder(side=ft.BorderSide(color="#273244"))
    task_input = ft.TextField(label="Task", expand=True, bgcolor="#151c26", border=input_border)
    code_editor = ft.TextField(label="Scratchpad", multiline=True, min_lines=14, max_lines=20, expand=True, value="# PADs code scratchpad\n", border=input_border)
    chat_list = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=10)
    approval_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    task_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
    git_output = ft.Text("Run a read-only operation to inspect this workspace.", selectable=True, color="#cbd5e1")
    github_output = ft.Text("Run a GitHub read operation. Public repositories work without a token.", selectable=True, color="#cbd5e1")
    repository_input = ft.TextField(label="GitHub repository (owner/name)", value=repository_from_remote(), bgcolor="#151c26", border=input_border)
    status = ft.Text("Local session | external actions require approval", size=12, color="#94a3b8")

    def refresh_tasks():
        task_list.controls = [ft.Row([ft.Checkbox(label=item["title"], value=item["done"], on_change=lambda e, item=item: item.update(done=e.control.value)), ft.Text(item["priority"], size=11, color="#fbbf24")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN) for item in tasks]

    def add_task(e=None):
        title = (task_input.value or "").strip()
        if title:
            tasks.append({"title": title, "done": False, "priority": "normal"})
            task_input.value = ""
            refresh_tasks()
            page.update()

    def show_git(operation):
        try:
            git_output.value = run_git_read(operation)
        except Exception as error:
            git_output.value = f"Git error: {error}"
        page.update()

    def show_github(resource):
        try:
            github_output.value = github_read(repository_input.value or "", resource)
        except Exception as error:
            github_output.value = f"GitHub error: {error}"
        page.update()

    def render_approvals():
        approval_list.controls = []
        for index, item in enumerate(approvals):
            approval_list.controls.append(text_card(f"{item['state'].upper()} | {item['capability']}", item["details"] + ("\nApproval changes state only; an integration must still execute it." if item["state"] == "approved" else "")))
            if item["state"] == "pending":
                approval_list.controls.append(ft.Row([ft.Button("Approve", on_click=lambda e, index=index: resolve_approval(index, True)), ft.Button("Reject", on_click=lambda e, index=index: resolve_approval(index, False))], spacing=8))

    def resolve_approval(index, approved):
        approvals[index]["state"] = "approved" if approved else "rejected"
        render_approvals()
        page.update()

    def request_approval(capability, details):
        approvals.append({"capability": capability, "details": details, "state": "pending"})
        render_approvals()
        page.update()

    def ask_ai(e=None):
        prompt = (message_input.value or "").strip()
        if not prompt:
            return
        messages.extend([("YOU", prompt), ("PADS", run_agent(prompt))])
        chat_list.controls = [text_card(label, body, "#e2e8f0") for label, body in messages]
        message_input.value = ""
        page.update()

    message_input = ft.TextField(hint_text="Ask PADs to plan, explain, or draft...", expand=True, min_lines=1, max_lines=4, bgcolor="#151c26", border=input_border, on_submit=ask_ai)
    capability_buttons = [ft.Button(name, on_click=lambda e, name=name: request_approval(name, CAPABILITIES[name])) for name in CAPABILITIES]
    tabs = ft.Tabs(
        length=5,
        selected_index=0,
        expand=True,
        content=ft.Column(
            [
                ft.TabBar(tabs=[
                    ft.Tab(label="Assistant"),
                    ft.Tab(label="Tasks"),
                    ft.Tab(label="Code editor"),
                    ft.Tab(label="Approvals"),
                    ft.Tab(label="GitHub"),
                ]),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        ft.Column([chat_list, ft.Row([message_input, ft.IconButton(ft.Icons.ARROW_UPWARD, tooltip="Send", bgcolor="#67e8f9", on_click=ask_ai)])], expand=True, spacing=12),
                        ft.Column([ft.Row([task_input, ft.IconButton(ft.Icons.ADD, tooltip="Add task", on_click=add_task)]), task_list], expand=True),
                        ft.Column([code_editor, ft.Row([ft.Button("Request patch approval", on_click=lambda e: request_approval("Code changes", "Proposed changes from the current scratchpad"))])], expand=True),
                        ft.Column([ft.Text("Risk gate", size=22, weight=ft.FontWeight.BOLD), ft.Text("Review every network, external, or write action before it can run.", color="#94a3b8"), approval_list], expand=True),
                        ft.Column([
                            ft.Text("Read-only developer operations", size=22, weight=ft.FontWeight.BOLD),
                            ft.Text("Git runs inside this workspace. GitHub calls use the public API and never mutate data.", color="#94a3b8"),
                            ft.Row([ft.Button("Git status", on_click=lambda e: show_git("status")), ft.Button("Git log", on_click=lambda e: show_git("log")), ft.Button("Git diff", on_click=lambda e: show_git("diff")), ft.Button("Remote", on_click=lambda e: show_git("remote"))], wrap=True),
                            git_output,
                            ft.Divider(color="#273244"),
                            repository_input,
                            ft.Row([ft.Button("Repository", on_click=lambda e: show_github("repository")), ft.Button("Open issues", on_click=lambda e: show_github("issues")), ft.Button("Open PRs", on_click=lambda e: show_github("pulls"))], wrap=True),
                            github_output,
                        ], expand=True, scroll=ft.ScrollMode.AUTO),
                    ],
                ),
            ],
            expand=True,
        ),
    )
    sidebar = ft.Container(width=250, bgcolor="#111821", padding=18, content=ft.Column([ft.Text("PADS", size=24, weight=ft.FontWeight.BOLD, color="#f8fafc"), ft.Text("Personal Assistant for Developers", color="#94a3b8"), ft.Divider(color="#273244"), ft.Text("CAPABILITIES", size=11, weight=ft.FontWeight.BOLD, color="#67e8f9"), *capability_buttons, ft.Divider(color="#273244"), ft.Text("SECURITY", size=11, weight=ft.FontWeight.BOLD, color="#67e8f9"), ft.Text("Local session\nLeast privilege\nExplicit approvals\nAudit-friendly state", size=13, color="#cbd5e1"), ft.Container(expand=True), status], expand=True))
    page.add(ft.Row([sidebar, ft.Container(expand=True, padding=24, content=ft.Column([ft.Row([ft.Text("Developer control room", size=24, weight=ft.FontWeight.BOLD), ft.Container(expand=True), ft.Text("SAFE MODE", color="#86efac", weight=ft.FontWeight.BOLD)]), tabs], expand=True))], expand=True))


if __name__ == "__main__":
    ft.run(main)
