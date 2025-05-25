# run.py
import sys
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow  

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Dijkstra")

    window = MainWindow()
    window.resize(1200, 800)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
