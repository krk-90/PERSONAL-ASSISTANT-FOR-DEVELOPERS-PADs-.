import flet as ft
from llm_call import call

def main(page: ft.Page):
    page.title = "PADs | Code Assistant"
    page.window.width = 1100
    page.window.height = 760
    page.bgcolor = "#10131a"
    page.padding = 0
    page.theme = ft.Theme(color_scheme_seed="#7dd3fc")

    conversations = [
    {
        "title": "Welcome to PADs",
        "time": "Just now",
        "messages": []
    }
]

    current_chat = 0
    chat_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=18)
    history_list = ft.Column(spacing=4, expand=True, scroll=ft.ScrollMode.AUTO)

    def message_bubble(label, message, is_user):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(label, size=12, weight=ft.FontWeight.BOLD, color="#a7f3d0" if is_user else "#7dd3fc"),
                    ft.Text(message, size=15, color="#e5e7eb", selectable=True),
                ],
                spacing=6,
            ),
            bgcolor="#12332d" if is_user else "#17202d",
            border=ft.Border.all(1, "#263142"),
            border_radius=12,
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        )

    current_chat = 0

    def load_chat(index):
        nonlocal current_chat

        current_chat = index

        chat_area.controls.clear()

        if len(conversations[index]["messages"]) == 0:
            chat_area.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Welcome to PADs",
                                size=26,
                                weight=ft.FontWeight.BOLD,
                                color="#f8fafc",
                            ),
                            ft.Text(
                                "Your focused coding partner.",
                                size=15,
                                color="#94a3b8",
                            ),
                        ]
                    )
                )
            )
        else:
            for msg in conversations[index]["messages"]:
                chat_area.controls.append(
                    message_bubble(
                        msg["label"],
                        msg["content"],
                        msg["is_user"]
                    )
                )

        page.update()

    def render_history():
        history_list.controls.clear()
        for i, item in enumerate(conversations):

            history_list.controls.append(
                ft.TextButton(
                    content=ft.Text(
                        item["title"],
                        color="#d1d5db"
                    ),
                    on_click=lambda e, idx=i: load_chat(idx)
                )
            )

    def new_chat(e=None):
        nonlocal current_chat

        conversations.insert(
            0,
            {
                "title": "New Chat",
                "time": "Just now",
                "messages": []
            }
        )

        current_chat = 0

        chat_area.controls.clear()

        chat_area.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Welcome to PADs",
                            size=26,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "Your focused coding partner."
                        )
                    ]
                )
            )
        )

        render_history()
        page.update()

    def send_message(e=None):
        nonlocal current_chat

        message = (message_input.value or "").strip()

        if not message:
            return

        if conversations[current_chat]["title"] == "New Chat":
            conversations[current_chat]["title"] = message[:32]

        try:
            response = call(message)

            if hasattr(response, "content"):
                response = response.content

            response = str(response)

        except Exception as err:
            response = f"Error: {err}"

        # Save user message
        conversations[current_chat]["messages"].append(
            {
                "label": "YOU",
                "content": message,
                "is_user": True
            }
        )

        # Save AI message
        conversations[current_chat]["messages"].append(
            {
                "label": "PADS",
                "content": response,
                "is_user": False
            }
        )

        # Show messages
        chat_area.controls.append(
            message_bubble("YOU", message, True)
        )

        chat_area.controls.append(
            message_bubble("PADS", response, False)
        )

        message_input.value = ""

        render_history()
        page.update()

    def toggle_drawer(e):
        drawer.visible = not drawer.visible
        page.update()

    message_input = ft.TextField(
        hint_text="Ask PADs about your code...",
        expand=True,
        min_lines=1,
        max_lines=5,
        color="#e5e7eb",
        hint_style=ft.TextStyle(color="#6b7280"),
        border_color="#263142",
        focused_border_color="#7dd3fc",
        bgcolor="#161b24",
        border_radius=12,
        content_padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        on_submit=send_message,
    )
    drawer = ft.Container(
        width=280,
        bgcolor="#151a23",
        padding=ft.Padding(left=16, right=16, top=18, bottom=16),
        content=ft.Column(
            [
                ft.Row([
                    ft.Text("CONVERSATIONS", size=12, weight=ft.FontWeight.BOLD, color="#7dd3fc"),
                    ft.Container(expand=True),
                    ft.IconButton(ft.Icons.CLOSE, tooltip="Close menu", icon_color="#94a3b8", on_click=toggle_drawer),
                ]),
                ft.Button("＋  New conversation", on_click=new_chat, style=ft.ButtonStyle(bgcolor="#1e293b", color="#e0f2fe", padding=ft.Padding(left=12, right=12, top=12, bottom=12))),
                ft.Divider(color="#263142"),
                history_list,
                ft.Divider(color="#263142"),
                ft.Text("LOCAL SESSION", size=11, color="#687589"),
                ft.Text("History is kept in this session", size=12, color="#8491a5"),
            ],
            spacing=12,
        ),
    )
    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(ft.Icons.MENU, tooltip="Open conversation history", icon_color="#d1d5db", on_click=toggle_drawer),
                ft.Text("PADs", size=20, weight=ft.FontWeight.BOLD, color="#f8fafc"),
                ft.Text("/ code assistant", size=14, color="#687589"),
                ft.Container(expand=True),
                ft.Icon(ft.Icons.CIRCLE, size=10, color="#86efac"),
                ft.Text("Ready", size=12, color="#94a3b8"),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        border=ft.Border(bottom=ft.BorderSide(1, "#202938")),
        padding=ft.Padding(left=18, right=22, top=12, bottom=12),
    )
    input_area = ft.Container(
        content=ft.Row(
            [
                message_input,
                ft.IconButton(ft.Icons.ARROW_UPWARD, tooltip="Send message", icon_color="#0f172a", bgcolor="#7dd3fc", on_click=send_message),
            ],
            spacing=10,
        ),
        padding=ft.Padding(left=24, right=24, top=12, bottom=18),
    )

    render_history()
    new_chat()
    page.add(ft.Row([drawer, ft.Column([header, chat_area, input_area], expand=True, spacing=0)], expand=True, spacing=0))


if __name__ == "__main__":
    ft.run(main)
