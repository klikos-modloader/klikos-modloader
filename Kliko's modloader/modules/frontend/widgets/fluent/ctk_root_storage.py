from customtkinter import CTk


root_instance: CTk | None = None

def set_root_instance(root: CTk):
    global root_instance
    root_instance = root

def get_root_instance() -> CTk | None:
    return root_instance

def clear_root_instance():
    global root_instance
    root_instance = None