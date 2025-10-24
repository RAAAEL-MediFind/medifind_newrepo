from nicegui import ui, app
import requests
import asyncio
from utils.api import base_url  # Make sure base_url is defined in this file

# Define styles for clarity
GRADIENT_STYLE = "background: linear-gradient(180deg, #00a7b1, #02c3b8);"
WHITE_SECTION_STYLE = "background-color: white; color: #333;"


@ui.page("/")
def show_main_page():

    # --- HEAD HTML STYLES AND JS ---
    ui.add_head_html(
        """
    <style>
    @keyframes floatLeaf {
        0% { transform: translateY(0) rotate(0deg); opacity: 0.8; }
        50% { transform: translateY(-30px) rotate(45deg); opacity: 1; }
        100% { transform: translateY(0) rotate(90deg); opacity: 0.8; }
    }
    .device-transition { transition: transform 0.4s ease; }

    /* ✅ Responsive Adjustments */
    @media (max-width: 768px) {
        /* Navbar layout: logo + purchase button side by side */
        .navbar-row {
            flex-direction: row !important;
            justify-content: center !important;
            align-items: center !important;
            gap: 12px !important;
        }

        .navbar-row img {
            width: 120px !important;
            height: auto !important;
        }

        .navbar-row button {
            font-size: 0.85rem !important;
            padding: 0.5rem 1rem !important;
        }

        /* Hero text smaller */
        .hero-text {
            font-size: 1.6rem !important;
            text-align: center !important;
            margin: 1rem auto !important;
        }

        /* Hide right-side hero image on mobile */
        .hero-right-img {
            display: none !important;
        }

        /* Adjust grid for mobile */
        .grid-cols-1.sm\\:grid-cols-2.lg\\:grid-cols-3 {
            grid-template-columns: 1fr !important;
        }

        /* Card resizing */
        .w-80 {
            width: 90% !important;
            margin: 0 auto !important;
        }
    }

    @media (min-width: 769px) {
        /* Show right-side hero image on desktop */
        .hero-right-img {
            display: block !important;
        }
    }
    </style>
    <script>
    document.addEventListener("mousemove", (e) => {
        document.querySelectorAll(".device-img, .device-img-small").forEach((el) => {
            const speed = 0.05;
            const x = (window.innerWidth - e.pageX * speed) / 100;
            const y = (window.innerHeight - e.pageY * speed) / 100;
            el.style.transform = `translate(${x}px, ${y}px)`;
        });
    });
    </script>
    """
    )

    # --- HERO SECTION ---
    with ui.column().classes("w-screen relative pt-12").style(GRADIENT_STYLE):
        # ✅ Logo + Purchase Button side by side (works on mobile and desktop)
        with ui.row().classes(
            "items-center justify-between w-full px-6 md:px-20 navbar-row"
        ).style(f"{GRADIENT_STYLE}"):
            ui.image("assets/medilogo.png").classes(
                "w-[150px] md:w-[250px] h-[75px] md:h-[100px]"
            )
            ui.button(
                "PURCHASE ITEM", on_click=lambda: ui.navigate.to("/shop")
            ).classes(
                "text-white text-bold rounded-full px-6 py-2 hover:opacity-90 transition"
            ).props(
                "color=#11cdef"
            )

        # ✅ Hero content with responsive layout
        with ui.grid().classes(
            "w-full grid-cols-1 md:grid-cols-2 items-center mt-12 px-6 md:px-20"
        ):
            # Left text + image (small)
            with ui.column().classes(
                "items-center md:items-start text-center md:text-left space-y-4"
            ):
                ui.label("Because the right Care shouldn't be hard to find").classes(
                    "font-extrabold leading-tight text-3xl md:text-[3rem] text-white hero-text"
                )
                ui.image("assets/h1-slider04 (1).png").classes(
                    "w-[200px] mx-auto md:mx-0"
                )

            # Right large image (hidden on mobile)
            ui.image("assets/photo_med-removebg-preview.png").classes(
                "w-[1000px] md:w-[800px] border-rounded device-transition hero-right-img"
            )

        # Floating leaves (kept same)
        ui.image("assets/ldp-leaf-03 (1).png").classes("absolute w-[40px]").style(
            "top:20%; left:10%; animation-delay:2s; opacity:0.8; animation: floatLeaf 10s linear infinite;"
        )
        ui.image("assets/ldp-leaf-03 (1).png").classes("absolute w-[40px]").style(
            "top:30%; left:60%; animation-delay:4s; opacity:0.8; animation: floatLeaf 10s linear infinite;"
        )
        ui.image("assets/ldp-leaf-03 (1).png").classes("absolute w-[40px]").style(
            "top:80%; left:80%; animation-delay:6s; opacity:0.8; animation: floatLeaf 10s linear infinite;"
        )

    # --- PHARMACY GRID SECTION ---
    with ui.column().classes("w-full items-center py-10 px-4").style(
        WHITE_SECTION_STYLE
    ):
        ui.label("Find a Pharmacy Near You").classes(
            "text-3xl font-bold text-gray-800 mb-8"
        )

        pharmacy_grid = ui.grid().classes(
            "w-full max-w-7xl justify-center gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
        )

    # --- API INTEGRATION ---
    async def fetch_and_display_pharmacies():
        endpoint_url = f"{base_url}/public/pharmacies/all"
        try:
            pharmacy_grid.clear()
            with pharmacy_grid:
                with ui.column().classes("col-span-full items-center mt-8"):
                    ui.spinner(size="lg")
                    ui.label("Loading pharmacies...").classes("text-gray-500")

            response = await asyncio.to_thread(requests.get, endpoint_url, timeout=20)
            pharmacy_grid.clear()
            with pharmacy_grid:
                if response.status_code == 200:
                    response_data = response.json()
                    pharmacies_list = response_data.get("data", [])
                    if not pharmacies_list:
                        ui.label("No pharmacies found.").classes(
                            "col-span-full text-center text-gray-500"
                        )
                        return

                    for pharmacy in pharmacies_list:
                        name = pharmacy.get("pharmacy_name", "Unknown Pharmacy")
                        pharmacy_id = pharmacy.get("id")
                        flyer_url = pharmacy.get("flyer")
                        address = pharmacy.get("digital_address", "No address")
                        image_source = flyer_url or "assets/landing_home11.jpg"

                        if not pharmacy_id:
                            continue

                        with ui.card().classes(
                            "w-80 rounded-2xl shadow-md hover:shadow-lg transition p-4 flex flex-col justify-between h-full cursor-pointer"
                        ).on(
                            "click",
                            lambda pid=pharmacy_id: ui.navigate.to(f"/pharmacy/{pid}"),
                        ):
                            with ui.element("div").classes(
                                "w-full h-48 rounded-xl overflow-hidden mb-3"
                            ):
                                ui.image(image_source).classes(
                                    "w-full h-full object-cover"
                                )

                            with ui.column().classes(
                                "mt-1 text-center w-full flex-grow"
                            ):
                                ui.label(name).classes(
                                    "font-semibold text-gray-800 text-lg mb-2"
                                )
                                with ui.row().classes(
                                    "items-center justify-center text-sm text-gray-600 mb-1 w-full"
                                ):
                                    ui.icon("location_on", size="xs").classes("mr-1")
                                    ui.label(address)

                            with ui.row().classes("justify-center mt-3 w-full"):
                                ui.label("View Details").classes(
                                    "text-xs text-blue-500"
                                )

                else:
                    ui.label(
                        f"Error loading pharmacies ({response.status_code})"
                    ).classes("col-span-full text-center text-red-500")
        except requests.RequestException as e:
            pharmacy_grid.clear()
            with pharmacy_grid:
                ui.label(f"Connection Error: {e}").classes(
                    "col-span-full text-center text-red-500"
                )
        except Exception as e:
            pharmacy_grid.clear()
            with pharmacy_grid:
                ui.label(f"An unexpected error occurred: {e}").classes(
                    "col-span-full text-center text-red-500"
                )

    ui.timer(0.1, fetch_and_display_pharmacies, once=True)
