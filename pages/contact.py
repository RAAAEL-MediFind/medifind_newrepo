from nicegui import ui
from components.footer import show_footer
from components.navbar import show_navbar


@ui.page("/contact")
def contact_page():
    show_navbar()
    with ui.column().classes("w-screen bg-[#f8fafc] text-gray-700"):
        # 🔹 Header Section
        with ui.column().classes(
            "items-center text-center py-20text-white ml-80"
        ).props("color=teal-600"):
            ui.label("Contact MediFind").classes("text-4xl font-bold mb-2")
            ui.label(
                "We’re here to help you locate trusted medicines across Ghana."
            ).classes("text-lg opacity-90")

        # 🔹 Contact Information Cards
        with ui.row().classes(
            "justify-center mt-12 gap-8 flex-wrap px-6 items-center ml-60"
        ):
            info_cards = [
                ("📍", "Our Office", "Accra, Ghana"),
                ("📞", "Phone", "+233 20 123 4567"),
                ("✉️", "Email", "support@medifind.com"),
            ]
            for icon, title, detail in info_cards:
                with ui.card().classes(
                    "w-72 bg-gradient shadow-md rounded-2xl p-6 text-center hover:shadow-xl transition"
                ):
                    ui.label(icon).classes("text-4xl mb-3 text-cyan-500")
                    ui.label(title).classes("text-lg font-semibold text-gray-800")
                    ui.label(detail).classes("text-sm text-gray-500")

        # 🔹 Contact Form
        with ui.element("section").classes(
            "max-w-3xl mx-auto mt-16 bg-white rounded-2xl shadow-md p-10 w-full"
        ):
            ui.label("Send Us a Message").classes(
                "text-2xl font-semibold text-gray-800 mb-6 text-center"
            )
            with ui.column().classes("space-y-4"):
                name = ui.input(
                    label="Your Name", placeholder="Enter your name"
                ).classes(
                    "w-full bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-400"
                )
                email = ui.input(
                    label="Your Email", placeholder="Enter your email"
                ).classes(
                    "w-full bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-400"
                )
                message = ui.textarea(
                    label="Your Message", placeholder="Type your message..."
                ).classes(
                    "w-full bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-400 h-32"
                )

                def submit():
                    if not name.value or not email.value or not message.value:
                        ui.notify("Please fill in all fields", color="red")
                    else:
                        ui.notify(
                            f"Thanks {name.value}, we’ll get back to you soon!",
                            color="green",
                        )
                        name.value = email.value = message.value = ""

                ui.button("Send Message", on_click=submit).classes(
                    "text-white font-semibold px-6 py-3 rounded-xl hover:opacity-90 transition"
                ).props("color=teal-600")

        with ui.column().classes("mt-16 px-6 pb-20 items-center"):
            ui.label("Find Us on the Map").classes(
                "text-2xl font-semibold text-gray-800 mb-6"
            )

        show_footer()
