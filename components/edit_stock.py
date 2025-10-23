from nicegui import ui, app
import asyncio

# This variable will hold a reference to the save button.
_save_changes_btn: ui.button = None


@ui.page("/edit_stock")
def show_edit_event_page():
    global _save_changes_btn

    # --- Page Styling (copied from create_ad) ---
    ui.add_head_html(
        """
    <style>
    body {
        margin: 0;
        background:url('/assets/create.jpg') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Poppins', sans-serif;
        color: white;
        overflow: hidden; /* Prevent the main body from scrolling */
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
            ui.label("EDIT STOCK DETAILS").classes(
                "font-extrabold text-4xl tracking-wide text-center text-teal-900"
            )

            # --- Input Fields ---
            title = ui.input("Medication Name").props("outlined").classes("w-full")
            description = ui.textarea("Description").props("outlined").classes("w-full")
            price = ui.number("Price").props("outlined").classes("w-full")

            # --- Category Selection ---
            ui.label("Categories").classes("font-medium text-gray-600")
            categories = (
                ui.select(
                    [
                        "ANALGESICS",
                        "ANTIBIOTICS",
                        "ANTI HYPERTENSIVES",
                        "ANTI DIABETICS",
                        "ANTI VIRAL",
                        "ANTI ULCERS",
                    ]
                )
                .classes("w-full text-gray-800")
                .props('outlined popup-content-class="text-gray-800"')
            )
            stock = ui.number("Available Stock").props("outlined").classes("w-full")

            # --- Uploader ---
            ui.label("Upload new image (optional)").classes("font-medium text-gray-600")
            flyer = (
                ui.upload()
                .classes("w-full rounded-lg border border-dashed border-gray-400 p-4")
                .props("color=teal")
            )

            # --- Async Save Function ---
            async def save_changes():
                if not title.value:
                    ui.notify("Please enter a medication name.", color="negative")
                    return

                # Provide visual feedback on click
                _save_changes_btn.props(add="disable loading")
                await asyncio.sleep(2)  # Simulate API call
                _save_changes_btn.props(remove="disable loading")
                ui.notify(
                    f"Stock for '{title.value}' updated successfully!", color="positive"
                )
                # Note: Fields are not cleared on an edit page.

            # --- Action Buttons ---
            _save_changes_btn = (
                ui.button("Save Changes", on_click=save_changes)
                .classes(
                    "mt-6 bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 px-6 rounded-xl shadow-md w-full"
                )
                .props("color=teal")
            )

            ui.button(
                "Cancel", on_click=lambda: ui.navigate.to("/pharmacydashboard")
            ).classes(
                "mt-6 bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 px-6 rounded-xl shadow-md w-full"
            ).props(
                "color=teal"
            )


# ui.run()
