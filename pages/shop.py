from nicegui import ui, app
import requests
import asyncio

# Assuming these modules are correctly set up and accessible
from components.navbar import show_navbar
from components.footer import show_footer

# Assume base_url is defined in utils.api
# Example: base_url = "http://api.example.com"
from utils.api import (
    base_url,
)  # Although not used for image URLs, keep for potential future use

# --- GLOBAL SHOPPING CART DATA STRUCTURE (UNCHANGED) ---
shopping_cart_items = []


def get_cart_count():
    """Calculates the total number of items in the cart."""
    return sum(item["quantity"] for item in shopping_cart_items)


# --- PAYMENT DIALOG FUNCTION (UNCHANGED) ---
async def show_payment_dialog(
    title: str, price: float, vendor_name: str, momo_details: dict
):
    """
    Displays a dialog for the user to select a payment method, showing specific vendor details.
    Returns the selected payment method string.
    """
    payment_method = None

    # The dialog is inherently centered and will scale down nicely on mobile.
    with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg mx-auto"):
        ui.label(f"Checkout: {title}").classes("text-xl font-bold mb-2")
        ui.label(f"Sold by: {vendor_name}").classes("text-md text-gray-600 mb-1")
        ui.label(f"Total Amount: GH₵ {price:.2f}").classes("text-lg text-teal-600 mb-4")

        details_container = ui.column().classes(
            "w-full p-4 border rounded-lg bg-gray-50 mt-4"
        )

        def update_payment_details(e):
            """Updates the content of the details container based on the radio selection."""
            nonlocal payment_method
            payment_method = e.value
            details_container.clear()

            with details_container:
                if e.value == "MTN Mobile Money":
                    momo_number = momo_details.get("MTN", "N/A")
                    ui.label("You selected MTN Mobile Money (MoMo).").classes(
                        "font-semibold"
                    )
                    ui.markdown(
                        f"""
- **Payable To:** **{vendor_name}**
- **Merchant Number (MTN):** **{momo_number}**
- **Amount:** **GH₵ {price:.2f}**
- **Reference:** `{title.replace(' ', '-').upper()}`
                        
**Please complete the transaction on your phone and click 'Confirm Payment'.**
"""
                    ).classes("text-sm")

                elif e.value == "Telecel Cash":
                    momo_number = momo_details.get("TELECEL", "N/A")
                    ui.label(
                        "You selected Telecel Cash (formerly Vodafone Cash)."
                    ).classes("font-semibold")
                    ui.markdown(
                        f"""
- **Payable To:** **{vendor_name}**
- **Merchant Number (Telecel):** **{momo_number}**
- **Amount:** **GH₵ {price:.2f}**
- **Reference:** `{title.replace(' ', '-').upper()}`
                        
**Please complete the transaction on your phone and click 'Confirm Payment'.**
"""
                    ).classes("text-sm")

                elif e.value == "Cash on Pickup":
                    ui.label("You selected Cash on Pickup. 💰").classes("font-semibold")
                    ui.label(
                        f"You will pay **GH₵ {price:.2f}** in cash when you pick up the item at **{vendor_name}**."
                    ).classes("text-sm")

        ui.radio(
            options=["MTN Mobile Money", "Telecel Cash", "Cash on Pickup"],
            value="MTN Mobile Money",
            on_change=update_payment_details,
        ).classes("mb-2").props("color=teal-600")

        # Initial call to set up the default view
        update_payment_details(type("obj", (object,), {"value": "MTN Mobile Money"}))

        with ui.row().classes("w-full justify-end mt-6 space-x-2"):
            ui.button(
                "Cancel", on_click=lambda: dialog.submit(None), color="grey"
            ).props("flat")
            ui.button(
                "Confirm Payment",
                on_click=lambda: dialog.submit(payment_method),
                color="teal-600",
            )

    return await dialog


# --- BUY NOW HANDLER (UNCHANGED) ---
async def handle_buy_now(
    title: str, price: float, vendor_name: str, momo_details: dict
):
    """Handles the Quick Buy click (single item checkout)."""
    selected_method = await show_payment_dialog(title, price, vendor_name, momo_details)

    if selected_method:
        ui.notify(
            f"Quick Buy for {title} placed. Payment method: {selected_method}",
            type="positive",
            timeout=5000,
        )
    else:
        ui.notify(f"Quick Buy of {title} cancelled.", type="info")


# 🌟 --- PRODUCT CARD COMPONENT (MODIFIED: Always Column Layout for Buttons) --- 🌟
def product_card(
    image_url,
    title,
    category,
    description,
    price,
    vendor_name,
    momo_details,
    checkout_button_update_ref,
):
    """A UI component that displays a single product card with all details."""

    # Handler for ADD TO CART (Logic unchanged)
    def add_item_to_cart(p_title, p_price, p_vendor, p_momo):
        # Check if item is already in cart
        for item in shopping_cart_items:
            if item["title"] == p_title:
                item["quantity"] += 1
                ui.notify(
                    f"Added another {p_title}. Cart: {get_cart_count()} items",
                    timeout=2000,
                )
                checkout_button_update_ref.refresh()
                return

        # If not in cart, add new item
        shopping_cart_items.append(
            {
                "title": p_title,
                "price": p_price,
                "vendor_name": p_vendor,
                "momo_details": p_momo,
                "quantity": 1,
            }
        )
        ui.notify(
            f"Added {p_title} to cart. Cart: {get_cart_count()} items", timeout=2000
        )
        checkout_button_update_ref.refresh()

    with ui.card().classes(
        "w-80 rounded-2xl shadow-md hover:shadow-lg transition p-4 flex flex-col justify-between h-full"
    ) as card:
        card.product_data = {
            "title": title.lower(),
            "category": category.lower(),
            "description": description.lower(),
        }

        # Image and Info (Unchanged)
        with ui.element("div").classes("w-full h-48 rounded-xl overflow-hidden mb-3"):
            if image_url:
                ui.image(image_url).classes("w-full h-full object-cover")
            else:
                with ui.column().classes(
                    "w-full h-full bg-gray-100 flex items-center justify-center"
                ):
                    ui.icon("medication", size="xl", color="gray-400")
        with ui.column().classes("mt-1 text-center w-full flex-grow"):
            ui.label(category).classes("text-xs text-gray-400")
            ui.label(title).classes("font-semibold text-gray-800 text-base")
            desc_text = (
                (description[:50] + "...")
                if description and len(description) > 50
                else description or "No description."
            )
            ui.label(desc_text).classes("text-sm text-gray-500 my-1 h-10")
            ui.label(f"GH₵ {price:.2f}").classes(
                "text-gray-800 font-semibold text-lg mt-2"
            )

        # 🚀 ADD TO CART BUTTONS: Always stack vertically (column) on all screens
        with ui.column().classes(
            "justify-center mt-3 w-full gap-2"  # ui.column() defaults to flex-col
        ):
            # ADD TO CART button (W-FULL ensures it spans the column width)
            ui.button(
                "ADD TO CART",
                icon="shopping_cart",
                on_click=lambda t=title, p=price, v=vendor_name, m=momo_details: add_item_to_cart(
                    t, p, v, m
                ),
            ).classes(
                "hover:bg-teal-700 text-white px-3 py-2 rounded-full shadow text-sm w-full"
            ).props(
                "color=teal-600"
            )

            # QUICK BUY button (W-FULL ensures it spans the column width)
            ui.button(
                "QUICK BUY",
                icon="flash_on",
                on_click=lambda t=title, p=price, v=vendor_name, m=momo_details: handle_buy_now(
                    t, p, v, m
                ),
            ).classes(
                "hover:bg-blue-700 text-white px-3 py-2 rounded-full shadow text-sm w-full"
            ).props(
                "color=teal-600"
            )


@ui.page("/shop")
def shop_page():
    show_navbar()

    # --- CHECKOUT DIALOG FUNCTION (NEW - Defined within shop_page scope) ---
    async def show_checkout_dialog():
        """Shows the consolidated cart view and initiates the payment process."""
        if not shopping_cart_items:
            ui.notify("Your cart is empty!", type="info")
            return

        # IMPORTANT: This assumes all items in the cart are from the same vendor
        # (or at least that all payments go to the same central MoMo account).
        # This simplification is retained from the original logic.
        total_amount = sum(
            item["price"] * item["quantity"] for item in shopping_cart_items
        )

        vendor_name_for_momo = shopping_cart_items[0]["vendor_name"]
        momo_details_for_momo = shopping_cart_items[0]["momo_details"]

        with ui.dialog() as dialog, ui.card().classes("w-full max-w-xl mx-auto"):
            ui.label("Shopping Cart Checkout").classes("text-2xl font-bold mb-4")

            # Cart Item List
            with ui.column().classes("w-full border p-3 rounded-lg"):
                for item in shopping_cart_items:
                    with ui.row().classes(
                        "w-full justify-between items-center py-1 border-b"
                    ):
                        ui.label(f"{item['title']} (x{item['quantity']})").classes(
                            "text-lg"
                        )
                        ui.label(f"GH₵ {item['price'] * item['quantity']:.2f}").classes(
                            "font-semibold text-teal-700"
                        )

                ui.label(f"Order Total: GH₵ {total_amount:.2f}").classes(
                    "text-xl font-extrabold mt-3"
                )

            ui.label("Proceed to payment for the total order amount.").classes(
                "mt-4 text-md font-semibold"
            )

            async def initiate_payment():
                dialog.close()
                # Create a generic reference for a consolidated order
                order_ref = f"BULK-ORDER-ITEMS:{len(shopping_cart_items)}-QTY:{get_cart_count()}"

                final_method = await show_payment_dialog(
                    title=order_ref,
                    price=total_amount,
                    vendor_name=vendor_name_for_momo,
                    momo_details=momo_details_for_momo,
                )

                if final_method:
                    ui.notify(
                        f"Consolidated order successful via {final_method}. Total: GH₵ {total_amount:.2f}",
                        type="positive",
                        timeout=6000,
                    )
                    shopping_cart_items.clear()
                    checkout_button_update.refresh()
                else:
                    ui.notify("Consolidated payment cancelled.", type="info")

            with ui.row().classes("w-full justify-end mt-6 space-x-2"):
                ui.button("Back to Shop", on_click=dialog.close, color="grey").props(
                    "flat"
                )
                ui.button(
                    "Proceed to Payment", on_click=initiate_payment, color="green"
                ).props("icon=payment")

        await dialog

    # --- CHECKOUT BUTTON REFRESHABLE (FIXED: Defined within shop_page) ---
    @ui.refreshable
    def checkout_button_update():
        ui.button(
            f"🛒  ({get_cart_count()} items)", on_click=show_checkout_dialog
        ).classes("text-lg font-bold max-w-sm mb-4").props("color=teal-600")

    # --- Main Container ---
    # 🌟 RESPONSIVE CONTAINER: Added p-4 for good mobile padding.
    with ui.column().classes(
        "w-full items-center pb-10 bg-[#f0f7fa] min-h-screen px-4"
    ):
        ui.label("Shop All Products").classes(
            "text-4xl font-bold text-center mt-20 mb-6 text-gray-800"
        )

        # --- Styled Search Bar ---
        with ui.row().classes("w-full max-w-xl justify-center mb-4"):
            search_input = (
                ui.input(placeholder="Search by name, category, or description...")
                .props("outlined rounded clearable dense bg-color=white")
                .classes("flex-grow")
                .style("border-radius: 9999px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);")
            )
            search_input.add_slot("prepend")
            with search_input:
                ui.icon("search", color="grey-6").classes("ml-2")

        # --- Checkout Button at the top ---
        checkout_button_update()  # Call the refreshable function here

        # --- Grid for Product Cards ---
        # 🌟 RESPONSIVE GRID:
        products_grid = ui.grid().classes(
            "w-full max-w-7xl justify-center gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
        )

    # Store all fetched products
    all_products_data = []

    def update_product_display():
        """Filters products based on search input and updates the grid."""
        search_term = search_input.value.lower().strip()
        products_grid.clear()
        found_products = False
        with products_grid:
            if not all_products_data:
                ui.label("Loading or no products available.").classes(
                    "col-span-full text-center text-gray-500 mt-4"
                )
                return

            for product in all_products_data:
                title_lower = product.get("medicine_name", "").lower()
                category_lower = product.get("category", "").lower()
                description_lower = product.get("description", "").lower()

                if (
                    search_term in title_lower
                    or search_term in category_lower
                    or search_term in description_lower
                ):

                    image_url = product.get("flyer")
                    title = product.get("medicine_name", "No Title")
                    category = product.get("category", "Uncategorized")
                    description = product.get("description", "")
                    price = product.get("price", 0.0)

                    vendor_name = product.get(
                        "vendor_name", "MediFind Partner Pharmacy"
                    )
                    momo_details = product.get(
                        "momo_details",
                        {"MTN": "054 123 4567", "TELECEL": "050 987 6543"},
                    )

                    product_card(
                        image_url=image_url,
                        title=title,
                        category=category,
                        description=description,
                        price=price,
                        vendor_name=vendor_name,
                        momo_details=momo_details,
                        checkout_button_update_ref=checkout_button_update,  # PASS THE REF HERE
                    )
                    found_products = True

            if not found_products and search_term:
                ui.label(f"No products found matching '{search_input.value}'").classes(
                    "col-span-full text-center text-gray-500 mt-4"
                )
            elif not found_products and not search_term and not all_products_data:
                ui.label("No products available at the moment.").classes(
                    "col-span-full text-center text-gray-500 mt-4"
                )

    # Connect search input
    search_input.on("change", update_product_display)

    async def fetch_and_store_products():
        """Fetches all products initially and stores them."""
        nonlocal all_products_data
        endpoint_url = f"{base_url}/search/all"
        try:
            with products_grid:
                products_grid.clear()
                with ui.column().classes("col-span-full items-center mt-8"):
                    ui.spinner(size="lg")
                    ui.label("Loading products...").classes("text-gray-500")

            response = await asyncio.to_thread(requests.get, endpoint_url, timeout=30)

            if response.status_code == 200:
                response_data = response.json()
                all_products_data = response_data.get("data", [])

                if not isinstance(all_products_data, list):
                    all_products_data = []
                    ui.notify(
                        "Received unexpected data format from API.", color="negative"
                    )

            else:
                all_products_data = []
                ui.notify(
                    f"Error fetching products: Status {response.status_code}",
                    color="negative",
                )

        except requests.RequestException as e:
            all_products_data = []
            ui.notify(f"Connection Error: {e}", color="negative")
            products_grid.clear()
            with products_grid:
                ui.label("Connection Error. Could not load products.").classes(
                    "col-span-full text-center text-red-500 mt-4"
                )

        finally:
            update_product_display()
            checkout_button_update.refresh()

    # Fetch data on page load
    ui.timer(0.1, fetch_and_store_products, once=True)

    show_footer()
