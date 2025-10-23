from nicegui import ui, app
import requests
import asyncio
from utils.api import base_url  # Make sure base_url is defined in this file


@ui.page("/signin")
def show_signin_page():

    ui.add_head_html(
        """
    <style>
    @keyframes dissolve {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.2; }
    }
    .dissolve-animation {
      animation: dissolve 5s ease-in-out infinite;
    }

    /* --- Responsive Layout Styles --- */

    /* Mobile view */
    @media (max-width: 768px) {
      .signin-grid {
        display: flex;
        flex-direction: column;
        height: auto;
      }

      .signin-left {
        display: none; /* hide background image section on mobile */
      }

      .signin-right {
        width: 100%;
        padding: 2rem 1rem;
        justify-content: center;
        align-items: center;
      }

      .signin-form {
        width: 100% !important;
      }

      .signin-header img {
        width: 180px !important;
        height: auto !important;
      }

      .signin-header label {
        text-align: center;
      }

      .role-card {
        width: 45% !important;
        height: 100px !important;
      }
    }

    /* Desktop view */
    @media (min-width: 769px) {
      .signin-grid {
        grid-template-columns: repeat(2, 1fr);
      }

      .signin-left {
        display: flex;
      }

      .signin-right {
        display: flex;
      }
    }
    </style>
    """
    )

    with ui.grid(columns=2).classes("w-full min-h-screen signin-grid"):

        # Left side with background image and welcome message
        with ui.column().classes(
            "w-full bg-cover bg-no-repeat bg-center relative signin-left"
        ).style("background-image:url(/assets/signin4.png)"):
            with ui.column().classes(
                "absolute inset-0 bg-black/60 flex items-center justify-center"
            ):
                with ui.column().classes("text-center items-center max-w-sm"):
                    ui.label("Welcome Back").classes(
                        "text-white font-extrabold text-4xl dissolve-animation"
                    )
                    ui.label(
                        "Don't have an account? Sign up to stay connected."
                    ).classes("text-white text-lg dissolve-animation")
                    ui.element("div").classes("h-8")
                    ui.button(
                        "SIGN UP", on_click=lambda: ui.navigate.to("/signup")
                    ).classes("text-white font-semibold px-8 py-2 rounded-full").props(
                        "color=teal-600"
                    )

        # Right side with the sign-in form
        with ui.column().classes(
            "w-full flex items-center justify-start pt-20 bg-white signin-right"
        ):
            with ui.column().classes("w-[500px] px-8 signin-form"):
                with ui.column().classes("w-full items-center mb-8 signin-header"):
                    ui.label("MEDIFIND").classes("text-5xl font-bold text-blue").style(
                        "letter-spacing: 0.1em"
                    )
                    ui.image("assets/signuplog.png").classes(
                        "items-center w-[250px] h-[100px] mt-0 "
                    )
                    ui.label(
                        "...because the right care shouldn't be hard to find"
                    ).classes("text-sm font-normal text-gray-500 mt-1 tracking-wide")

                ui.label("SIGN IN").classes(
                    "text-2xl font-bold mt-4 mb-2 text-gray-800"
                )
                ui.label("Choose your role:").classes(
                    "text-md font-semibold text-gray-600 mb-4"
                )

                # Role selection cards
                with ui.row().classes("w-full justify-start gap-4 mb-6"):
                    user_button = ui.card().classes(
                        "w-32 h-24 flex flex-col items-center justify-center cursor-pointer border-2 border-gray-200 rounded-lg transition-all hover:border-blue-300 hover:shadow-lg role-card"
                    )
                    with user_button:
                        user_icon = ui.icon("person_outline", size="0.5").classes(
                            "text-gray-500"
                        )
                        user_label = ui.label("Patient").classes(
                            "text-gray-500 font-semibold"
                        )

                    pharmacy_button = ui.card().classes(
                        "w-32 h-24 flex flex-col items-center justify-center cursor-pointer border-2 border-gray-200 rounded-lg transition-all hover:border-blue-300 hover:shadow-lg role-card"
                    )
                    with pharmacy_button:
                        pharmacy_icon = ui.icon("medical_services", size="0.5").classes(
                            "text-gray-500"
                        )
                        pharmacy_label = ui.label("Pharmacy").classes(
                            "text-gray-500 font-semibold"
                        )

                # Container for the dynamic sign-in forms
                with ui.column().classes("w-full relative h-[400px]"):
                    # User Sign-in Form (initially hidden)
                    with ui.column().classes(
                        "w-full absolute top-0 left-0 overflow-y-auto h-full pr-2"
                    ) as user_form:
                        user_form.visible = False
                        ui.label("YOUR EMAIL").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        user_email = (
                            ui.input(placeholder="Enter email")
                            .props("outlined")
                            .classes("w-full mb-4")
                        )
                        ui.label("PASSWORD").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        user_password = (
                            ui.input(placeholder="Enter your password", password=True)
                            .props("outlined")
                            .classes("w-full mb-8")
                        )
                        ui.button(
                            "Sign In as Patient",
                            on_click=lambda: handle_signin("patient"),
                        ).classes(
                            "w-full text-white font-semibold py-2 rounded-full"
                        ).props(
                            "color=teal-600"
                        )

                    # Pharmacy Sign-in Form (initially hidden)
                    with ui.column().classes(
                        "w-full absolute top-0 left-0 overflow-y-auto h-full pr-2"
                    ) as pharmacy_form:
                        pharmacy_form.visible = False
                        ui.label("PHARMACY EMAIL").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        pharma_email = (
                            ui.input(placeholder="Enter email")
                            .props("outlined")
                            .classes("w-full mb-4")
                        )
                        ui.label("PASSWORD").classes(
                            "text-sm font-semibold text-gray-700"
                        )
                        pharma_password = (
                            ui.input(placeholder="Enter your password", password=True)
                            .props("outlined")
                            .classes("w-full mb-8")
                        )
                        ui.button(
                            "Sign In as Pharmacy",
                            on_click=lambda: handle_signin("pharmacy"),
                        ).classes(
                            "w-full text-white font-semibold py-2 rounded-full"
                        ).props(
                            "color=teal-600"
                        )

                # --- BACKEND LOGIC ---

                def send_request_sync(url, data):
                    """Synchronous function to send the request."""
                    try:
                        headers = {"Content-Type": "application/x-www-form-urlencoded"}
                        return requests.post(url, data=data, headers=headers)
                    except requests.RequestException as e:
                        return e

                async def handle_signin(role: str):
                    """Handles the entire sign-in process, including authentication and session storage."""
                    endpoint_url = f"{base_url}/users/login"

                    if role == "patient":
                        email = user_email.value
                        password = user_password.value
                    else:  # pharmacy
                        email = pharma_email.value
                        password = pharma_password.value

                    if not email or not password:
                        ui.notify("Email and password are required.", color="negative")
                        return

                    payload_data = {"email": email, "password": password}

                    ui.notify("Signing in...", spinner=True)
                    response = await asyncio.to_thread(
                        send_request_sync, endpoint_url, payload_data
                    )

                    if isinstance(response, requests.Response):
                        if response.status_code == 200:
                            token_data = response.json()
                            access_token = token_data.get("access_token")

                            # --- THE FIXES ---
                            app.storage.user["authenticated"] = True
                            app.storage.user["name"] = email
                            app.storage.user["access_token"] = access_token
                            app.storage.user["role"] = role
                            ui.notify("Login successful!", color="positive")

                            if role == "pharmacy":
                                ui.navigate.to("/pharmacydashboard")
                            else:
                                ui.navigate.to("/userdashboard")
                        else:
                            try:
                                error_detail = response.json().get(
                                    "detail", "Invalid credentials."
                                )
                            except requests.exceptions.JSONDecodeError:
                                error_detail = response.text
                            ui.notify(
                                f"Login failed: {error_detail}",
                                color="negative",
                                multi_line=True,
                            )
                    else:
                        ui.notify(
                            f"Could not connect to the server: {response}",
                            color="negative",
                        )

                # --- UI INTERACTION LOGIC ---

                state = {"selected_role": None}

                def select_role(role):
                    """Controls the visibility and styling of the role selection and forms."""
                    if state["selected_role"] == role:
                        user_form.visible = False
                        pharmacy_form.visible = False
                        user_button.classes(
                            remove="border-blue-300", add="border-gray-200"
                        )
                        user_icon.classes(remove="text-blue-300", add="text-gray-500")
                        user_label.classes(remove="text-blue-300", add="text-gray-500")
                        pharmacy_button.classes(
                            remove="border-blue-300", add="border-gray-200"
                        )
                        pharmacy_icon.classes(
                            remove="text-blue-300", add="text-gray-500"
                        )
                        pharmacy_label.classes(
                            remove="text-blue-300", add="text-gray-500"
                        )
                        state["selected_role"] = None
                        return

                    state["selected_role"] = role
                    if role == "user":
                        user_form.visible = True
                        pharmacy_form.visible = False
                        user_button.classes(
                            remove="border-gray-200", add="border-blue-300"
                        )
                        user_icon.classes(remove="text-gray-500", add="text-blue-300")
                        user_label.classes(remove="text-gray-500", add="text-blue-300")
                        pharmacy_button.classes(
                            remove="border-blue-300", add="border-gray-200"
                        )
                        pharmacy_icon.classes(
                            remove="text-blue-300", add="text-gray-500"
                        )
                        pharmacy_label.classes(
                            remove="text-blue-300", add="text-gray-500"
                        )
                    else:
                        user_form.visible = False
                        pharmacy_form.visible = True
                        pharmacy_button.classes(
                            remove="border-gray-200", add="border-blue-300"
                        )
                        pharmacy_icon.classes(
                            remove="text-gray-500", add="text-blue-300"
                        )
                        pharmacy_label.classes(
                            remove="text-gray-500", add="text-blue-300"
                        )
                        user_button.classes(
                            remove="border-blue-300", add="border-gray-200"
                        )
                        user_icon.classes(remove="text-blue-300", add="text-gray-500")
                        user_label.classes(remove="text-blue-300", add="text-gray-500")

                user_button.on("click", lambda: select_role("user"))
                pharmacy_button.on("click", lambda: select_role("pharmacy"))
