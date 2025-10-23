from nicegui import ui, app
import asyncio
import requests
from components.navbar import show_navbar  # Assuming this exists
from utils.api import base_url


@ui.page("/inbox")
def pharmacy_inbox_page():
    show_navbar()

    # --- 1. Dialog to show full message details ---
    with ui.dialog() as message_detail_dialog, ui.card().classes("min-w-[500px]"):
        detail_sender = ui.label().classes("font-bold text-lg")
        # --- Added Labels for Dialog ---
        detail_username = ui.label().classes("text-sm text-gray-600")
        detail_email = ui.label().classes("text-sm text-gray-600")
        detail_contact = ui.label().classes("text-sm text-gray-600")
        # --- End ---
        detail_subject = ui.label().classes("text-gray-700 mb-2")
        ui.separator()
        detail_message = ui.markdown().classes(
            "mt-2"
        )  # Use markdown for better formatting
        with ui.row().classes("w-full justify-end mt-4"):
            ui.button("Close", on_click=message_detail_dialog.close).props(
                "flat color=grey"
            )

    # --- Page Content ---
    with ui.column().classes("w-full max-w-7xl mx-auto p-8 items-start"):
        ui.label("My Inbox").classes("text-3xl font-bold text-sky-700 mb-6")
        messages_container = ui.column().classes("w-full gap-4")

    # --- 2. Function to mark a message as read ---
    # --- MODIFIED: Accepts subject_label ---
    async def mark_as_read(
        message_id: str, message_card: ui.card, subject_label: ui.label
    ):
        token = app.storage.user.get("access_token")
        if not token:
            return

        headers = {"Authorization": f"Bearer {token}"}
        read_url = f"{base_url}/messages/{message_id}/read"

        try:
            print(f"DEBUG: Marking message {message_id} as read at {read_url}")
            response = await asyncio.to_thread(
                requests.patch, read_url, headers=headers, timeout=10
            )

            if response.status_code == 200:
                ui.notify(f"Message marked as read.", color="positive", timeout=1000)
                # Visually mark as read
                message_card.classes(remove="bg-white", add="bg-gray-100")
                # --- NEW: Remove bold from subject ---
                subject_label.classes(remove="font-bold")
                # --- END ---
            else:
                error = response.text
                try:
                    error = response.json().get("detail", error)
                except:
                    pass
                ui.notify(
                    f"Failed to mark as read ({response.status_code}): {error}",
                    color="negative",
                    multi_line=True,
                )

        except requests.RequestException as e:
            ui.notify(f"Connection error marking as read: {e}", color="negative")

    # --- 3. Function to open the detail dialog ---
    # --- MODIFIED: Accepts subject_label ---
    async def show_message_details(
        msg_data: dict, card_element: ui.card, subject_label: ui.label
    ):
        # Populate the dialog content
        detail_sender.set_text(f"From: {msg_data.get('sender_name', 'Unknown Sender')}")
        detail_username.set_text(f"Username: {msg_data.get('user_name', 'N/A')}")
        detail_email.set_text(f"Email: {msg_data.get('sender_email', 'N/A')}")
        detail_contact.set_text(f"Contact: {msg_data.get('sender_contact', 'N/A')}")
        detail_subject.set_text(f"Subject: {msg_data.get('subject', 'No Subject')}")
        detail_message.set_content(f"**Message:**\n\n{msg_data.get('message', '')}")

        detail_username.set_visibility(bool(msg_data.get("user_name")))
        detail_email.set_visibility(bool(msg_data.get("sender_email")))
        detail_contact.set_visibility(bool(msg_data.get("sender_contact")))

        message_detail_dialog.open()

        # Call the mark as read function
        message_id = msg_data.get("message_id")
        # --- Check if already read before calling API ---
        is_read_before_click = (
            "bg-gray-100" in card_element._classes
        )  # Check current background
        if (
            message_id and not is_read_before_click
        ):  # Only call API if not already marked visually
            await mark_as_read(message_id, card_element, subject_label)
        elif not message_id:
            ui.notify("Could not find message ID to mark as read.", color="warning")
        # If already read, do nothing

    # --- Logic to Fetch Messages ---
    async def fetch_messages():
        token = app.storage.user.get("access_token")
        if not token:
            ui.notify("Authentication error. Please log in.", color="negative")
            ui.navigate.to("/signin")
            return

        headers = {"Authorization": f"Bearer {token}"}
        messages_url = f"{base_url}/messages/inbox"

        try:
            response = await asyncio.to_thread(
                requests.get, messages_url, headers=headers, timeout=20
            )

            # --- Added try/except for clear() ---
            try:
                messages_container.clear()
            except RuntimeError as e:
                print(f"Ignoring UI update for disconnected client: {e}")
                return  # Stop executing, the page is gone
            # --- End ---

            if response.status_code == 200:
                messages_data = response.json()

                message_list = []
                if isinstance(messages_data, dict) and "inbox" in messages_data:
                    message_list = messages_data.get("inbox", [])
                elif isinstance(messages_data, list):
                    message_list = messages_data

                if not message_list:
                    with messages_container:
                        ui.label("You have no messages.").classes("text-gray-500")
                    return

                # --- Display each message ---
                with messages_container:
                    for msg in message_list:
                        if not isinstance(msg, dict):
                            print(f"Warning: Unexpected item in message list: {msg}")
                            continue

                        # --- Check is_read status ---
                        is_read = msg.get("is_read", False)
                        card_bg = "bg-gray-100" if is_read else "bg-white"
                        subject_style = (
                            "font-bold" if not is_read else ""
                        )  # Bold if NOT read
                        # ---

                        message_card = ui.card().classes(
                            f"w-full shadow-md cursor-pointer hover:shadow-lg transition {card_bg}"
                        )
                        with message_card:
                            with ui.card_section():
                                # --- DISPLAY SENDER INFO ---
                                sender_name = msg.get("sender_name", "Unknown Sender")
                                ui.label(f"From: {sender_name}").classes(
                                    "font-bold text-lg"
                                )

                                sender_username = msg.get("user_name")
                                if sender_username:
                                    ui.label(f"Username: {sender_username}").classes(
                                        "text-sm text-gray-600"
                                    )

                                sender_email = msg.get("sender_email")
                                if sender_email:
                                    ui.label(f"Email: {sender_email}").classes(
                                        "text-sm text-gray-600"
                                    )

                                sender_contact = msg.get("sender_contact")
                                if sender_contact:
                                    ui.label(f"Contact: {sender_contact}").classes(
                                        "text-sm text-gray-600"
                                    )
                                # --- END OF SENDER INFO ---

                                subject = msg.get("subject", "No Subject")
                                # --- Store subject label and apply style ---
                                subject_label = ui.label(f"Subject: {subject}").classes(
                                    f"text-gray-700 mt-1 {subject_style}"
                                )

                            ui.separator()

                            # --- Truncate long messages for preview ---
                            message_preview = msg.get("message", "")
                            if len(message_preview) > 100:
                                message_preview = message_preview[:100] + "..."

                            with ui.card_section().classes("pt-0"):
                                ui.label(message_preview).classes(
                                    "text-sm text-gray-600"
                                )

                        # --- MODIFIED: Pass subject_label to click handler ---
                        message_card.on(
                            "click",
                            lambda m=msg, c=message_card, sl=subject_label: show_message_details(
                                m, c, sl
                            ),
                        )

            else:
                with messages_container:
                    ui.label(
                        f"Error loading messages ({response.status_code})."
                    ).classes("text-red-500")

        except requests.RequestException as e:
            try:
                with messages_container:
                    ui.label(f"Connection error: {e}").classes("text-red-500")
            except RuntimeError as re:
                print(f"Ignoring UI update for disconnected client: {re}")

    ui.timer(0.1, fetch_messages, once=True)
