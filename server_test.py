from Server import Server

server = Server()
# server.add_mouse_listener()
server.start_msg_listener()
server.main_loop()