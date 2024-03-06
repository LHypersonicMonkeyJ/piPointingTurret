import os
import sys
import time
import can
from datetime import datetime
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel
from pointee import Ui_Pointee

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from pointing import pointing

class PointeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initHardware()
        self.initUI()
        self.initTimer()
        self.initButtons()

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
        self.timer_current_time = QTimer(self)
        self.timer_current_time.timeout.connect(self.update_current_time)
        self.timer_current_time.start(1000)

        # default timer for upating target pointing (1 second)
        # this timer interval can be changed depends on selected pointing target

        # timer for updating current room weather (20 second)
        self.timer_room_weather = QTimer(self)
        #self.timer_room_weather.setTimerType(Qt.PreciseTimer)
        self.timer_room_weather.timeout.connect(self.update_current_room_weather)
        self.timer_room_weather.start(20000)

        # timer for updating current outdoor weather (15 minute)

        # timer for updating daily outdoor weather (midnight)

        # timer for updating date (midnight)

    def initButtons(self):
        """ Initialize buttons """
        # get the available pointing targets from the pointing class
        # if the button is clicked, change the button color to green
        for target in self.pointing.available_targets:
            targetButtonName = "target_" + target
            self.ui.__getattribute__(targetButtonName).clicked.connect(lambda _, target=target: self.target_button_on_click(target))

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
        current_time = QDateTime.currentDateTime()
        self.ui.label_currentTime.setText(current_time.toString("hh:mm:ss"))

    def update_outdoor_current_weather(self):
        pass

    def update_outdoor_daily_weather(self):
        pass

    def update_date(self):
        pass

    def target_button_on_click(self, target):
        """ Update the pointing target
        1. Change the target button color to green
        2. Request target ephemeris
        3. Calculate the target pointing loop delta time
        4. Update the target pointing loop Qtimer
        5. Call function to update the target pointing 
        """
        print("target button clicked: {}".format(target))

def main():
    app = QApplication(sys.argv)
    window = PointeeApp()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()

