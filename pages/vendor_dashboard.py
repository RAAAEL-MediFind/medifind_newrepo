from nicegui import ui, app
import asyncio
import requests
from components.navbar import show_navbar  # Assuming this exists
from utils.api import base_url  # Make sure base_url is defined
from nicegui.events import UploadEventArguments  # Import for upload handling
import base64  # Import for image preview

# --- Sidebar State & Toggle Logic ---
sidebar_visible_on_mobile = False  # Initially hidden on mobile
sidebar_drawer = None  # Placeholder


def toggle_sidebar():
    global sidebar_visible_on_mobile
    sidebar_visible_on_mobile = not sidebar_visible_on_mobile
    if sidebar_drawer:
        # We rely on toggle_and_style now
        pass


@ui.page("/pharmacydashboard")  # Note: Ensure this route is unique
def pharmacy_dashboard():
    global sidebar_drawer

    # --- CSS for Responsiveness ---
    ui.add_head_html("""
<style>
/* Default styles (Desktop) */
body { 
    overflow-x: hidden !important; 
    background-color: #f0f9ff; /* <-- ★★★ CHANGED BACK TO BLUE ★★★ */
}

.nicegui-left-drawer {
    position: fixed !important; left: 0; top: 0;
    height: 100vh; width: 16rem;
    background-color: #f0f9ff; /* <-- Sidebar is blue */
    box-shadow: 0 2px 8px rgba(0,0,0,0.1); color: #374151;
    transition: transform 0.3s ease-in-out; transform: translateX(0);
    z-index: 999;
}

.main-dashboard-content {
    align-items: flex-start !important; /* Forces left-alignment */
    margin-left: 16rem; 
    padding: 0 !important; /* FORCING PADDING TO ZERO */
    background-color: #f0f9ff; /* <-- ★★★ CHANGED BACK TO BLUE ★★★ */
    min-height: 100vh;
    transition: margin-left 0.3s ease-in-out;
    width: calc(100% - 16rem);
}


.toggle-btn { display: none; }

/* Mobile Styles (< 900px) */
@media (max-width: 900px) {
    .nicegui-left-drawer {
        transform: translateX(-100%);
        width: 250px !important;
    }
    .nicegui-left-drawer.open {
        transform: translateX(0);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .main-dashboard-content { margin-left: 0 !important; width: 100% !important; padding: 0 !important; }
    .toggle-btn {
        display: block !important; position: fixed; top: 1rem; left: 1rem; z-index: 1001;
        background: #0ea5e9; color: white; border: none; border-radius: 8px;
        padding: 6px 10px; font-size: 1.5rem; cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    body.sidebar-open .main-dashboard-content::before {
        content: ''; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background-color: rgba(0, 0, 0, 0.5); z-index: 998;
    }
    .nicegui-header { padding-left: 4.5rem !important; position: relative; z-index: 900; }
}

/* Card and Grid Adjustments */
@media (max-width: 1200px) {
     .overview-cards .nicegui-card { min-width: 180px; }
     .stock-grid { grid-template-columns: repeat(3, 1fr) !important; }
}
@media (max-width: 768px) {
     .overview-cards { flex-direction: column; gap: 1rem !important; }
     .stock-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 0.8rem !important; }
     .stock-grid .nicegui-card img { height: 100px !important; }
     .stock-grid .nicegui-card .text-lg { font-size: 1rem !important; }
     .stock-grid .nicegui-card .text-sm { font-size: 0.8rem !important; height: auto !important; min-height: 2.5rem; }
}
@media (max-width: 500px) {
    .stock-grid { grid-template-columns: 1fr !important; }
    /* Inner padding on mobile */
    .w-full.p-0 { padding: 0.5rem !important; } /* Give a little space on mobile */
    .nicegui-card { padding: 0.75rem !important; }
}
</style>
""")

    show_navbar()

    toggle_button = ui.button("☰").classes("toggle-btn")

    edit_uploaded_file_data = {}

    async def logout():
        app.storage.user.clear()
        ui.notify("Logged out.")
        ui.navigate.to("/signin")

    # === PHARMACY SIDEBAR ===
    sidebar_drawer = ui.left_drawer().classes("nicegui-left-drawer")
    with sidebar_drawer:
        toggle_button.on('click', lambda: toggle_and_style(sidebar_drawer))

        with ui.column().classes("p-4 gap-y-2 h-full"):
            ui.button("Add New Stock", icon="add_circle", on_click=lambda: ui.navigate.to("/create_ad")).classes(
                "w-full bg-[#34989e] text-white font-semibold rounded-lg py-2.5 mb-4 hover:bg-[#2d868c]"
            )
            primary_links = [
                ("Dashboard", "/pharmacydashboard", "dashboard"),
                ("Inbox", "/inbox", "mail"),
                ("Outbox", "/sent_messages", "outgoing_mail"),
            ]
            for label, route, icon_name in primary_links:
                with ui.row().classes("w-full items-center gap-4 px-3 py-2 rounded-lg hover:bg-sky-100 cursor-pointer").on(
                    "click", lambda r=route: ui.navigate.to(r)
                ):
                    ui.icon(icon_name).classes("text-sky-600 text-xl")
                    ui.label(label).classes("text-base font-medium text-gray-700")
            ui.separator().classes("my-4")
            ui.label("ACCOUNT").classes("text-xs font-semibold text-gray-500 uppercase px-3")
            with ui.row().classes("items-center gap-4 px-3 py-2 rounded-lg hover:bg-sky-100 cursor-pointer").on(
                "click", lambda: ui.navigate.to("/pharmacy/settings")
            ):
                ui.icon("settings").classes("text-sky-600 text-xl")
                ui.label("Settings").classes("text-base font-medium text-gray-700")
            ui.space()
            ui.button("Logout", icon="logout", on_click=logout).classes(
                "w-full bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl py-2.5 shadow-md hover:from-red-600 hover:to-red-700"
            ).props("unelevated")

    # === MAIN DASHBOARD CONTENT ===
    with ui.column().classes("main-dashboard-content") as main_content:
        #
        # 'p-0' is 0px. This makes it touch.
        # If this is TOO close, change it to 'p-1' (4px) or 'p-2' (8px)
        #
        with ui.column().classes("w-full p-0"): 
            ui.label("Pharmacy Dashboard").classes("text-3xl font-bold text-sky-700 mb-6 w-full")
            stat_labels = {}

            # --- Top 4 Stat Cards ---
            with ui.row().classes("w-full gap-4 md:gap-6 flex-wrap overview-cards"):
                card_titles = {
                    "total_medicines": "Total Medicines",
                    "pending_orders": "Pending Orders",
                    "completed_sales": "Completed Sales",
                    "customers": "Customers",
                }
                for key, title in card_titles.items():
                    with ui.card().classes("bg-white shadow rounded-xl p-4 border-t-4 border-sky-500 flex flex-col items-center text-center min-w-[150px]"):
                        ui.label(title).classes("text-gray-600 text-sm font-medium")
                        stat_labels[key] = ui.label("0").classes("text-3xl font-bold text-sky-700 mt-1")
            
            # --- "New Messages" Card (separate row) ---
            with ui.row().classes("w-full gap-4 md:gap-6 flex-wrap mt-6"): # mt-6 adds space
                with ui.card().classes("bg-white shadow rounded-xl p-4 border-t-4 border-sky-500 flex flex-col items-center text-center min-w-[150px]"):
                    ui.label("New Messages").classes("text-gray-600 text-sm font-medium")
                    stat_labels["total_messages"] = ui.label("0").classes("text-3xl font-bold text-sky-700 mt-1")

            ui.label("AVAILABLE STOCK").classes("text-xl font-semibold text-sky-700 mt-8 mb-4") 
            stock_grid = ui.grid().classes("w-full gap-4 stock-grid")
    
    # --- Toggle Drawer ---
    sidebar_open_state = True

    def toggle_and_style(drawer: ui.left_drawer):
        nonlocal sidebar_open_state
        sidebar_open_state = not sidebar_open_state
        drawer.classes(remove='open' if not sidebar_open_state else '', add='open' if sidebar_open_state else 'open')
        ui.run_javascript(f"document.body.classList.toggle('sidebar-open', {str(sidebar_open_state).lower()});")
        ui.run_javascript(f"""
            const mainContent = document.querySelector('.main-dashboard-content');
            if (window.innerWidth > 900 && mainContent) {{
                 mainContent.style.marginLeft = '{'16rem' if sidebar_open_state else '0'}';
                 mainContent.style.width = 'calc(100% - {'16rem' if sidebar_open_state else '0px'})';
            }} else if (mainContent) {{
                 mainContent.style.marginLeft = '0';
                 mainContent.style.width = '100%';
            }}
        """)

    # === FETCH DATA ===
    async def fetch_data():
        token = app.storage.user.get("access_token")
        if not token:
            ui.navigate.to("/signin")
            return

        headers = {"Authorization": f"Bearer {token}"}

        # --- Fetch Stats ---
        try:
            stats_url = f"{base_url}/dashboard/stats"
            stats_response = await asyncio.to_thread(requests.get, stats_url, headers=headers, timeout=10)
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                if "pending_orders" in stat_labels:
                    stat_labels["pending_orders"].set_text(str(stats_data.get("pending_orders", 0)))
                if "completed_sales" in stat_labels:
                    stat_labels["completed_sales"].set_text(str(stats_data.get("completed_sales", 0)))
                if "customers" in stat_labels:
                    stat_labels["customers"].set_text(str(stats_data.get("customers", 0)))
        except requests.RequestException as e:
            print(f"Error fetching stats: {e}")

        # --- Fetch Inventory ---
        try:
            stock_url = f"{base_url}/inventory/my-stock"
            stock_response = await asyncio.to_thread(requests.get, stock_url, headers=headers, timeout=15)

            try:
                stock_grid.clear()
            except RuntimeError as e:
                print(f"Ignoring UI update for disconnected client: {e}")
                return

            with stock_grid:
                if stock_response.status_code == 200:
                    response_data = stock_response.json()
                    stock_items = response_data.get("data", [])
                    if "total_medicines" in stat_labels:
                        stat_labels["total_medicines"].set_text(str(len(stock_items)))
                    if not stock_items:
                        ui.label("Inventory empty.").classes("col-span-full text-gray-500")
                        return
                    for item in stock_items:
                        medicine_id = item.get("id") or item.get("_id")
                        medicine_name = item.get("medicine_name", "No Name")
                        if not medicine_id:
                            continue
                        with ui.card().tight().classes("w-full bg-white shadow-md rounded-xl"):
                            flyer_url = item.get("flyer")
                            if flyer_url:
                                ui.image(flyer_url).classes("w-full h-32 object-cover rounded-t-xl")
                            else:
                                with ui.column().classes("w-full h-32 bg-sky-100 items-center justify-center rounded-t-xl"):
                                    ui.icon("medication", size="xl", color="sky-600")
                            with ui.card_section():
                                ui.badge(item.get("category", "N/A"), color="sky").classes("mb-1 text-xs")
                                ui.label(medicine_name).classes("text-base font-semibold text-sky-700 leading-tight")
                                description = item.get("description", "")
                                ui.label(description[:40] + "..." if len(description) > 40 else description).classes("text-xs text-gray-500 my-1 h-8")
                                ui.label(f"GH₵ {item.get('price', 0):.2f}").classes("text-sm text-gray-700 font-medium")
                                ui.label(f"Stock: {item.get('quantity', 0)}").classes("text-xs text-gray-600")
                                with ui.row().classes("w-full justify-end gap-1 mt-1"):
                                    ui.button(icon="edit", on_click=lambda item_data=item: print(f"Edit {item_data}")).props("flat round dense color=grey-8 size=sm")
                                    ui.button(icon="delete", color="red", on_click=lambda mid=medicine_id, mname=medicine_name: print(f"Delete {mid}, {mname}")).props("flat round dense size=sm")
                else:
                    ui.label(f"Error loading stock ({stock_response.status_code})").classes("col-span-full text-red-500")

        except requests.RequestException as e:
            try:
                stock_grid.clear()
                with stock_grid:
                    ui.label(f"Could not connect to fetch stock: {e}").classes("col-span-full text-red-500")
            except RuntimeError as re:
                print(f"Ignoring UI update for disconnected client: {re}")

    # ✅ Correct placement — outside fetch_data(), inside pharmacy_dashboard()
    ui.timer(0.1, fetch_data, once=True)
