from nicegui import ui
from components.footer import show_footer
from components.navbar import show_navbar


@ui.page("/contact")
def contact_page():
    show_navbar()
    with ui.column().classes("w-screen bg-[#f8fafc] text-gray-700 overflow-x-hidden"):
        # 🔹 Header Section
        with ui.column().classes(
            "items-center text-center py-20 text-white px-6 md:px-0"
        ).style("background: linear-gradient(90deg, #11cdef, #0fbad4);"):
            ui.label("Contact MediFind").classes("text-3xl md:text-5xl font-bold mb-3")
            ui.label(
                "We’re here to help you locate trusted medicines across Ghana."
            ).classes("text-base md:text-lg opacity-90 max-w-2xl")

        # 🔹 Contact Information Cards
        with ui.row().classes(
            "justify-center mt-12 gap-6 flex-wrap px-4 md:px-12 items-center"
        ):
            info_cards = [
                ("📍", "Our Office", "Accra, Ghana"),
                ("📞", "Phone", "+233 20 123 4567"),
                ("✉️", "Email", "support@medifind.com"),
            ]
            for icon, title, detail in info_cards:
                with ui.card().classes(
                    "w-72 md:w-80 bg-white shadow-md rounded-2xl p-6 text-center "
                    "hover:shadow-xl transition-all duration-300"
                ):
                    ui.label(icon).classes("text-4xl mb-3 text-cyan-500")
                    ui.label(title).classes("text-lg font-semibold text-gray-800")
                    ui.label(detail).classes("text-sm text-gray-500")

        # 🔹 Contact Form Section (Responsive)
        with ui.row().classes(
            "flex-col md:flex-row justify-center items-start mt-16 gap-10 px-6 md:px-20"
        ):
            # 🧭 Left Side: Text / Illustration (only shows on desktop)
            with ui.column().classes(
                "hidden md:flex w-full md:w-1/2 items-center justify-center"
            ):
                ui.icon("support_agent").classes("text-8xl text-cyan-500 mb-4")
                ui.label("We value your feedback!").classes(
                    "text-2xl font-semibold text-gray-800 mb-2"
                )
                ui.label(
                    "Reach out to us with your questions or suggestions and we’ll respond promptly."
                ).classes("text-gray-600 text-center px-6")

            # 🧾 Right Side: Form
            with ui.element("section").classes(
                "bg-white rounded-2xl shadow-md p-8 md:p-10 w-full md:w-1/2"
            ):
                ui.label("Send Us a Message").classes(
                    "text-2xl font-semibold text-gray-800 mb-6 text-center"
                )
                with ui.column().classes("space-y-4"):
                    name = ui.input(
                        label="Your Name", placeholder="Enter your name"
                    ).classes(
                        "w-full bg-gray-50 border border-gray-300 rounded-xl "
                        "focus:ring-2 focus:ring-cyan-400"
                    )
                    email = ui.input(
                        label="Your Email", placeholder="Enter your email"
                    ).classes(
                        "w-full bg-gray-50 border border-gray-300 rounded-xl "
                        "focus:ring-2 focus:ring-cyan-400"
                    )
                    message = ui.textarea(
                        label="Your Message", placeholder="Type your message..."
                    ).classes(
                        "w-full bg-gray-50 border border-gray-300 rounded-xl "
                        "focus:ring-2 focus:ring-cyan-400 h-32"
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
                        "text-white font-semibold px-6 py-3 rounded-xl hover:opacity-90 transition-all duration-300"
                    ).props("color=teal-600")

        show_footer()
