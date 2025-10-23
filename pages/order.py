from nicegui import ui, app
import requests
from utils.api import base_url
from components.navbar import show_navbar
from components.sidebar import show_sidebar
from components.footer import show_footer

# --- API Call ---


def fetch_order_details_sync(order_id):
    """Fetch a single order’s detailed info."""
    try:
        token = app.storage.user.get("token", "YOUR_AUTH_TOKEN")
        headers = {"Authorization": f"Bearer {token}"}
        api_url = f"{base_url}/orders/{order_id}"

        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching order details: {e}")
        return {"error": "Failed to load order details."}


# --- Page Definition ---


@ui.page("/order")
def order_details_page(order_id: str):
    """Display detailed information about a specific order."""

    if not app.storage.user.get("authenticated"):
        ui.navigate.to("/signin")
        return

    show_navbar()
    show_sidebar()

    with ui.column().classes("mt-24 px-8 gap-8 max-w-5xl mx-auto w-full"):
        ui.label("Order Details").classes("text-4xl font-bold text-sky-700 mb-2")
        ui.separator().classes("opacity-50")

        details_container = ui.column().classes("w-full gap-6")
        loading_label = ui.label("Loading order details...").classes(
            "text-lg text-gray-500 italic"
        )

        async def load_order_details():
            details_container.clear()
            loading_label.visible = True

            result = await ui.run.io_bound(fetch_order_details_sync, order_id)
            loading_label.visible = False

            if not result or result.get("error"):
                ui.label(result.get("error", "Could not load details")).classes(
                    "text-red-500 text-xl"
                )
                return

            order = result.get("order", result)

            # --- Top Section: Summary ---
            with details_container:
                with ui.card().classes(
                    "w-full rounded-2xl shadow-xl border border-gray-200 bg-white p-4"
                ):
                    ui.label(f"Order #{order.get('id', 'N/A')}").classes(
                        "text-2xl font-bold text-gray-800"
                    )
                    ui.label(f"Placed on: {order.get('date', 'Unknown')}").classes(
                        "text-sm text-gray-600"
                    )

                    # Status Badge
                    status = order.get("status", "Pending")
                    status_color = {
                        "Pending": "orange",
                        "Shipped": "blue",
                        "Delivered": "green",
                        "Cancelled": "red",
                    }.get(status, "gray")

                    ui.badge(status, color=status_color).classes(
                        "text-white font-semibold px-4 py-2 rounded-full mt-2"
                    )

                    # --- Status Progress Tracker ---
                    steps = ["Pending", "Shipped", "Delivered"]
                    active_index = (
                        steps.index(status) if status in steps else len(steps) - 1
                    )

                    with ui.row().classes("justify-between items-center mt-6 w-full"):
                        for i, step in enumerate(steps):
                            color = status_color if i <= active_index else "gray"
                            with ui.column().classes("items-center w-full"):
                                ui.icon(
                                    "check_circle"
                                    if i <= active_index
                                    else "radio_button_unchecked"
                                ).classes(f"text-{color}-500 text-3xl")
                                ui.label(step).classes(
                                    f"text-sm font-medium text-{color}-600"
                                )
                                if i < len(steps) - 1:
                                    ui.linear_progress(
                                        value=1.0 if i < active_index else 0.3,
                                        color=color,
                                        show_value=False,
                                    ).classes("w-full h-1 rounded-full mt-1")

            # --- Ordered Items Section ---
            with ui.card().classes(
                "w-full rounded-2xl shadow-lg bg-white p-4 border border-gray-100"
            ):
                ui.label("Ordered Items").classes(
                    "text-xl font-semibold text-gray-800 mb-2"
                )

                items = order.get("items", [])
                if not items:
                    ui.label("No items found for this order.").classes(
                        "text-gray-500 italic"
                    )
                else:
                    for item in items:
                        with ui.row().classes(
                            "justify-between items-center py-2 border-b border-gray-200 last:border-none"
                        ):
                            ui.label(item.get("name", "Unnamed Item")).classes(
                                "font-medium text-gray-800"
                            )
                            ui.label(f"Qty: {item.get('quantity', 1)}").classes(
                                "text-gray-600"
                            )
                            ui.label(f"${item.get('price', 0):.2f}").classes(
                                "font-semibold text-gray-700"
                            )

            # --- Total & Actions ---
            with ui.card().classes(
                "w-full rounded-2xl shadow-lg bg-white p-4 border border-gray-100"
            ):
                ui.label("Order Summary").classes(
                    "text-xl font-semibold text-gray-800 mb-2"
                )

                ui.label(f"Subtotal: ${order.get('subtotal', 0):.2f}").classes(
                    "text-gray-700"
                )
                ui.label(f"Shipping: ${order.get('shipping', 0):.2f}").classes(
                    "text-gray-700"
                )
                ui.separator().classes("my-2 opacity-40")
                ui.label(f"Total: ${order.get('total', 0):.2f}").classes(
                    "text-lg font-bold text-sky-700"
                )

            # --- Back Button ---
            ui.button(
                "← Back to My Orders", on_click=lambda: ui.navigate.to("/orders")
            ).classes(
                "mt-6 bg-gray-700 text-white hover:bg-gray-800 px-6 py-2 rounded-full"
            )

        ui.timer(0.1, load_order_details, once=True)

    show_footer()
