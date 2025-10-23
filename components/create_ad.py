from nicegui import ui, events, app
import asyncio
import requests
from utils.api import base_url  # Assuming base_url is in this file


@ui.page("/create_ad")
def show_create_ad_page():

    uploaded_file_data = {}

    ### --- PAGE PROTECTION --- ###
    if app.storage.user.get("role") != "pharmacy":
        ui.notify(
            "You must be logged in as a pharmacy to create an ad.", color="negative"
        )
        ui.navigate.to("/signin")
        return

    # --- Page Styling ---
    ui.add_head_html(
        """
    <style>
    body {
        margin: 0;
        background:url('/assets/create.jpg') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Poppins', sans-serif;
        color: white;
        overflow: hidden;
    }
    </style>"""
    )

    # --- Main Page Layout ---
    with ui.column().classes("w-full items-center"):
        ui.label("MEDIFIND").classes("text-6xl font-bold text-teal-900").style(
            "letter-spacing: 0.1em; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);"
        )
        ui.label("...because the right care shouldn't be hard to find").classes(
            "text-sm font-normal text-black mt-1 tracking-wide"
        ).style("letter-spacing: 0.1em; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);")

        # --- Form Container ---
        with ui.column().classes(
            "w-full max-w-2xl mx-auto mt-4 p-8 rounded-2xl shadow-2xl bg-white space-y-6 "
            "max-h-[80vh] overflow-y-auto"
        ):
            ui.label("ADD NEW MEDICINE").classes(
                "font-extrabold text-4xl tracking-wide text-center text-teal-900"
            )

            medicine_name_input = (
                ui.input("Medication Name").props("outlined").classes("w-full")
            )
            description_input = (
                ui.textarea("Description").props("outlined").classes("w-full")
            )
            price_input = ui.number("Price").props("outlined").classes("w-full")
            category_select = (
                ui.select(
                    [
                        "ANALGESICS",
                        "ANTIBIOTICS",
                        "ANTI HYPERTENSIVES",
                        "ANTI DIABETICS",
                        "ANTI VIRAL",
                        "ANTI ULCERS",
                    ],
                    label="Category",
                )
                .classes("w-full text-gray-800")
                .props(
                    "outlined dense popup-content-class='bg-white text-black shadow-md rounded-lg'"
                )
            )
            quantity_input = (
                ui.number("Available Stock (Quantity)")
                .props("outlined")
                .classes("w-full")
            )

            upload_container = ui.column().classes("w-full gap-0")

            async def handle_flyer_upload(e: events.UploadEventArguments):
                try:
                    file = e.file
                    if not file:
                        ui.notify("No file was uploaded.", color="negative")
                        return
                    content = await file.read()
                    uploaded_file_data.clear()
                    uploaded_file_data["name"] = getattr(file, "name", "flyer.jpg")
                    uploaded_file_data["content"] = content
                    uploaded_file_data["type"] = getattr(
                        file, "content_type", "image/jpeg"
                    )
                    ui.notify(
                        f"Image '{uploaded_file_data['name']}' ready for submission."
                    )
                except Exception as ex:
                    ui.notify(f"Could not process file: {ex}", color="negative")

            def build_uploader():
                upload_container.clear()
                with upload_container:
                    ui.label("Upload Image (Optional)").classes(
                        "font-medium text-gray-600"
                    )
                    ui.upload(
                        on_upload=handle_flyer_upload, auto_upload=True, max_files=1
                    ).classes(
                        "w-full rounded-lg border border-dashed border-gray-400 p-4"
                    ).props(
                        "color=teal"
                    )

            # --- Submission Logic ---
            def send_request_sync(url, data, files, headers):
                try:
                    return requests.post(
                        url, data=data, files=files, headers=headers, timeout=90
                    )
                except requests.RequestException as e:
                    return e

            async def submit():
                token = app.storage.user.get("access_token")
                if not token:
                    ui.notify(
                        "Your session has expired. Please log in again.",
                        color="negative",
                    )
                    ui.navigate.to("/signin")
                    return

                if not all(
                    [
                        medicine_name_input.value,
                        price_input.value,
                        description_input.value,
                        category_select.value,
                        quantity_input.value,
                    ]
                ):
                    ui.notify("Please fill all required fields.", color="negative")
                    return

                submit_button.disable()

                # ##### THIS IS THE FIX: The payload now exactly matches the backend documentation. #####
                # ##### The unnecessary 'pharmacy_id' has been removed.                         #####
                payload_data = {
                    "medicine_name": medicine_name_input.value,
                    "quantity": int(quantity_input.value),
                    "price": price_input.value,
                    "description": description_input.value,
                    "category": category_select.value,
                }

                files = {}
                if "content" in uploaded_file_data:
                    files["flyer"] = (
                        uploaded_file_data["name"],
                        uploaded_file_data["content"],
                        uploaded_file_data["type"],
                    )

                headers = {"Authorization": f"Bearer {token}"}
                endpoint_url = f"{base_url}/inventory/add"

                ui.notify("Submitting...", spinner=True)
                response = await asyncio.to_thread(
                    send_request_sync, endpoint_url, payload_data, files, headers
                )

                if isinstance(response, requests.Response) and response.status_code in [
                    200,
                    201,
                ]:
                    ui.notify(
                        f"Medicine '{medicine_name_input.value}' added successfully!",
                        color="positive",
                    )
                    # Clear form for next entry
                    medicine_name_input.value = ""
                    description_input.value = ""
                    price_input.value = None
                    category_select.value = None
                    quantity_input.value = None
                    uploaded_file_data.clear()
                    build_uploader()
                else:
                    try:
                        error_detail = response.json().get(
                            "detail", "An unknown error occurred."
                        )
                    except:
                        error_detail = (
                            response.text
                            if hasattr(response, "text")
                            else str(response)
                        )
                    ui.notify(
                        f"Submission failed: {error_detail}",
                        color="negative",
                        multi_line=True,
                    )

                submit_button.enable()

            # --- Action Buttons ---
            with ui.row().classes("w-full gap-4"):
                submit_button = ui.button("Add Medicine", on_click=submit).classes(
                    "flex-grow bg-teal-600 hover:bg-teal-700 text-white font-semibold py-3 rounded-xl"
                )
                ui.button(
                    "Cancel",
                    on_click=lambda: ui.navigate.to("/pharmacydashboard"),
                    color="red",
                ).classes("flex-grow py-3 rounded-xl")

            build_uploader()
