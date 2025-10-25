from nicegui import ui, app
import requests
import asyncio
from components.navbar import show_navbar  # Assuming you have this
from utils.api import base_url


@ui.page("/pharmacy/{pharmacy_id}")
def show_pharmacy_page(pharmacy_id: str):
    show_navbar()  # Make sure this component exists and is imported

    ui.add_head_html(
        """
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

        <style>
        /* ============================
           RESPONSIVE MAP & HEADER
           ============================ */
        /*
         * Note: The NiceGUI/Quasar/Tailwind default is flex.
         * We primarily use the custom CSS to override this for mobile view
         * when flex-direction: column is needed, and to explicitly hide the map.
        */
        
        /* Mobile View: <= 768px */
        @media (max-width: 768px) {
            #map-display {
                display: none !important; /* Hide map completely on mobile view */
            }

            /* Apply to the main header row for stacking */
            .pharmacy-header-row {
                flex-direction: column !important;
                align-items: flex-start !important;
                gap: 10px !important;
            }

            /* Buttons side-by-side on mobile */
            .pharmacy-buttons {
                display: flex !important;
                flex-direction: row !important;
                justify-content: space-between !important;
                width: 100% !important; /* Force full width on mobile */
                gap: 10px !important;
                margin-top: 10px !important;
            }

            .pharmacy-buttons button {
                flex: 1 !important; /* Distribute space equally */
                font-size: 0.9rem !important;
            }
            
            /* Pharmacy Name visibility and size on mobile */
            .pharmacy-name-label {
                width: 100%;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                font-size: 1.8rem !important; /* Reduced size for mobile */
                font-weight: 700 !important;
            }
        }

        /* Desktop View: >= 769px (Explicitly setting row layout for clarity) */
        @media (min-width: 769px) {
            #map-display {
                display: block !important;
                height: 200px !important;
            }

            .pharmacy-header-row {
                flex-direction: row !important;
                justify-content: space-between !important;
                align-items: flex-start !important;
            }

            .pharmacy-buttons {
                display: flex !important;
                flex-direction: column !important; /* Stack buttons vertically on desktop */
                gap: 0.5rem !important;
            }
            
            .pharmacy-name-label {
                font-size: 2.5rem !important;
                font-weight: bold !important;
                white-space: nowrap;
            }
        }
        </style>
    """
    )

    # --- Store uploaded prescription file info ---
    uploaded_prescription_info = {"name": None, "content": None, "type": None}

    # --- Dialogs (3. and 4. Backend Logic are defined later) ---

    # 1. SIMPLIFIED Message Dialog (No Upload)
    # ... (Dialog definition is kept as is) ...
    with ui.dialog().classes("text-black") as message_dialog, ui.card().classes(
        "min-w-[500px] p-6"
    ):
        ui.label("Send a Message").classes("text-xl font-bold text-gray-800 mb-4")
        subject_input = ui.input("Subject").props("outlined").classes("w-full mb-4")
        message_textarea = (
            ui.textarea("Your Message").props("outlined rows=4").classes("w-full mb-4")
        )

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=message_dialog.close).props("flat color=grey")
            # Calls the simplified send_message function
            ui.button(
                "Send",
                on_click=lambda: send_message(
                    pharmacy_id, subject_input, message_textarea, message_dialog
                ),
            ).classes("bg-sky-600 text-white")

    # 2. SEPARATE Prescription Upload Dialog
    # ... (Dialog definition is kept as is) ...
    with ui.dialog().classes("text-black") as upload_dialog, ui.card().classes(
        "min-w-[500px] p-6"
    ):
        ui.label("Upload Prescription").classes("text-xl font-bold text-gray-800 mb-4")

        prescription_title_input = (
            ui.input("Title").props("outlined").classes("w-full mb-4")
        )
        prescription_notes_input = (
            ui.textarea("Notes (Optional)")
            .props("outlined rows=3")
            .classes("w-full mb-4")
        )

        async def handle_upload_select(e):
            if e.content:
                uploaded_prescription_info["name"] = e.name
                uploaded_prescription_info["content"] = e.content.read()
                uploaded_prescription_info["type"] = e.type
                ui.notify(f"Selected: {e.name}", color="positive")
            else:  # Handle deselection/cancel
                uploaded_prescription_info.clear()
                uploaded_prescription_info.update(
                    {"name": None, "content": None, "type": None}
                )
                ui.notify("Upload cancelled.", color="warning")

        upload_element = ui.upload(
            on_upload=handle_upload_select,
            label="Click or drag file (Image/PDF, max 5MB)",
            auto_upload=True,
            max_files=1,
            max_file_size=5_000_000,
        ).props(f"flat dense accept={'.jpg,.jpeg,.png,.pdf'}")

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button(
                "Cancel",
                on_click=lambda: (
                    upload_dialog.close(),
                    uploaded_prescription_info.clear(),
                    uploaded_prescription_info.update(
                        {"name": None, "content": None, "type": None}
                    ),
                    upload_element.clear(),
                ),
            ).props("flat color=grey")
            # Calls the upload_prescription function
            ui.button(
                "Upload",
                on_click=lambda: upload_prescription(
                    prescription_title_input,
                    prescription_notes_input,
                    uploaded_prescription_info,
                    upload_dialog,
                    upload_element,
                ),
            ).classes(
                "bg-green-600 text-white"
            )  # Green color for upload action

    # 3. SIMPLIFIED Backend Logic for Sending Message (No Prescription)
    async def send_message(p_id: str, subject_field, message_field, dialog):
        token = app.storage.user.get("access_token")
        if not token:
            ui.notify("You must be logged in.", color="negative")
            return

        subject = subject_field.value
        message = message_field.value

        if not subject or not message:
            ui.notify("Subject and message cannot be empty.", color="negative")
            return

        send_message_url = f"{base_url}/messages/send"
        message_payload = {
            "pharmacy_id": p_id,
            "subject": subject,
            "message": message,
        }
        headers_form_encoded = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        ui.notify("Sending message...", spinner=True, color="info")
        try:
            send_response = await asyncio.to_thread(
                requests.post,
                send_message_url,
                data=message_payload,
                headers=headers_form_encoded,
                timeout=20,
            )
            if send_response.status_code == 200:
                ui.notify("Message sent successfully!", color="positive")
                subject_field.set_value(None)
                message_field.set_value(None)
                dialog.close()
            else:
                error = "Failed."
                try:
                    error = send_response.json().get("detail", send_response.text)
                except:
                    error = send_response.text
                ui.notify(
                    f"Failed ({send_response.status_code}): {error}",
                    color="negative",
                    multi_line=True,
                )
        except requests.RequestException as e:
            ui.notify(f"Connection error: {e}", color="negative")

    # 4. SEPARATE Backend Logic for Uploading Prescription
    async def upload_prescription(
        title_field, notes_field, file_info, dialog, uploader
    ):
        token = app.storage.user.get("access_token")
        if not token:
            ui.notify("You must be logged in.", color="negative")
            return

        title = title_field.value
        notes = notes_field.value

        if not title:
            ui.notify("Title is required.", color="negative")
            return
        if not file_info.get("name") or not file_info.get("content"):
            ui.notify("Please select a file to upload.", color="negative")
            return

        ui.notify("Uploading prescription...", spinner=True, color="info")
        upload_url = f"{base_url}/prescriptions/upload"
        headers_auth_only = {"Authorization": f"Bearer {token}"}
        files_payload = {
            "file": (file_info["name"], file_info["content"], file_info["type"])
        }
        data_payload = {"title": title, "notes": notes or ""}

        try:
            upload_response = await asyncio.to_thread(
                requests.post,
                upload_url,
                headers=headers_auth_only,
                files=files_payload,
                data=data_payload,
                timeout=30,
            )

            if upload_response.status_code == 200:
                ui.notify("Prescription uploaded successfully!", color="positive")
                title_field.set_value(None)
                notes_field.set_value(None)
                file_info.clear()
                file_info.update({"name": None, "content": None, "type": None})
                uploader.clear()
                dialog.close()
            else:
                error_detail = "Upload failed."
                try:
                    error_detail = upload_response.json().get(
                        "detail", upload_response.text
                    )
                except:
                    error_detail = upload_response.text
                ui.notify(
                    f"Upload failed ({upload_response.status_code}): {error_detail}",
                    color="negative",
                    multi_line=True,
                )

        except requests.RequestException as e:
            ui.notify(f"Connection error: {e}", color="negative", multi_line=True)

    # Main container
    with ui.column().classes("w-full bg-gray-50 min-h-screen"):
        # Header
        with ui.column().classes("w-full bg-[#00a7b1] text-white p-8 shadow-md"):
            # Apply the custom class to the main row for responsive layout control
            with ui.row(wrap=False).classes(
                "w-full max-w-7xl mx-auto items-start justify-between gap-8 pharmacy-header-row"
            ):
                # Left Side (Name, Address, Buttons)
                with ui.column().classes("gap-1"):
                    ui.button(
                        "Back to All Pharmacies",
                        on_click=lambda: ui.navigate.to("/"),
                        icon="arrow_back",
                    ).props("flat round text-color=white")

                    # Apply custom class for responsive text handling
                    pharmacy_name_label = ui.label("Loading Pharmacy...").classes(
                        "text-4xl md:text-5xl font-bold pharmacy-name-label"
                    )
                    pharmacy_address_label = ui.label("Loading address...").classes(
                        "text-lg opacity-80"
                    )

                    # Wrap buttons in a row with the custom class for mobile/desktop control
                    with ui.row().classes("pharmacy-buttons"):
                        ui.button(
                            "Contact Pharmacy",
                            icon="mail",
                            on_click=message_dialog.open,
                        ).style(
                            "padding: 0.5rem 1.5rem; "
                            "border-radius: 0.5rem; "
                            "background-color: white !important; "
                            "color: #00a7b1 !important; "
                            "font-weight: bold !important; "
                            "text-transform: none !important;"
                            "box-shadow: none !important;"
                            "z-index: 10;"
                        )

                        ui.button(
                            "Upload Prescription",
                            icon="upload_file",
                            on_click=upload_dialog.open,
                        ).style(
                            "padding: 0.5rem 1.5rem; "
                            "border-radius: 0.5rem; "
                            "background-color: white !important; "
                            "color: #00a7b1 !important; "
                            "font-weight: bold !important; "
                            "text-transform: none !important;"
                            "box-shadow: none !important;"
                            "z-index: 10;"
                        )

                # Right Side (Map)
                with ui.column().classes("w-full md:w-1/3 min-w-[300px]"):
                    ui.label("Location").classes(
                        "text-xl font-semibold opacity-90 mb-2"
                    )
                    # This element contains the Leaflet map and has the ID #map-display
                    map_container = (
                        ui.element("div")
                        .props('id="map-display"')
                        .style(
                            "width: 100%; height: 200px; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);"
                        )
                    )

        # Main Content Area
        with ui.column().classes("w-full max-w-7xl mx-auto p-4 md:p-8 items-center"):
            ui.separator().classes("w-full mb-8")
            ui.label("Available Medicines").classes(
                "text-3xl font-bold text-gray-800 mb-4"
            )
            search_field = (
                ui.input(placeholder="Search for a medicine in this pharmacy...")
                .props("outlined rounded dense clearable")
                .classes("w-full max-w-xl bg-white mb-8")
            )
            # This grid is already responsive via Tailwind classes
            medicines_grid = ui.grid().classes(
                "w-full justify-items-center grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
            )

    def handle_search():
        search_term = search_field.value.lower()
        if medicines_grid:
            # Need to use list(medicines_grid) because children collection can change
            for card in list(medicines_grid.default_slot.children):
                if hasattr(card, "medicine_name"):
                    medicine_name = getattr(card, "medicine_name", "").lower()
                    card.set_visibility(search_term in medicine_name)

    search_field.on("change", handle_search)

    # --- Data Fetching Logic (Kept as is) ---
    async def fetch_pharmacy_data():
        pharmacy_name = "Pharmacy Details"
        # --- Fetch Pharmacy Details ---
        try:
            pharmacy_url = f"{base_url}/public/pharmacies/{pharmacy_id}"
            response = await asyncio.to_thread(requests.get, pharmacy_url, timeout=10)

            if response.status_code == 200:
                response_data = response.json()
                data = response_data.get("data", {})

                pharmacy_name = data.get("pharmacy_name", "Pharmacy Details")
                pharmacy_address = data.get("digital_address")
                gps_location = data.get("gps_location")

                pharmacy_name_label.set_text(pharmacy_name)
                pharmacy_address_label.set_text(
                    pharmacy_address or "No address provided."
                )

                lat, lon = None, None
                if gps_location and isinstance(gps_location, dict):
                    lat = gps_location.get("lat")
                    lon = gps_location.get("lon")

                if lat is not None and lon is not None:
                    ui.run_javascript(
                        f'''
                        try {{
                            const containerId = 'map-display';
                            const container = L.DomUtil.get(containerId);
                            let map = window.leafletMapInstance;

                            if (container && !map) {{
                                map = L.map(containerId).setView([{lat}, {lon}], 15);
                                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                                }}).addTo(map);
                                L.marker([{lat}, {lon}]).addTo(map).bindPopup('{pharmacy_name.replace("'", "\\'")}').openPopup();
                                window.leafletMapInstance = map;
                            }} else if (map) {{
                                map.setView([{lat}, {lon}], 15);
                                map.eachLayer(function (layer) {{
                                    if (layer instanceof L.Marker) {{
                                        map.removeLayer(layer);
                                    }}
                                }});
                                L.marker([{lat}, {lon}]).addTo(map).bindPopup('{pharmacy_name.replace("'", "\\'")}').openPopup();
                            }}
                        }} catch (e) {{ console.error('Error initializing/updating Leaflet map:', e); }}
                    '''
                    )
                else:
                    map_container.clear()
                    with map_container:
                        with ui.element("div").classes(
                            "w-full h-full bg-gray-200 flex items-center justify-center rounded-xl"
                        ):
                            ui.label("Map data not available").classes("text-gray-500")
            else:
                pharmacy_name_label.set_text(
                    f"Pharmacy Not Found ({response.status_code})"
                )

        except requests.RequestException:
            pharmacy_name_label.set_text("Connection Error")

        # --- Fetch Medicines/Ads ---
        medicines_url = f"{base_url}/public/pharmacies/{pharmacy_id}/ads"
        try:
            response = await asyncio.to_thread(requests.get, medicines_url, timeout=20)
            try:
                # Clear all children from the grid
                for child in list(medicines_grid.default_slot.children):
                    child.delete()
            except RuntimeError as e:
                print(f"Ignoring grid clear for disconnected client: {e}")
                return

            with medicines_grid:
                if response.status_code == 200:
                    response_data = response.json()
                    medicines_list = response_data.get("data", [])

                    if not medicines_list:
                        ui.label("No medicines/ads found for this pharmacy.").classes(
                            "col-span-full"
                        )
                        return

                    for med in medicines_list:
                        with ui.card().classes(
                            "w-full shadow-md hover:shadow-lg transition cursor-pointer"
                        ) as card:
                            # Attach data for search filtering
                            card.medicine_name = med.get("medicine_name", "")
                            image_path = med.get("flyer")
                            title = med.get("medicine_name", "Medicine")
                            description = med.get("description", "No description")

                            if image_path and image_path.startswith("http"):
                                image_source = image_path
                            else:
                                image_source = "/assets/landing_home11.jpg"

                            ui.image(image_source).classes(
                                "w-full h-40 object-cover"
                            ).props("loading=lazy")
                            with ui.card_section():
                                ui.label(title).classes("font-bold")
                                ui.label(description).classes(
                                    "text-sm text-gray-600 truncate"
                                )  # Added truncate
                else:
                    ui.label(
                        f"Could not load medicines/ads ({response.status_code})."
                    ).classes("col-span-full text-red-500")
        except requests.RequestException as e:
            try:
                # Clear all children from the grid
                for child in list(medicines_grid.default_slot.children):
                    child.delete()
                with medicines_grid:
                    ui.label(f"Connection error fetching medicines/ads: {e}").classes(
                        "col-span-full text-red-500"
                    )
            except RuntimeError as re:
                print(f"Ignoring grid clear for disconnected client: {re}")

    ui.timer(0.1, fetch_pharmacy_data, once=True)
