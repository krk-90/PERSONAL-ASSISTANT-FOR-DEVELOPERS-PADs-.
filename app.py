
import flet as ft


def main(page: ft.Page):
    page.title = "PERSONAL ASSISTANT (PA)"
    page.window.width = 1000
    page.window.height = 700
    page.bgcolor = "#9bd177"

    # Chat area
    chat_area = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    # Message input
    message_input = ft.TextField(
    hint_text="Type your message...",
    expand=True,
    color="black",
    border_color="blue",
    height=50,
    border_radius=25,
    content_padding=ft.Padding(
        left=20,
        right=20,
        top=10,
        bottom=10,
    ),
)

    # Send message function
    def send_message(e):
        message = message_input.value.strip()

        if message == "":
            return

        # Display user message
        chat_area.controls.append(
            ft.Text(
                f"You: {message}",
                color="black",
                size=18,
            )
        )

        # Temporary assistant response
        chat_area.controls.append(
            ft.Text(
                "Assistant: I received your message!",
                color="blue",
                size=18,
            )
        )

        # Clear input
        message_input.value = ""

        page.update()

    # Send button
    send_button = ft.Button(
        "Send",
        on_click=send_message,
        height=40,
        
    )

    # Header
    header = ft.Text(
        "PERSONAL ASSISTANT (PA)",
        size=28,
        weight=ft.FontWeight.BOLD,
        color="black",
    )

    # Input area
    input_area = ft.Container(
        content=ft.Row(
            controls=[
                message_input,
                send_button,
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(
            left=30,
            right=30,
            top=10,
            bottom=10,
        ),
    )

    # Main layout
    page.add(
        ft.Column(
            controls=[
                header,
                ft.Divider(),
                chat_area,
                ft.Divider(),
                input_area,
            ],
            expand=True,
            spacing=10,
        )
    )


if __name__ == "__main__":
    ft.run(main)