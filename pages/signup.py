from nicegui import ui
from nicegui.events import UploadEventArguments
import base64
import requests
import asyncio
from utils.api import base_url  # Assuming base_url is in this file


@ui.page("/signup")
def show_signup_page():
    uploaded_file_data = {}

    # ---------- HEAD HTML ----------
    ui.add_head_html(
        """
    <style>
        .typing-cursor::after { content: '|'; animation: blink 1s step-end infinite; }
        @keyframes blink { from, to { color: transparent; } 50% { color: white; } }

        /* --- Responsive Layout Styles --- */

        /* Mobile view */
        @media (max-width: 768px) {
            .signup-grid {
                display: flex;
                flex-direction: column;
                height: auto;
            }

            .signup-left {
                display: none; /* hide background image section on mobile */
            }

            .signup-right {
                width: 100%;
                padding: 2rem 1rem;
                justify-content: center;
                align-items: center;
            }

            .signup-form {
                width: 100% !important;
            }

            .signup-header img {
                width: 180px !important;
                height: auto !important;
            }

            .signup-header label {
                text-align: center;
            }

            .role-card {
                width: 45% !important;
                height: 100px !important;
            }

            #map {
                height: 250px !important;
            }
        }

        /* Desktop view */
        @media (min-width: 769px) {
            .signup-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .signup-left {
                display: flex;
            }

            .signup-right {
                display: flex;
            }
        }
    </style>
    <script>
        function typeDeleteAnimation(elementId, text) {
            const element = document.getElementById(elementId);
            if (!element) return;
            let i = 0;
            let isDeleting = false;
            const typingSpeed = 150, deletingSpeed = 75, pauseDuration = 2000;
            function animate() {
                const currentSubstring = text.substring(0, i);
                element.textContent = currentSubstring;
                if (isDeleting) { i--; } else { i++; }
                if (!isDeleting && i > text.length) {
                    isDeleting = true;
                    setTimeout(animate, pauseDuration);
                } else if (isDeleting && i < 0) {
                    isDeleting = false;
                    i = 0;
                    setTimeout(animate, 500);
                } else {
                    setTimeout(animate, isDeleting ? deletingSpeed : typingSpeed);
                }
            }
            animate();
        }
        document.addEventListener('DOMContentLoaded', (event) => {
            typeDeleteAnimation('welcome-text', 'Welcome to Medifind');
        });
    </script>
    """
    )

    # ---------- PAGE LAYOUT ----------
    with ui.grid(columns=2).classes("w-full min-h-screen signup-grid"):

        # --- LEFT: Welcome Section ---
        with ui.column().classes(
            "w-full bg-cover bg-no-repeat bg-center relative signup-left"
        ).style("background-image:url(/assets/signup.png)"):
            with ui.column().classes(
                "absolute inset-0 bg-black/60 flex items-center justify-center"
            ):
                with ui.column().classes("text-center items-center max-w-sm"):
                    ui.label().classes(
                        "text-white font-extrabold text-4xl typing-cursor h-12"
                    ).props('id="welcome-text"')
                    ui.label(
                        "Already have an account? Sign in to stay connected."
                    ).classes("text-white text-lg")
                    ui.element("div").classes("h-8")
                    ui.button(
                        "SIGN IN", on_click=lambda: ui.navigate.to("/signin")
                    ).classes("bg-blue text-white font-semibold px-8 py-2 rounded-full")

        # --- RIGHT: Form Section ---
        with ui.column().classes(
            "w-full flex items-center justify-start pt-20 bg-white signup-right"
        ):
            with ui.column().classes("w-[500px] px-8 signup-form"):

                # --- HEADER ---
                with ui.column().classes("w-full items-center mb-8 signup-header"):
                    ui.label("MEDIFIND").classes("text-5xl font-bold text-blue").style(
                        "letter-spacing: 0.1em"
                    )
                    ui.image("assets/signuplog.png").classes(
                        "items-center w-[250px] h-[100px] mt-0 "
                    )
                    ui.label(
                        "...because the right care shouldn't be hard to find"
                    ).classes("text-sm text-gray-500 mt-1 tracking-wide")

                ui.label("Create Account").classes(
                    "text-2xl font-bold mt-4 mb-2 text-gray-800"
                )
                ui.label("Choose your role:").classes(
                    "text-md font-semibold text-gray-600 mb-4"
                )

                # --- ROLE SELECTION ---
                with ui.row().classes("w-full justify-start gap-4 mb-6"):
                    user_button = ui.card().classes(
                        "w-32 h-24 flex flex-col items-center justify-center cursor-pointer border-2 border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-lg role-card"
                    )
                    with user_button:
                        user_icon = ui.icon("person_outline").classes("text-gray-500")
                        user_label = ui.label("User").classes(
                            "text-gray-500 font-semibold"
                        )

                    pharmacy_button = ui.card().classes(
                        "w-32 h-24 flex flex-col items-center justify-center cursor-pointer border-2 border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-lg role-card"
                    )
                    with pharmacy_button:
                        pharmacy_icon = ui.icon("medical_services").classes(
                            "text-gray-500"
                        )
                        pharmacy_label = ui.label("Pharmacy").classes(
                            "text-gray-500 font-semibold"
                        )

                # --- FORMS CONTAINER ---
                with ui.column().classes("w-full relative h-[500px]"):

                    # USER FORM
                    with ui.column().classes(
                        "w-full absolute top-0 left-0 overflow-y-auto h-full pr-2"
                    ) as user_form:
                        user_form.visible = False
                        ui.label("YOUR FULL NAME").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        user_username = (
                            ui.input(placeholder="Enter your name")
                            .props("outlined")
                            .classes("w-full mb-4")
                        )
                        ui.label("YOUR EMAIL").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        user_email = (
                            ui.input(placeholder="Enter email")
                            .props("outlined")
                            .classes("w-full mb-4")
                        )
                        ui.label("PHONE NUMBER").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        user_phone = (
                            ui.input(placeholder="Enter phone number")
                            .props("outlined")
                            .classes("w-full mb-4")
                        )
                        ui.label("PASSWORD").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        user_password = (
                            ui.input(placeholder="Enter password", password=True)
                            .props("outlined")
                            .classes("w-full mb-4")
                        )
                        ui.label("CONFIRM PASSWORD").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        user_confirm_password = (
                            ui.input(placeholder="Confirm password", password=True)
                            .props("outlined")
                            .classes("w-full mb-8")
                        )
                        ui.button(
                            "Sign Up as User", on_click=lambda: handle_signup("user")
                        ).classes(
                            "w-full text-white font-semibold py-2 rounded-full"
                        ).props(
                            "color=teal-600"
                        )

                    # PHARMACY FORM
                    with ui.column().classes(
                        "w-full absolute top-0 left-0 overflow-y-auto h-full pr-2"
                    ) as pharmacy_form:
                        pharmacy_form.visible = False
                        ui.label("PHARMACY NAME").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        pharma_username = (
                            ui.input(placeholder="Enter pharmacy name")
                            .props("outlined")
                            .classes("w-full mb-4")
                        )
                        ui.label("PHARMACY EMAIL").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        pharma_email = (
                            ui.input(placeholder="Enter email")
                            .props("outlined")
                            .classes("w-full mb-4")
                        )
                        ui.label("PHONE NUMBER").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        pharma_phone = (
                            ui.input(placeholder="Enter phone number")
                            .props("outlined")
                            .classes("w-full mb-4")
                        )
                        ui.label("LICENSE NUMBER").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        pharma_license = (
                            ui.input(placeholder="License number")
                            .props("outlined")
                            .classes("w-full mb-4")
                        )
                        ui.label("GPS ADDRESS").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        pharma_address = (
                            ui.input(placeholder="Digital address")
                            .props("outlined")
                            .classes("w-full mb-4")
                        )

                        # --- 🗺️ MAP INTEGRATION ---
                        ui.label("Select Pharmacy Location on Map").classes(
                            "text-sm font-semibold text-gray-700 mb-2"
                        )

                        pharma_latitude = (
                            ui.input(label="Latitude")
                            .props("outlined readonly id=lat_input")
                            .classes("w-full mb-2")
                        )
                        pharma_longitude = (
                            ui.input(label="Longitude")
                            .props("outlined readonly id=lon_input")
                            .classes("w-full mb-4")
                        )

                        # <-- START: NEW PYTHON FUNCTION
                        # This function will be called from JavaScript
                        async def handle_map_update(e):
                            try:
                                lat = e.args['lat']
                                lon = e.args['lon']
                                
                                # Manually set the value on the Python side
                                pharma_latitude.set_value(lat)
                                pharma_longitude.set_value(lon)
                                
                                # Also update the visual input fields for the user
                                await ui.run_javascript(f"""
                                    document.querySelector('#lat_input input').value = '{lat}';
                                    document.querySelector('#lon_input input').value = '{lon}';
                                """)
                                print(f"Python received coords: {lat}, {lon}")
                            except Exception as ex:
                                print(f"Error in handle_map_update: {ex}")

                        # Create an event listener
                        ui.on('map_update', handle_map_update)
                        # <-- END: NEW PYTHON FUNCTION

                        ui.element("div").classes(
                            "w-full h-[300px] rounded-lg mb-4 border border-gray-200"
                        ).props('id="map"')

                        # <-- START: NEW SCRIPT BLOCK
                        ui.add_head_html(
                            """
                            <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
                            <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
                            <script>
                                var map;
                                var marker;

                                // This function now sends an event to Python
                                function updateAndNotifyPython(lat, lon) {
                                    console.log(`Sending coords to Python: ${lat}, ${lon}`);
                                    
                                    // This is the new, reliable way
                                    // It emits an event that the 'ui.on('map_update', ...)' listener in Python will catch.
                                    emitEvent('map_update', { lat: lat, lon: lon });
                                }

                                function initPharmacyMap() {
                                    console.log("initPharmacyMap() called.");
                                    
                                    if (!document.getElementById('map')) {
                                        console.log("Map element not found, retrying in 100ms.");
                                        setTimeout(initPharmacyMap, 100);
                                        return;
                                    }
                                    
                                    if (map) {
                                        console.log("Map already initialized, invalidating size.");
                                        map.invalidateSize();
                                        return;
                                    }

                                    console.log("Initializing Leaflet map...");
                                    map = L.map('map').setView([5.6037, -0.1870], 7); // Ghana default
                                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                                        maxZoom: 19,
                                        attribution: '© OpenStreetMap contributors'
                                    }).addTo(map);
                                    console.log("Map initialized.");

                                    // --- Geolocation ---
                                    if (navigator.geolocation) {
                                        console.log("Requesting geolocation...");
                                        navigator.geolocation.getCurrentPosition(function(pos) {
                                            var lat = pos.coords.latitude.toFixed(6);
                                            var lon = pos.coords.longitude.toFixed(6);
                                            console.log(`Geolocation successful: ${lat}, ${lon}`);
                                            map.setView([lat, lon], 14);
                                            marker = L.marker([lat, lon]).addTo(map)
                                                .bindPopup("Your current location").openPopup();
                                            updateAndNotifyPython(lat, lon); // Call the new function
                                        }, function(err) {
                                            console.warn('Geolocation error: ' + err.message);
                                        });
                                    } else {
                                        console.log("Geolocation not supported by this browser.");
                                    }

                                    // --- Map Click ---
                                    map.on('click', function(e) {
                                        var lat = e.latlng.lat.toFixed(6);
                                        var lon = e.latlng.lng.toFixed(6);
                                        console.log(`Map clicked: ${lat}, ${lon}`);
                                        if (marker) map.removeLayer(marker);
                                        marker = L.marker([lat, lon]).addTo(map)
                                            .bindPopup(`Selected: ${lat}, ${lon}`).openPopup();
                                        updateAndNotifyPython(lat, lon); // Call the new function
                                    });
                                }
                            </script>
                            """
                        )
                        # <-- END: NEW SCRIPT BLOCK

                        # Flyer upload
                        ui.label("PHARMACY IMAGE (Flyer)").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        image_preview = ui.image().classes(
                            "w-32 h-32 object-cover rounded-lg my-2"
                        )
                        image_preview.visible = False

                        async def handle_upload(e: UploadEventArguments):
                            try:
                                file = e.file
                                if not file:
                                    ui.notify("No file uploaded.", color="negative")
                                    return
                                content = await file.read()
                                uploaded_file_data.clear()
                                uploaded_file_data.update(
                                    {
                                        "name": getattr(file, "name", "flyer"),
                                        "content": content,
                                        "type": getattr(
                                            file,
                                            "content_type",
                                            "application/octet-stream",
                                        ),
                                    }
                                )
                                data_url = f"data:{uploaded_file_data['type']};base64,{base64.b64encode(content).decode('utf-8')}"
                                image_preview.set_source(data_url)
                                image_preview.visible = True
                                ui.notify(f"Uploaded {uploaded_file_data['name']}")
                            except Exception as ex:
                                ui.notify(f"Upload error: {ex}", color="negative")

                        ui.upload(
                            on_upload=handle_upload,
                            auto_upload=True,
                            max_files=1,
                            label="Upload Picture",
                        ).classes("w-full mb-4").props("color=teal-600")

                        ui.label("PASSWORD").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        pharma_password = (
                            ui.input(password=True, placeholder="Enter password")
                            .props("outlined")
                            .classes("w-full mb-4")
                        )
                        ui.label("CONFIRM PASSWORD").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        pharma_confirm_password = (
                            ui.input(password=True, placeholder="Confirm password")
                            .props("outlined")
                            .classes("w-full mb-8")
                        )

                        ui.button(
                            "Sign Up as Pharmacy",
                            on_click=lambda: handle_signup("pharmacy"),
                        ).classes(
                            "w-full text-white font-semibold py-2 rounded-full"
                        ).props(
                            "color=teal-600"
                        )

                # ---------- HANDLERS ----------
                def send_request_sync(url, data, files):
                    try:
                        return requests.post(url, data=data, files=files)
                    except requests.RequestException as e:
                        return e

                async def handle_signup(role: str):
                    endpoint_url = f"{base_url}/users/register"
                    payload_data, files = {}, {}

                    if role == "user":
                        # <-- SYNTAX ERROR FIXED HERE
                        if user_password.value != user_confirm_password.value:
                            ui.notify("Passwords do not match!", color="negative")
                            return
                        payload_data = {
                            "username": user_username.value,
                            "email": user_email.value,
                            "phone": user_phone.value,
                            "password": user_password.value,
                            "role": "patient",
                        }
                    else:  # pharmacy
                        if pharma_password.value != pharma_confirm_password.value:
                            ui.notify("Passwords do not match!", color="negative")
                            return
                        if "content" not in uploaded_file_data:
                            ui.notify("Please upload a flyer.", color="negative")
                            return

                        # This validation will now work correctly
                        if not pharma_latitude.value or not pharma_longitude.value:
                            ui.notify("Please select a location on the map.", color="negative")
                            return

                        payload_data = {
                            "username": pharma_username.value,
                            "email": pharma_email.value,
                            "phone": pharma_phone.value,
                            "password": pharma_password.value,
                            "license_number": pharma_license.value,
                            "digital_address": pharma_address.value,
                            "role": "pharmacy",
                            "latitude": pharma_latitude.value,
                            "longitude": pharma_longitude.value,
                        }
                        files["flyer"] = (
                            uploaded_file_data["name"],
                            uploaded_file_data["content"],
                            uploaded_file_data["type"],
                        )

                    ui.notify("Submitting form...", spinner=True)
                    response = await asyncio.to_thread(
                        send_request_sync, endpoint_url, payload_data, files
                    )
                    if isinstance(response, requests.Response):
                        if response.status_code in [200, 201]:
                            ui.notify("Registration successful!", color="positive")
                            ui.navigate.to("/signin")
                        else:
                            try:
                                ui.notify(
                                    f"Error: {response.json().get('detail', 'Unknown error')}",
                                    color="negative",
                                )
                            except:
                                ui.notify(f"Error: {response.text}", color="negative")
                    else:
                        ui.notify(f"Server error: {response}", color="negative")

                # ---------- ROLE SELECTION ----------
                state = {"selected_role": None}

                def select_role(role):
                    if state["selected_role"] == role:
                        user_form.visible = pharmacy_form.visible = False
                        state["selected_role"] = None
                        return

                    state["selected_role"] = role
                    user_form.visible = role == "user"
                    pharmacy_form.visible = role == "pharmacy"

                    if role == "pharmacy":
                        ui.run_javascript("initPharmacyMap()")

                user_button.on("click", lambda: select_role("user"))
                pharmacy_button.on("click", lambda: select_role("pharmacy"))
