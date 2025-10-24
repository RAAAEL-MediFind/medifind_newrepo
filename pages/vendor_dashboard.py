from nicegui import ui, app
import asyncio
import requests
from components.navbar import show_navbar  # Assuming this exists
from utils.api import base_url  # Make sure base_url is defined
from nicegui.events import UploadEventArguments  # Import for upload handling
import base64  # Import for image preview


sidebar_visible = True


def toggle_sidebar():
    global sidebar_visible
    sidebar_visible = not sidebar_visible
    ui.notify("Sidebar " + ("opened" if sidebar_visible else "closed"))
    ui.run_javascript(
        f"""
        const sidebar = document.querySelector('.nicegui-left-drawer');
        if (sidebar) {{
            sidebar.style.display = '{'block' if sidebar_visible else 'none'}';
        }}
    """
    )


@ui.page("/pharmacydashboard")
def pharmacy_dashboard():

    ui.add_head_html(
        """
<style>
/* === GLOBAL DASHBOARD RESPONSIVE DESIGN === */
body {
    overflow-x: hidden !important;
}

/* Sidebar default look */
.nicegui-left-drawer {
    background: linear-gradient(180deg, #0fbad4, #11cdef);
    transition: all 0.3s ease-in-out;
    z-index: 999 !important;
}

/* --- Toggle Button (hamburger) --- */
.toggle-btn {
    display: none;
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 1000;
    background: #0fbad4;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 1.3rem;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

/* Show toggle button on mobile */
@media (max-width: 900px) {
    .toggle-btn {
        display: block;
    }
    .nicegui-left-drawer {
        position: fixed !important;
        height: 100vh !important;
        width: 220px !important;
        left: 0;
        top: 0;
        display: none; /* hidden by default */
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    .ml-64 {
        margin-left: 0 !important;
        padding: 1rem !important;
        width: 100% !important;
    }
}

/* Adjust cards and grids */
@media (max-width: 768px) {
    .nicegui-card {
        width: 100% !important;
        padding: 0.8rem !important;
        border-radius: 10px !important;
    }
    .nicegui-card img {
        width: 100% !important;
        height: 90px !important;
        object-fit: cover !important;
        border-radius: 10px !important;
    }
    .nicegui-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 0.8rem !important;
    }
}
@media (max-width: 500px) {
    .nicegui-grid {
        grid-template-columns: 1fr !important;
    }
}
</style>
"""
    )
    ui.add_head_html(
        """
<style>
@media (max-width: 900px) {
  .toggle-btn {
    display: block !important;
  }
}
@media (min-width: 901px) {
  .toggle-btn {
    display: none !important;
  }
}
</style>
"""
    )

    show_navbar()

    edit_uploaded_file_data = {}

    async def logout():
        app.storage.user.clear()
        ui.notify("Logged out.")
        ui.navigate.to("/signin")

    # === PHARMACY SIDEBAR ===
    with ui.left_drawer().classes("bg-sky-50 w-64 shadow-md text-gray-800"):
        with ui.column().classes("p-4 gap-y-2 h-full"):
            ui.button(
                "Add New Stock",
                icon="add_circle",
                on_click=lambda: ui.navigate.to("/create_ad"),
            ).classes(
                "w-full text-white font-semibold rounded-lg py-2.5 mb-4 hover:bg-[#2d868c]"
            ).props(
                "color=teal-600 unelevated"
            )
            # --- Sidebar Toggle Button (Always on Top) ---
            # --- Sidebar Toggle Button (Always on Top) ---
            ui.button("☰", on_click=toggle_sidebar).classes(
                "toggle-btn fixed z-[1001]"
            ).style(
                """top: 15px;left: 15px;
                    font-size: 1.8rem; background: #0fbad4; color: white; border-radius: 8px;box-shadow: 0 3px 8px rgba(0,0,0,0.3); padding: 6px 12px;cursor: pointer;"""
            )

            primary_links = [
                ("Dashboard", "/pharmacydashboard", "dashboard"),
                ("Inbox", "/inbox", "mail"),
                ("Outbox", "/sent_messages", "mail"),
            ]

            for label, route, icon_name in primary_links:
                with ui.row().classes(
                    "w-full items-center gap-4 px-3 py-2 rounded-lg hover:bg-[#d6eef0] cursor-pointer transition-all duration-200"
                ).on("click", lambda r=route: ui.navigate.to(r)):
                    ui.icon(icon_name).classes("text-[#34989e] text-xl")
                    ui.label(label).classes("text-base font-medium text-gray-700")

            ui.separator().classes("my-4")
            ui.label("ACCOUNT").classes(
                "text-xs font-semibold text-gray-500 uppercase px-3"
            )

            with ui.row().classes(
                "items-center gap-4 px-3 py-2 rounded-lg hover:bg-[#d6eef0] cursor-pointer"
            ).on("click", lambda: ui.navigate.to("/pharmacy/settings")):
                ui.icon("settings").classes("text-[#34989e] text-xl")
                ui.label("Settings").classes("text-base font-medium text-gray-700")

            ui.space()

            ui.button("Logout", icon="logout", on_click=logout).classes(
                "w-full bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl py-2.5 shadow-md hover:from-red-600 hover:to-red-700"
            ).props("color=teal600 unelevated")

    # === MAIN DASHBOARD CONTENT ===
    with ui.column().classes("w-full p-8 ml-64 bg-sky-50 min-h-screen items-center"):
        ui.query(".nicegui-content").classes("m-0 p-0")
        with ui.column().classes("w-full max-w-7xl"):  # Centered content with max-width
            ui.label("Pharmacy Dashboard").classes(
                "text-3xl font-bold text-sky-700 mb-6 w-full"
            )

        # --- Overview Cards ---
        stat_labels = {}
        with ui.row().classes("w-full gap-6"):
            card_titles = {
                "total_medicines": "Total Medicines",
                "pending_orders": "Pending Orders",
                "completed_sales": "Completed Sales",
                "customers": "Customers",
                "total_messages": "New Messages",
            }
            for key, title in card_titles.items():
                with ui.card().classes(
                    "bg-white shadow-md rounded-2xl flex-grow p-5 border-t-4 border-sky-500 flex flex-col items-center text-center"
                ):
                    ui.label(title).classes("text-gray-600 text-sm")
                    stat_labels[key] = ui.label("0").classes(
                        "text-3xl font-bold text-sky-700"
                    )

        ui.separator().classes("my-8")

        # --- AVAILABLE STOCK SECTION ---
        ui.label("AVAILABLE STOCK").classes("text-xl font-semibold text-sky-700 mb-4")
        stock_grid = ui.grid(columns=4).classes("w-full gap-4")

        # === DELETE DIALOG ===
        with ui.dialog() as delete_dialog, ui.card():
            ui.label("Are you sure?").classes("text-lg font-bold text-sky-700")
            ui.label("This action cannot be undone.").classes("text-gray-600")
            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button("Cancel", on_click=delete_dialog.close).props(
                    "flat color=grey-7"
                )
                confirm_delete_button = ui.button("Delete", color="red")

        # === EDIT DIALOG ===
        with ui.dialog() as edit_dialog, ui.card().classes("min-w-[400px]"):
            ui.label("Edit Medicine Details").classes(
                "text-xl font-bold text-sky-700 mb-4"
            )
            edit_item_id = None
            edit_name = (
                ui.input("Medicine Name").props("outlined dense").classes("w-full")
            )
            edit_quantity = (
                ui.number("Quantity", format="%.0f")
                .props("outlined dense")
                .classes("w-full")
            )
            edit_price = (
                ui.number("Price (GH₵)", format="%.2f")
                .props("outlined dense")
                .classes("w-full")
            )
            edit_category = (
                ui.input("Category").props("outlined dense").classes("w-full")
            )
            edit_description = (
                ui.textarea("Description").props("outlined dense").classes("w-full")
            )
            ui.label("Update Image (Optional)").classes(
                "text-sm font-semibold text-gray-700 mt-2"
            )
            edit_image_preview = ui.image().classes(
                "w-24 h-24 object-cover rounded-lg my-1"
            )
            edit_image_preview.visible = False

            async def handle_edit_upload(e: UploadEventArguments):
                try:
                    file = e.file
                    if not file:
                        return
                    content = await file.read()
                    file_name = getattr(file, "name", "flyer_edit")
                    file_type = getattr(
                        file, "content_type", "application/octet-stream"
                    )
                    edit_uploaded_file_data.clear()
                    edit_uploaded_file_data["name"] = file_name
                    edit_uploaded_file_data["content"] = content
                    edit_uploaded_file_data["type"] = file_type
                    b64_content = base64.b64encode(content).decode("utf-8")
                    data_url = f"data:{file_type};base64,{b64_content}"
                    edit_image_preview.set_source(data_url)
                    edit_image_preview.set_visibility(True)
                    ui.notify(f"New image selected: {file_name}")
                except Exception as ex:
                    ui.notify(f"Could not process file: {ex}", color="negative")

            ui.upload(
                on_upload=handle_edit_upload,
                auto_upload=True,
                max_files=1,
                label="Choose New Image",
            ).props("dense flat").classes("w-full mb-4")

            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button(
                    "Cancel",
                    on_click=lambda: (
                        edit_dialog.close(),
                        edit_uploaded_file_data.clear(),
                    ),
                ).props("flat color=grey-7")
                ui.button("Save Changes", on_click=lambda: handle_update()).classes(
                    "bg-sky-600 text-white hover:bg-sky-700"
                )

        # === DELETE ITEM FUNCTION ===
        async def delete_item(medicine_id: str, item_name: str):
            async def perform_delete():
                token = app.storage.user.get("access_token")
                if not token:
                    ui.notify("Auth error.", color="negative")
                    delete_dialog.close()
                    return
                headers = {"Authorization": f"Bearer {token}"}
                delete_url = f"{base_url}/inventory/my-stock/{medicine_id}"
                ui.notify(f"Deleting {item_name}...", spinner=True)
                try:
                    response = await asyncio.to_thread(
                        requests.delete, delete_url, headers=headers, timeout=15
                    )
                    if response.status_code in [200, 204]:
                        ui.notify(f"{item_name} deleted.", color="positive")
                        await fetch_data()  # This will refresh the dashboard counts
                    else:
                        error_detail = "Unknown error"
                        try:
                            error_detail = response.json().get("detail", error_detail)
                        except:
                            error_detail = response.text
                        ui.notify(
                            f"Delete failed: {error_detail} ({response.status_code})",
                            color="negative",
                            multi_line=True,
                        )
                except requests.RequestException as e:
                    ui.notify(f"Connection error: {e}", color="negative")
                finally:
                    delete_dialog.close()

            confirm_delete_button.remove_event_listeners("click")
            confirm_delete_button.on("click", perform_delete)
            delete_dialog.open()

        # === EDIT ITEM HANDLER ===
        def open_edit_dialog(item: dict):
            nonlocal edit_item_id
            item_id = item.get("id") or item.get("_id")
            if not item_id:
                ui.notify("Missing ID.", color="negative")
                return
            edit_item_id = item_id
            edit_name.set_value(item.get("medicine_name", ""))
            edit_quantity.set_value(item.get("quantity", 0))
            edit_price.set_value(item.get("price", 0.0))
            edit_category.set_value(item.get("category", ""))
            edit_description.set_value(item.get("description", ""))
            current_image_url = item.get("flyer")
            if current_image_url:
                edit_image_preview.set_source(current_image_url)
                edit_image_preview.set_visibility(True)
            else:
                edit_image_preview.set_visibility(False)
            edit_uploaded_file_data.clear()
            edit_dialog.open()

        async def handle_update():
            nonlocal edit_item_id
            if not edit_item_id:
                return
            token = app.storage.user.get("access_token")
            if not token:
                ui.notify("Auth error.", color="negative")
                return
            headers = {"Authorization": f"Bearer {token}"}
            update_url = f"{base_url}/inventory/my-stock/{edit_item_id}"
            try:
                updated_data = {
                    "medicine_name": edit_name.value,
                    "quantity": str(int(edit_quantity.value)),
                    "price": str(float(edit_price.value)),
                    "category": edit_category.value,
                    "description": edit_description.value,
                }
            except (ValueError, TypeError) as e:
                ui.notify(f"Invalid input: {e}", color="negative")
                return
            files_to_send = {}
            if "content" in edit_uploaded_file_data:
                files_to_send["flyer"] = (
                    edit_uploaded_file_data["name"],
                    edit_uploaded_file_data["content"],
                    edit_uploaded_file_data["type"],
                )
            ui.notify("Saving changes...", spinner=True)
            try:
                response = await asyncio.to_thread(
                    requests.put,
                    update_url,
                    headers=headers,
                    data=updated_data,
                    files=files_to_send if files_to_send else None,
                )
                if response.status_code == 200:
                    ui.notify("Update successful!", color="positive")
                    edit_dialog.close()
                    edit_uploaded_file_data.clear()
                    await fetch_data()  # This will refresh the dashboard counts
                else:
                    error_detail = "Unknown error"
                    try:
                        error_detail = response.json().get("detail", error_detail)
                    except:
                        error_detail = response.text
                    ui.notify(
                        f"Update failed: {error_detail} ({response.status_code})",
                        color="negative",
                        multi_line=True,
                    )
            except requests.RequestException as e:
                ui.notify(f"Connection error: {e}", color="negative")

        # === FETCH DASHBOARD DATA ===
        async def fetch_data():
            token = app.storage.user.get("access_token")
            if not token:
                ui.navigate.to("/signin")
                return
            headers = {"Authorization": f"Bearer {token}"}

            # --- This call will fail with 403, as seen in your logs ---
            # --- We will rely on other endpoints for counts ---
            try:
                stats_url = f"{base_url}/dashboard/stats"
                stats_response = await asyncio.to_thread(
                    requests.get, stats_url, headers=headers, timeout=20
                )
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    # These will likely not run, but we leave them as placeholders
                    stat_labels["pending_orders"].set_text(
                        str(stats_data.get("pending_orders", 0))
                    )
                    stat_labels["completed_sales"].set_text(
                        str(stats_data.get("completed_sales", 0))
                    )
                    stat_labels["customers"].set_text(
                        str(stats_data.get("customers", 0))
                    )
                else:
                    print(f"Error fetching stats: {stats_response.status_code}")
            except requests.RequestException as e:
                print(f"Error fetching stats: {e}")

            # --- FETCHING MESSAGES (Corrected for {'inbox': [...]}) ---
            try:
                messages_url = f"{base_url}/messages/inbox"
                messages_response = await asyncio.to_thread(
                    requests.get, messages_url, headers=headers, timeout=20
                )

                if messages_response.status_code == 200:
                    messages_data = messages_response.json()

                    # --- THIS IS THE FIX ---
                    message_count = 0
                    if isinstance(messages_data, dict) and "inbox" in messages_data:
                        message_list = messages_data.get("inbox", [])
                        message_count = len(message_list)
                    elif isinstance(messages_data, list):
                        message_count = len(messages_data)
                    # --- END OF FIX ---

                    stat_labels["total_messages"].set_text(str(message_count))
                else:
                    print(f"Error fetching messages: {messages_response.status_code}")
                    stat_labels["total_messages"].set_text("Err")

            except requests.RequestException as e:
                print(f"Connection error fetching messages: {e}")
                if "total_messages" in stat_labels:
                    stat_labels["total_messages"].set_text("Err")

            # === INVENTORY FETCH (With 'client deleted' fix and 'total_medicines' fix) ===
            try:
                stock_url = f"{base_url}/inventory/my-stock"
                stock_response = await asyncio.to_thread(
                    requests.get, stock_url, headers=headers, timeout=20
                )

                # --- FIX for "RuntimeError: client deleted" ---
                try:
                    stock_grid.clear()
                except RuntimeError as e:
                    print(f"Ignoring UI update for disconnected client: {e}")
                    return  # Stop function, user has left the page
                # --- END OF FIX ---

                with stock_grid:
                    if stock_response.status_code == 200:
                        response_data = stock_response.json()
                        stock_items = response_data.get("data", [])

                        # --- FIX FOR "TOTAL MEDICINES" CARD ---
                        if "total_medicines" in stat_labels:
                            stat_labels["total_medicines"].set_text(
                                str(len(stock_items))
                            )
                        # --- END OF FIX ---

                        if not stock_items:
                            ui.label("Inventory empty.").classes(
                                "col-span-full text-gray-500"
                            )
                            # We return *after* setting the total_medicines count to 0 (which len(stock_items) does)
                            return

                        for item in stock_items:
                            medicine_id = item.get("id") or item.get("_id")
                            medicine_name = item.get("medicine_name", "No Name")
                            if not medicine_id:
                                continue
                            with ui.card().tight().classes(
                                "w-full bg-white shadow-md rounded-xl"
                            ):
                                flyer_url = item.get("flyer")
                                if flyer_url:
                                    ui.image(flyer_url).classes(
                                        "w-full h-32 object-cover rounded-t-xl"
                                    )
                                else:
                                    with ui.column().classes(
                                        "w-full h-32 bg-sky-100 items-center justify-center rounded-t-xl"
                                    ):
                                        ui.icon(
                                            "medication", size="xl", color="sky-600"
                                        )
                                with ui.card_section():
                                    ui.badge(
                                        item.get("category", "N/A"), color="sky"
                                    ).classes("mb-2")
                                    ui.label(medicine_name).classes(
                                        "text-lg font-bold text-sky-700"
                                    )
                                    description = item.get(
                                        "description", "No description."
                                    )
                                    ui.label(
                                        description[:50] + "..."
                                        if len(description) > 50
                                        else description
                                    ).classes("text-sm text-gray-500 my-1 h-10")
                                    ui.label(
                                        f"Price: GHS {item.get('price', 0):.2f}"
                                    ).classes("text-gray-700")
                                    ui.label(
                                        f"Stock: {item.get('quantity', 0)}"
                                    ).classes("text-gray-700")
                                    with ui.row().classes(
                                        "w-full justify-end gap-1 mt-2"
                                    ):
                                        ui.button(
                                            icon="edit",
                                            on_click=lambda item_data=item: open_edit_dialog(
                                                item_data
                                            ),
                                        ).props("flat round dense color=grey-8")
                                        ui.button(
                                            icon="delete",
                                            color="red",
                                            on_click=lambda mid=medicine_id, mname=medicine_name: delete_item(
                                                mid, mname
                                            ),
                                        ).props("flat round dense")
                    else:
                        ui.label(
                            f"Error loading stock ({stock_response.status_code})"
                        ).classes("col-span-full text-red-500")

            except requests.RequestException as e:
                try:
                    stock_grid.clear()
                    with stock_grid:
                        ui.label(f"Could not connect to fetch stock: {e}").classes(
                            "col-span-full text-red-500"
                        )
                except RuntimeError as re:
                    print(f"Ignoring UI update for disconnected client: {re}")

    ui.timer(0.1, fetch_data, once=True)
