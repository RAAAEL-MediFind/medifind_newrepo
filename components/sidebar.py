from nicegui import ui, app


def show_sidebar():
    """User Dashboard Sidebar (Styled exactly like the Pharmacy Dashboard Sidebar)"""

    async def logout():
        """Clears user session and redirects to sign-in page."""
        app.storage.user.clear()
        ui.notify("You have been successfully logged out.", color="positive")
        ui.navigate.to("/signin")

    with ui.left_drawer().classes("bg-white w-64 shadow-md text-gray-800"):
        with ui.column().classes("p-4 gap-y-2 h-full"):

            # Sidebar menu items (matching pharmacy layout)
            primary_links = [
                ("Dashboard", "/userdashboard", "dashboard"),
                ("Find Medicine", "/shop", "medication"),
                ("Sent Messages", "/sent_messages", "mail"),
            ]

            # Each row styled exactly like pharmacy sidebar
            for label, route, icon_name in primary_links:
                with ui.row().classes(
                    "w-full items-center gap-4 px-3 py-2 rounded-lg hover:bg-[#d6eef0] "
                    "cursor-pointer transition-all duration-200"
                ).on("click", lambda r=route: ui.navigate.to(r)):
                    ui.icon(icon_name).classes("text-[#34989e] text-xl")
                    ui.label(label).classes("text-base font-medium text-gray-700")

            # Divider line
            ui.separator().classes("my-4")

            # Account section label
            ui.label("ACCOUNT").classes(
                "text-xs font-semibold text-gray-500 uppercase px-3"
            )

            # Settings option
            with ui.row().classes(
                "items-center gap-4 px-3 py-2 rounded-lg hover:bg-[#d6eef0] cursor-pointer"
            ).on("click", lambda: ui.navigate.to("/settings")):
                ui.icon("settings").classes("text-[#34989e] text-xl")
                ui.label("Settings").classes("text-base font-medium text-gray-700")

            # Spacer pushes logout button to bottom
            ui.space()

            # Logout button — same red gradient and rounded corners
            ui.button("Logout", icon="logout", on_click=logout).classes(
                "w-full bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl "
                "py-2.5 shadow-md hover:from-red-600 hover:to-red-700"
            ).props("color=teal600")
