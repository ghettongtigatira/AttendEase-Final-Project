from config import BASE_DIR
from frontend.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow(BASE_DIR)
    app.run()