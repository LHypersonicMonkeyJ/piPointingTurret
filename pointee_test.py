import os
import sys
import time
import can
from datetime import datetime
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from pointee import Ui_Pointee

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from pointing import pointing

class PointeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initHardware()
        self.initUI()
        self.initTimer()

    def initHardware(self):
        self.pointing = pointing()

    def initUI(self):
        # Create an instance of the generated UI
        self.ui = Ui_Pointee()
        self.ui.setupUi(self)
        self.resize(800, 480)
        self.setWindowTitle('Pointee')
        self.showFullScreen()
        self.setWindowFlag(Qt.FramelessWindowHint)

    def initTimer(self):
        """ timer init fastest to slowest """
        # timer for updating current time (1 second)

        # timer for upating target pointing (1 second)

        # timer for updating current room weather (20 second)
        self.timer_room_weather = QTimer(self)
        self.timer_room_weather.timeout.connect(self.update_current_room_weather)
        self.timer_room_weather.start(20000)

        # timer for updating current outdoor weather (15 minute)

        # timer for updating daily outdoor weather (midnight)

        # timer for updating date (midnight)

        

    #===========================================================================
    # define update functions (fastest to slowest)
    def update_current_room_weather(self):
        # Get indoor data
        current_room_temp = self.pointing.get_indoor_temperature()
        current_room_humidity = self.pointing.get_indoor_humidity()
        current_room_pressure = self.pointing.get_indoor_pressure()

        # Update
        # update the room temperature label
        self.ui.label_roomTemp.setText("{:.1f} °F".format(current_room_temp))

    def update_current_time(self):
        pass

    def update_outdoor_current_weather(self):
        pass

    def update_outdoor_daily_weather(self):
        pass

    def update_date(self):
        pass

def main():
    app = QApplication(sys.argv)
    window = PointeeApp()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()

