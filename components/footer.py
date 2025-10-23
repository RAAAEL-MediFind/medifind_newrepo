from nicegui import ui, app


def show_footer():
    with ui.element("footer").classes(
        " bg-[#34989e] text-gray-400 w-full mt-16 px-8 py-10"
    ):
        with ui.element("div").classes(
            "max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8"
        ):

            # 🔹 About Section
            with ui.column().classes("space-y-3"):
                ui.label("About MediFind").classes("text-lg font-semibold text-white")
                ui.label(
                    "MediFind helps you locate medicines from verified pharmacies across Ghana — quickly, safely, and reliably."
                ).classes("text-sm leading-relaxed text-blue-50")

                # Social Icons
                with ui.row().classes("gap-4 mt-3"):
                    for icon, link in [
                        ("facebook", "#"),
                        ("instagram", "#"),
                        ("twitter", "#"),
                        ("linkedin", "#"),
                    ]:
                        ui.link("", link, new_tab=True).classes(
                            "hover:opacity-80 transition"
                        ).props(f"icon={icon}")

            # 🔹 Quick Links Section
            with ui.column().classes("space-y-3"):
                ui.label("Quick Links").classes("text-lg font-semibold text-white")
                with ui.column().classes("no-underline"):
                    for name, link in [
                        ("Home", "/"),
                        ("Find Medicine", "/shop"),
                        ("Login", "/signin"),
                        ("Sign Up", "/signup"),
                    ]:
                        ui.link(name, link).classes(
                            "text-sm text-blue-50 hover:text-white transition no-underline"
                        )

            # 🔹 Contact Section
            with ui.column().classes("space-y-3"):
                ui.label("Contact Us").classes("text-lg font-semibold text-white")
                ui.label("📍 Accra, Ghana").classes("text-sm text-blue-50")
                ui.label("📞 +233 20 123 4567").classes("text-sm text-blue-50")
                ui.label("✉️ support@medifind.com").classes("text-sm text-blue-50")

        # 🔹 Footer Bottom
        with ui.row().classes("justify-center mt-8 border-t border-blue-200 pt-4"):
            ui.label("© 2025 MediFind. All rights reserved.").classes(
                "text-xs text-blue-50"
            )
