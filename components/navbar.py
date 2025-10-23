from nicegui import ui, app


def show_navbar():

    async def logout():
        """Clear the user's session data and redirect to the sign-in page."""
        app.storage.user.clear()
        ui.notify("You have been successfully logged out.")
        ui.navigate.to("/signin")

    with ui.header().classes("bg-[#34989e] text-white p-0"):
        with ui.row().classes("w-full items-center justify-between p-4"):

            # Left side: Logo and Navigation
            with ui.row().classes("items-center gap-4"):
                ui.label("MediFind").classes("text-3xl font-bold")
                ui.link("Home", target="/").classes(
                    "text-white font-semibold p-2 no-underline"
                )
                ui.link("Shop +", target="/shop").classes(
                    "text-white font-semibold p-2 no-underline"
                )

            # Right side: Conditional User Actions
            with ui.row().classes("items-center gap-4"):
                # Check if the user is logged in
                if app.storage.user.get("access_token"):
                    # --- Show these buttons if LOGGED IN ---

                    # Determine the dashboard path based on the user's role
                    role = app.storage.user.get("role")
                    if role == "pharmacy":
                        dashboard_path = "/pharmacydashboard"
                    else:
                        dashboard_path = "/userdashboard"

                    # Dashboard Button with dynamic navigation
                    ui.button(
                        "Dashboard", on_click=lambda: ui.navigate.to(dashboard_path)
                    ).classes(
                        "text-white font-bold text-sm px-4 py-1.5 rounded-full shadow-md "
                        "hover:bg-gray-200 transition-colors duration-200"
                    ).props(
                        "color=teal-600"
                    )

                else:
                    # --- Show these links if LOGGED OUT ---
                    ui.link("SIGN IN", target="/signin").classes(
                        "text-white font-semibold no-underline"
                    )
                    ui.link("SIGN UP", target="/signup").classes(
                        "text-white font-semibold no-underline"
                    )

                # These icons are always visible
                ui.icon("favorite_border", size="md").classes(
                    "hover:text-red-400 cursor-pointer"
                )
                with ui.row().classes("items-center"):
                    ui.icon("shopping_cart", size="md").classes("cursor-pointer")
