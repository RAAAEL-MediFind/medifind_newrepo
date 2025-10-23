from nicegui import ui, app
import requests
import asyncio  # <-- Added
from components.navbar import show_navbar
from components.footer import show_footer
from components.sidebar import show_sidebar
from utils.api import base_url  # <-- Added


@ui.page("/userdashboard")
def user_dashboard():
    """User Dashboard Page for MediFind"""

    # --- Security Guard ---
    if not app.storage.user.get("authenticated"):
        ui.navigate.to("/signin")
        return

    show_navbar()
    show_sidebar()

    # --- State variable to hold all fetched pharmacies ---
    all_pharmacies_data = []

    with ui.column().classes(
        "mt-24 px-8 gap-8 max-w-7xl mx-auto w-full"
    ):  # Changed max-width and added w-full

        # --- Personalized Welcome Message ---
        user_name = app.storage.user.get("name", "Medifinder")
        with ui.row().classes("justify-between items-center w-full"):
            ui.label(f"Welcome, {user_name}!").classes(
                "text-2xl font-bold text-sky-700"
            )
            # Logout button would typically be in the navbar or sidebar

        # --- Pharmacy Search Section ---
        ui.label("Find Pharmacies").classes(
            "text-3xl font-bold text-gray-800 mt-6 mb-4"
        )

        # --- Styled Search Bar ---
        with ui.row().classes(
            "w-full max-w-2xl justify-center mb-6 px-4"
        ):  # Increased max-width
            search_input = (
                ui.input(placeholder="Search by pharmacy name or location...")
                .props("outlined rounded clearable dense bg-color=white")
                .classes("flex-grow")
                .style("border-radius: 9999px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);")
            )
            search_input.add_slot("prepend")
            with search_input:
                ui.icon("search", color="grey-6").classes("ml-2")

        # --- Grid for Pharmacy Cards ---
        pharmacies_grid = ui.grid().classes(
            "w-full justify-center gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 px-4"  # Adjusted grid cols
        )

        # --- Function to update pharmacy display based on search ---
        def update_pharmacy_display():
            search_term = search_input.value.lower().strip()
            print(
                f"DEBUG: Updating pharmacy display. Search: '{search_term}'. Total fetched: {len(all_pharmacies_data)}"
            )  # Debug
            try:
                pharmacies_grid.clear()
            except RuntimeError as e:
                print(f"Ignoring grid clear for disconnected client: {e}")
                return

            found_pharmacies = False
            with pharmacies_grid:
                if not all_pharmacies_data:
                    ui.label("Loading pharmacies or none available.").classes(
                        "col-span-full text-center text-gray-500 mt-4"
                    )
                    return

                for i, pharmacy in enumerate(all_pharmacies_data):
                    if not isinstance(pharmacy, dict):
                        print(f"Warning: Skipping invalid pharmacy data at index {i}")
                        continue

                    # --- Extract data (Adjust keys based on your API response) ---
                    # IMPORTANT: Check your API response for the correct ID key!
                    pharmacy_id = pharmacy.get(
                        "pharmacy_id", pharmacy.get("id", pharmacy.get("_id"))
                    )
                    name = pharmacy.get("pharmacy_name", "Unknown Pharmacy")
                    address = pharmacy.get("digital_address", "No address")
                    # image_url = pharmacy.get("image_url") # Add if your API sends an image
                    # ---

                    name_lower = name.lower()
                    address_lower = address.lower()

                    if search_term in name_lower or search_term in address_lower:
                        found_pharmacies = True
                        print(f"DEBUG: Displaying pharmacy {i}: {name}")  # Debug

                        if not pharmacy_id:
                            print(
                                f"Warning: Pharmacy '{name}' is missing an ID, cannot make it clickable."
                            )
                            # Display non-clickable card if ID is missing
                            with ui.card().classes("w-full shadow-md rounded-lg p-4"):
                                ui.label(name).classes("font-bold text-lg text-sky-700")
                                ui.label(address).classes("text-sm text-gray-600")
                                # Add image if available: ui.image(image_url)...
                        else:
                            # --- Clickable Card ---
                            with ui.card().classes(
                                "w-full shadow-md rounded-lg p-4 cursor-pointer hover:shadow-lg transition"
                            ).on(
                                "click",
                                lambda p_id=pharmacy_id: ui.navigate.to(
                                    f"/pharmacy/{p_id}"
                                ),
                            ):
                                ui.label(name).classes("font-bold text-lg text-sky-700")
                                ui.label(address).classes("text-sm text-gray-600")
                                # Add image if available

                if not found_pharmacies and search_term:
                    ui.label(
                        f"No pharmacies found matching '{search_input.value}'"
                    ).classes("col-span-full text-center text-gray-500 mt-4")
                elif (
                    not found_pharmacies and not all_pharmacies_data
                ):  # Should be handled above
                    pass
                elif not found_pharmacies and all_pharmacies_data:
                    ui.label(f"No pharmacies match '{search_input.value}'.").classes(
                        "col-span-full text-center text-gray-500 mt-4"
                    )

        # Connect search input to the update function
        search_input.on("change", update_pharmacy_display)

        # --- Function to fetch all pharmacies ---
        async def fetch_all_pharmacies():
            nonlocal all_pharmacies_data
            endpoint_url = f"{base_url}/public/pharmacies/all"
            print(f"DEBUG: Calling API: {endpoint_url}")
            try:
                # Show loading state
                with pharmacies_grid:
                    try:
                        pharmacies_grid.clear()
                    except RuntimeError:
                        return
                    with ui.column().classes("col-span-full items-center mt-8"):
                        ui.spinner(size="lg")
                        ui.label("Loading pharmacies...").classes("text-gray-500")

                response = await asyncio.to_thread(
                    requests.get, endpoint_url, timeout=30
                )
                print(f"DEBUG: API response status: {response.status_code}")

                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        print(
                            f"DEBUG: API response data (first 500 chars): {str(response_data)[:500]}..."
                        )

                        # --- Adjust data extraction based on actual API response ---
                        if isinstance(response_data, dict) and "data" in response_data:
                            all_pharmacies_data = response_data.get("data", [])
                        elif isinstance(response_data, list):
                            all_pharmacies_data = response_data
                        else:
                            all_pharmacies_data = []
                            print(
                                "DEBUG: API response is not a list or dict with 'data' key."
                            )
                            ui.notify(
                                "Received unexpected data format from API.",
                                color="negative",
                            )
                        # ---

                        if not isinstance(all_pharmacies_data, list):
                            print(
                                f"DEBUG: Final all_pharmacies_data is not a list! Type: {type(all_pharmacies_data)}"
                            )
                            all_pharmacies_data = []
                            ui.notify("Data processing error.", color="negative")
                        else:
                            print(
                                f"DEBUG: Stored {len(all_pharmacies_data)} pharmacies."
                            )

                    except requests.exceptions.JSONDecodeError:
                        print("ERROR: Failed to decode API response as JSON.")
                        all_pharmacies_data = []
                        ui.notify("Error reading data from server.", color="negative")
                else:
                    print(
                        f"ERROR: API returned non-200 status. Response text: {response.text}"
                    )
                    all_pharmacies_data = []
                    ui.notify(
                        f"Error fetching pharmacies: Status {response.status_code}",
                        color="negative",
                    )

            except requests.RequestException as e:
                print(f"ERROR: Connection error: {e}")
                all_pharmacies_data = []
                ui.notify(f"Connection Error: {e}", color="negative")
                try:
                    pharmacies_grid.clear()  # Clear spinner on error
                    with pharmacies_grid:
                        ui.label(
                            "Connection Error. Could not load pharmacies."
                        ).classes("col-span-full text-center text-red-500 mt-4")
                except RuntimeError:
                    return  # Client left

            finally:
                # Call update_display AFTER data is fetched (or fetch failed)
                update_pharmacy_display()

        # Fetch pharmacies when the page loads
        ui.timer(0.1, fetch_all_pharmacies, once=True)

    show_footer()
