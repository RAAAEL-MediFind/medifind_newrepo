from nicegui import ui
from components.footer import show_footer
from components.navbar import show_navbar


@ui.page("/contact")
def contact_page():
    show_navbar()

    with ui.column().classes(
        "w-screen bg-[#f8fafc] text-gray-700 items-center px-4 md:px-0"
    ):

        # 🔹 Header Section
        with ui.column().classes(
            "items-center text-center py-20 text-white w-full md:max-w-6xl"
        ).style(
            "background: linear-gradient(90deg, #00b6c7, #02c3b8); border-radius: 16px;"
        ):
            ui.label("Contact MediFind").classes("text-4xl md:text-5xl font-bold mb-3")
            ui.label(
                "We’re here to help you locate trusted medicines across Ghana."
            ).classes("text-lg md:text-xl opacity-90")

        # 🔹 Contact Information Cards
        with ui.row().classes(
            "justify-center mt-16 gap-8 flex-wrap px-6 md:px-20 w-full md:max-w-6xl"
        ):
            info_cards = [
                ("📍", "Our Office", "Accra, Ghana"),
                ("📞", "Phone", "+233 20 123 4567"),
                ("✉️", "Email", "support@medifind.com"),
            ]
            for icon, title, detail in info_cards:
                with ui.card().classes(
                    "w-72 md:w-80 bg-white shadow-md rounded-2xl p-6 text-center hover:shadow-xl transition"
                ):
                    ui.label(icon).classes("text-4xl mb-3 text-cyan-500")
                    ui.label(title).classes("text-lg font-semibold text-gray-800")
                    ui.label(detail).classes("text-sm text-gray-500")

        # 🔹 Contact Form Section
        with ui.element("section").classes(
            "mt-20 mb-20 bg-white rounded-2xl shadow-lg p-8 md:p-14 w-full max-w-6xl"
        ):
            ui.label("Send Us a Message").classes(
                "text-2xl md:text-3xl font-semibold text-gray-800 mb-8 text-center"
            )

            # ✅ Form Inputs - full width on mobile, same row on desktop
            with ui.row().classes("flex flex-col md:flex-row gap-6 w-full"):
                name = ui.input(
                    label="Your Name", placeholder="Enter your name"
                ).classes(
                    "w-full md:flex-1 bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-400 h-14"
                )

                email = ui.input(
                    label="Your Email", placeholder="Enter your email"
                ).classes(
                    "w-full md:flex-1 bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-400 h-14"
                )

                subject = ui.input(
                    label="Subject", placeholder="Enter subject"
                ).classes(
                    "w-full md:flex-1 bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-400 h-14"
                )

            # ✅ Message box - full width and consistent visual design
            message = ui.textarea(
                label="Your Message", placeholder="Type your message..."
            ).classes(
                "w-full mt-6 bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-400 h-40"
            )

            def submit():
                if not name.value or not email.value or not message.value:
                    ui.notify("Please fill in all fields", color="red")
                else:
                    ui.notify(
                        f"Thanks {name.value}, we’ll get back to you soon!",
                        color="green",
                    )
                    name.value = email.value = subject.value = message.value = ""

            ui.button("Send Message", on_click=submit).classes(
                "text-white font-semibold px-8 py-3 rounded-xl hover:opacity-90 transition mt-8 mx-auto block"
            ).props("color=teal-600")

        show_footer()
