from src.screen_manager.gui import Gui
from src.sharer.server import Server
server = Server()
screen_manager_gui = Gui(update_func=server.update_position)
