from nicegui import ui, app
import asyncio
import requests
from components.navbar import show_navbar  # Assuming this exists
from utils.api import base_url


@ui.page("/sent_messages")  # Define the URL for this page
def user_sent_messages_page():
    show_navbar()  # Make sure navbar works for regular users too

    # --- Optional: Dialog to show full message details ---
    with ui.dialog() as message_detail_dialog, ui.card().classes("min-w-[500px]"):
        detail_recipient = ui.label().classes("font-bold text-lg")
        detail_subject = ui.label().classes("text-gray-700 mb-2")
        ui.separator()
        detail_message = ui.markdown().classes("mt-2")
        with ui.row().classes("w-full justify-end mt-4"):
            ui.button("Close", on_click=message_detail_dialog.close).props(
                "flat color=grey"
            )

    # --- Page Content ---
    with ui.column().classes("w-full max-w-7xl mx-auto p-8 items-start"):
        ui.label("Sent Messages").classes("text-3xl font-bold text-sky-700 mb-6")

        # Container for the sent messages
        sent_messages_container = ui.column().classes("w-full gap-4")

    # --- Optional: Function to open the detail dialog ---
    def show_message_details(msg_data: dict):
        # Populate the dialog content
        # --- NOTE: We need to know the key for the pharmacy's name/ID ---
        recipient_name = msg_data.get(
            "pharmacy_name", msg_data.get("pharmacy_id", "Unknown Pharmacy")
        )
        detail_recipient.set_text(f"To: {recipient_name}")
        detail_subject.set_text(f"Subject: {msg_data.get('subject', 'No Subject')}")
        detail_message.set_content(f"**Message:**\n\n{msg_data.get('message', '')}")
        message_detail_dialog.open()

    # --- Logic to Fetch Sent Messages ---
    async def fetch_sent_messages():
        print("DEBUG: fetch_sent_messages started.")  # <<< DEBUG PRINT
        token = app.storage.user.get("access_token")
        if not token:
            print("DEBUG: No access token found.")  # <<< DEBUG PRINT
            ui.notify("Authentication error. Please log in.", color="negative")
            ui.navigate.to("/signin")
            return

        print(f"DEBUG: Token found: {token[:10]}...")  # <<< DEBUG PRINT
        headers = {"Authorization": f"Bearer {token}"}
        # Use the correct endpoint for sent messages
        sent_messages_url = f"{base_url}/messages/sent"
        print(f"DEBUG: Calling API: {sent_messages_url}")  # <<< DEBUG PRINT

        try:
            response = await asyncio.to_thread(
                requests.get, sent_messages_url, headers=headers, timeout=20
            )
            print(
                f"DEBUG: API response status: {response.status_code}"
            )  # <<< DEBUG PRINT

            try:
                sent_messages_container.clear()
            except RuntimeError as e:
                print(f"Ignoring UI update for disconnected client: {e}")
                return

            if response.status_code == 200:
                messages_data = response.json()
                print(f"DEBUG: API response data: {messages_data}")  # <<< DEBUG PRINT

                # --- Get the list from the 'sent_messages' key ---
                message_list = []
                if isinstance(messages_data, dict) and "sent_messages" in messages_data:
                    message_list = messages_data.get("sent_messages", [])
                elif isinstance(
                    messages_data, list
                ):  # Keep this as a fallback just in case
                    message_list = messages_data
                # ---

                if not message_list:
                    with sent_messages_container:
                        ui.label("You haven't sent any messages yet.").classes(
                            "text-gray-500"
                        )
                    return

                # --- Display each sent message ---
                with sent_messages_container:
                    for msg in message_list:
                        if not isinstance(msg, dict):
                            print(
                                f"Warning: Unexpected item in sent message list: {msg}"
                            )
                            continue

                        # Make card clickable to show details
                        sent_card = ui.card().classes(
                            "w-full shadow-md cursor-pointer hover:shadow-lg transition bg-white"
                        )
                        with sent_card:
                            with ui.card_section():
                                # --- NOTE: Uses pharmacy_name based on your log ---
                                recipient = msg.get(
                                    "pharmacy_name",
                                    msg.get("pharmacy_id", "Unknown Pharmacy"),
                                )
                                ui.label(f"To: {recipient}").classes(
                                    "font-bold text-lg"
                                )

                                subject = msg.get("subject", "No Subject")
                                ui.label(f"Subject: {subject}").classes("text-gray-700")

                            # Message Preview
                            message_preview = msg.get("message", "")
                            if len(message_preview) > 100:
                                message_preview = message_preview[:100] + "..."

                            with ui.card_section().classes("pt-0"):
                                ui.label(message_preview).classes(
                                    "text-sm text-gray-600"
                                )

                        # Add click handler
                        sent_card.on("click", lambda m=msg: show_message_details(m))

            else:
                print(
                    f"ERROR: API returned status {response.status_code}. Response text: {response.text}"
                )  # <<< DEBUG PRINT
                with sent_messages_container:
                    ui.label(
                        f"Error loading sent messages ({response.status_code})."
                    ).classes("text-red-500")

        except requests.RequestException as e:
            print(f"ERROR: Connection error during fetch: {e}")  # <<< DEBUG PRINT
            try:
                with sent_messages_container:
                    ui.label(f"Connection error: {e}").classes("text-red-500")
            except RuntimeError as re:
                print(f"Ignoring UI update for disconnected client: {re}")

    # Load the messages when the page opens
    ui.timer(0.1, fetch_sent_messages, once=True)
