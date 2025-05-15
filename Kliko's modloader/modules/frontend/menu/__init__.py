from modules.logger import Logger

from .app import App


def run() -> None:
    Logger.info("Initializing modloader menu...")
    App().mainloop()