from nicegui import ui, app
from pages.contact import *
from pages.home import *
from pages.shop import *
from components.footer import *
from components.navbar import *
from pages.signup import *
from pages.signin import *
from pages.user_dashboard import *
from pages.vendor_dashboard import *
from pages.main_page import *
from pages.inbox import *
from pages.sent_messages import *
from components.create_ad import *
from components.edit_stock import *
from pages.order import *

app.add_static_files("/assets", "assets")
ui.run(storage_secret="nanijayblinkz1234@")
