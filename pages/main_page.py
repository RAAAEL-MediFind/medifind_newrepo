from nicegui import ui, app
import requests
import asyncio
from utils.api import base_url  # Make sure base_url is defined in this file

# Define styles for clarity
GRADIENT_STYLE = "background: linear-gradient(180deg, #00a7b1, #02c3b8);"
WHITE_SECTION_STYLE = "background-color: white; color: #333;"


@ui.page("/")
def show_main_page():

    ui.add_head_html(
        """
    <style>
    @keyframes floatLeaf {
        0% { transform: translateY(0) rotate(0deg); opacity: 0.8; }
        50% { transform: translateY(-30px) rotate(45deg); opacity: 1; }
        100% { transform: translateY(0) rotate(90deg); opacity: 0.8; }
    }
    .device-transition { transition: transform 0.4s ease; }
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
    ui.add_head_html(
        """
<style>
/* --- General Responsive Rules --- */
@media (max-width: 768px) {

    /* Navbar compact and centered */
    .navbar {
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 8px !important;
        gap: 6px !important;
        text-align: center !important;
    }

    .navbar img {
        width: 100px !important;
        height: auto !important;
    }

    .navbar button {
        font-size: 0.8rem !important;
        padding: 0.4rem 0.8rem !important;
        width: auto !important;
    }

    /* Hero text smaller, tighter spacing */
    .hero-text {
        font-size: 1.1rem !important;
        line-height: 1.2 !important;
        margin: 0.5rem auto !important;
        text-align: center !important;
        max-width: 95% !important;
    }

    /* Hero image smaller */
    .hero-image {
        width: 60% !important;
        max-width: 220px !important;
        margin: 0.5rem auto !important;
        display: block !important;
    }

    /* All grid/column sections adjust for mobile */
    .grid, .columns, .cards, .ui-row {
        display: grid !important;
        grid-template-columns: 1fr !important;
        gap: 0.6rem !important;
        align-items: center !important;
        justify-items: center !important;
        padding: 0.5rem !important;
    }

    /* Cards smaller and aligned */
    .card, .pharmacy-card {
        width: 90% !important;
        max-width: 300px !important;
        margin: auto !important;
        padding: 0.6rem !important;
        border-radius: 10px !important;
    }

    /* Images inside cards smaller */
    .card img, .pharmacy-card img {
        width: 60px !important;
        height: auto !important;
        margin: 0 auto !important;
        display: block !important;
    }

    /* Text inside cards */
    .card h3, .pharmacy-card h3 {
        font-size: 1rem !important;
        text-align: center !important;
        margin-top: 0.4rem !important;
    }

    /* Floating decorative leaves smaller */
    .floating-leaf {
        width: 18px !important;
        opacity: 0.6 !important;
    }

    /* Reduce vertical space globally */
    .page-section {
        margin: 0 !important;
        padding: 0.5rem 0 !important;
    }
}
</style>
"""
    )

    ui.add_head_html(
        """
    <style>
    @keyframes floatLeaf {
        0% { transform: translateY(0) rotate(0deg); opacity: 0.8; }
        50% { transform: translateY(-30px) rotate(45deg); opacity: 1; }
        100% { transform: translateY(0) rotate(90deg); opacity: 0.8; }
    }
    .device-transition { transition: transform 0.4s ease; }

    /* =======================
       📱 MOBILE VIEW STYLES
       ======================= */
    @media (max-width: 768px) {
        /* Make hero section vertical and centered */
        .w-screen.relative.pt-24 {
            padding-top: 5rem !important;
            text-align: center !important;
        }

        .w-full.-mt-20 {
            flex-direction: column !important;
            align-items: center !important;
            gap: 1rem !important;
        }

        /* Logo smaller */
        .w-\\[150px\\].md\\:w-\\[250px\\] {
            width: 120px !important;
            height: auto !important;
        }

        /* Purchase button centered */
        .text-white.text-bold.items-end.md\\:block.md\\:ml-\\[800px\\] {
            margin: 1rem auto !important;
            display: block !important;
            font-size: 0.9rem !important;
        }

        /* Hero text smaller and centered */
        .font-extrabold.leading-tight.mb-8.text-3xl.md\\:text-\\[3rem\\].text-white {
            font-size: 1.7rem !important;
            line-height: 2.2rem !important;
            text-align: center !important;
        }

        /* Image scaling */
        .w-\\[1000px\\].md\\:w-\\[800px\\] {
            width: 100% !important;
            max-width: 320px !important;
            margin: 0 auto !important;
        }

        /* Grid: show one card per row */
        .grid-cols-1.sm\\:grid-cols-2.lg\\:grid-cols-3 {
            grid-template-columns: 1fr !important;
        }

        /* Card responsiveness */
        .w-80 {
            width: 90% !important;
            margin: 0 auto !important;
        }

        /* Pharmacy label */
        .text-3xl.font-bold.text-gray-800.mb-8 {
            font-size: 1.8rem !important;
            text-align: center !important;
        }
    }

    /* =======================
       💻 DESKTOP VIEW STYLES
       ======================= */
    @media (min-width: 769px) {
        .font-extrabold.leading-tight.mb-8.text-3xl.md\\:text-\\[3rem\\].text-white {
            font-size: 3rem !important;
            text-align: left !important;
        }

        .w-\\[1000px\\].md\\:w-\\[800px\\] {
            max-width: 800px !important;
        }

        .grid-cols-1.sm\\:grid-cols-2.lg\\:grid-cols-3 {
            grid-template-columns: repeat(3, 1fr) !important;
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

    # --- Hero Section ---
    with ui.column().classes("w-screen relative pt-24").style(GRADIENT_STYLE):
        with ui.row().classes("items-center w-full -mt-20").style(
            f"display: flex; top: 0; z-index: 100; {GRADIENT_STYLE}"
        ):
            ui.image("assets/medilogo.png").classes(
                "items-center w-[150px] md:w-[250px] h-[75px] md:h-[100px] mt-0 "
            )
            ui.button(
                "PURCHASE ITEM", on_click=lambda: ui.navigate.to("/shop")
            ).classes("text-white text-bold items-end md:block md:ml-[800px]").style(
                "border-radius: 25px; padding: 0.6rem 1.5rem; cursor: pointer; transition: 0.3s ease;"
            ).props(
                "color=#11cdef"
            )

        with ui.grid().classes("w-full grid-cols-1 md:grid-cols-2"):
            with ui.column().classes(
                " items-center px-4 md:px-24 pb-12 md:pb-20 text-center md:text-left z-10 mt-40"
            ):
                ui.label("Because the right Care shouldn't be hard to find").classes(
                    "font-extrabold leading-tight mb-8 text-3xl md:text-[3rem] text-white"
                )
                ui.image("assets/h1-slider04 (1).png").classes(
                    "w-[200px] mx-auto md:mx-0"
                )

            with ui.column().classes(
                "w-full flex flex-col md:flex-row items-center md:items-end justify-center gap-4 md:gap-8"
            ):
                ui.image("assets/photo_med-removebg-preview.png").classes(
                    "w-[1000px] md:w-[800px] border-rounded device-transition "
                )

                ui.image("").classes(
                    "w-1/5 md:w-[300px] device-img-small device-transition md:ml-80 md:-mt-80"
                )

        ui.image("assets/ldp-leaf-03 (1).png").classes("absolute w-[40px]").style(
            "top:20%; left:10%; animation-delay:2s; opacity: 0.8; animation: floatLeaf 10s linear infinite;"
        )
        ui.image("assets/ldp-leaf-03 (1).png").classes("absolute w-[40px]").style(
            "top:30%; left:60%; animation-delay:4s; opacity: 0.8; animation: floatLeaf 10s linear infinite;"
        )
        ui.image("assets/ldp-leaf-03 (1).png").classes("absolute w-[40px]").style(
            "top:80%; left:80%; animation-delay:6s; opacity: 0.8; animation: floatLeaf 10s linear infinite;"
        )
    # --- End Hero Section ---

    # --- Pharmacy Grid Section ---
    with ui.column().classes("w-full items-center py-10 px-4").style(
        WHITE_SECTION_STYLE
    ):
        ui.label("Find a Pharmacy Near You").classes(
            "text-3xl font-bold text-gray-800 mb-8"
        )
        # Grid layout for the cards
        pharmacy_grid = ui.grid().classes(
            "w-full max-w-7xl justify-center gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
        )

    # --- API Integration to Fetch and Display Pharmacies ---
    async def fetch_and_display_pharmacies():
        """Fetches all pharmacies from the backend and populates the grid."""
        endpoint_url = f"{base_url}/public/pharmacies/all"
        try:
            # Add loading indicator
            pharmacy_grid.clear()
            with pharmacy_grid:
                with ui.column().classes("col-span-full items-center mt-8"):
                    ui.spinner(size="lg")
                    ui.label("Loading pharmacies...").classes("text-gray-500")

            response = await asyncio.to_thread(requests.get, endpoint_url, timeout=20)

            pharmacy_grid.clear()  # Clear loading indicator
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
                        # --- MODIFIED: Extract address, remove phone/email ---
                        name = pharmacy.get("pharmacy_name", "Unknown Pharmacy")
                        pharmacy_id = pharmacy.get("id")
                        flyer_url = pharmacy.get("flyer")
                        address = pharmacy.get(
                            "digital_address", "No address"
                        )  # Get address

                        image_source = flyer_url or "assets/landing_home11.jpg"

                        if not pharmacy_id:
                            continue

                        # --- Styled Card (Similar to shop.py) ---
                        with ui.card().classes(
                            "w-80 rounded-2xl shadow-md hover:shadow-lg transition p-4 flex flex-col justify-between h-full cursor-pointer"
                        ).on(
                            "click",
                            lambda pid=pharmacy_id: ui.navigate.to(f"/pharmacy/{pid}"),
                        ):

                            # Image container
                            with ui.element("div").classes(
                                "w-full h-48 rounded-xl overflow-hidden mb-3"
                            ):
                                ui.image(image_source).classes(
                                    "w-full h-full object-cover"
                                )

                            # --- MODIFIED: Pharmacy Info ---
                            with ui.column().classes(
                                "mt-1 text-center w-full flex-grow"
                            ):
                                ui.label(name).classes(
                                    "font-semibold text-gray-800 text-lg mb-2"
                                )  # Pharmacy Name
                                # Display Address instead of phone/email
                                with ui.row().classes(
                                    "items-center justify-center text-sm text-gray-600 mb-1 w-full"
                                ):
                                    ui.icon("location_on", size="xs").classes(
                                        "mr-1"
                                    )  # Location icon
                                    ui.label(address)  # Display address

                            # Optional: View Details indicator
                            with ui.row().classes("justify-center mt-3 w-full"):
                                ui.label("View Details").classes(
                                    "text-xs text-blue-500"
                                )

                else:  # Handle API error
                    ui.label(
                        f"Error loading pharmacies ({response.status_code})"
                    ).classes("col-span-full text-center text-red-500")

        except requests.RequestException as e:  # Handle connection error
            pharmacy_grid.clear()
            with pharmacy_grid:
                ui.label(f"Connection Error: {e}").classes(
                    "col-span-full text-center text-red-500"
                )
        except Exception as e:  # Catch other potential errors
            pharmacy_grid.clear()
            with pharmacy_grid:
                ui.label(f"An unexpected error occurred: {e}").classes(
                    "col-span-full text-center text-red-500"
                )

    # Use a timer to run the async function on page load
    ui.timer(0.1, fetch_and_display_pharmacies, once=True)
