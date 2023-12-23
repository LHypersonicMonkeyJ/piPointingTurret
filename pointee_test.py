import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from pointee import Ui_Pointee

class PointeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create an instance of the generated UI
        self.ui = Ui_Pointee()
        self.ui.setupUi(self)
        
        # Remove window title bar and frame
        self.setWindowFlag(Qt.FramelessWindowHint)

def main():
    app = QApplication(sys.argv)
    window = PointeeApp()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()

