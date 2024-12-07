import signal
import os
import sys
import time
import can
from datetime import datetime
from PyQt5 import uic
from PyQt5.QtCore import Qt, QTime, QTimer, QDateTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel
# from pointee import Ui_Pointee

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
        uic.loadUi('qt_gui/Pointee/pointee.ui', self)
        self.adjustSize()  # Adjust size based on layout
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
        self.update_current_time()

        # default timer for upating target pointing (1 second)
        # this timer interval can be changed depends on selected pointing target

        # timer for updating current room weather (20 second)
        self.timer_room_weather = QTimer(self)
        #self.timer_room_weather.setTimerType(Qt.PreciseTimer)
        self.timer_room_weather.timeout.connect(self.update_current_room_weather)
        self.timer_room_weather.start(20000)
        self.update_current_room_weather()

        # timer for updating current outdoor weather (60 minute)
        self.timer_outdoor_weather = QTimer(self)
        self.timer_outdoor_weather.timeout.connect(self.update_current_outdoor_weather)
        self.timer_outdoor_weather.start(3600000)
        self.update_current_outdoor_weather()

        # Timer for updating date at midnight
        self.timer_date = QTimer(self)
        self.timer_date.timeout.connect(self.update_date)

        # Calculate time until midnight
        current_time = QTime.currentTime()
        midnight = QTime(0, 0)
        time_until_midnight = current_time.msecsTo(midnight) if current_time < midnight else (24 * 60 * 60 * 1000) - current_time.msecsTo(midnight)
        
        # Start the timer with the time until midnight
        self.timer_date.start(time_until_midnight)
        
        # After midnight, reset the timer to trigger every 24 hours
        self.timer_date.timeout.connect(lambda: self.timer_date.start(86400000))
        
        self.update_date()

    def initButtons(self):
        """ Initialize buttons """
        # get the available pointing targets from the pointing class
        # if the button is clicked, change the button color to green
        for target in self.pointing.available_targets:
            targetButtonName = "target_" + target
            self.__getattribute__(targetButtonName).clicked.connect(lambda _, target=target: self.target_button_on_click(target))

    #===========================================================================
    # define update functions (fastest to slowest)
    def update_current_room_weather(self):
        # Get indoor data
        current_room_temp = self.pointing.get_indoor_temperature()
        current_room_humidity = self.pointing.get_indoor_humidity()
        current_room_pressure = self.pointing.get_indoor_pressure()

        # Update labels
        self.label_roomTemp.setText("{:.1f} °F".format(current_room_temp))
        self.label_roomHumidity.setText("{:.1f} %".format(current_room_humidity))

    def update_current_outdoor_weather(self):
        if not self.pointing.update_outdoor_weather():
            print("Failed to update outdoor weather.")
            return

        outdoor_sealevel_pressure = self.pointing.get_outdoor_sealevel_pressure()
        outdoor_temp = self.pointing.get_outdoor_temp()
        outdoor_max_temp = self.pointing.get_outdoor_max_temp()
        outdoor_min_temp = self.pointing.get_outdoor_min_temp()
        outdoor_humidity = self.pointing.get_outdoor_humidity()
        outdoor_feellike_temp = self.pointing.get_outdoor_feellike_temp()

        # Update labels
        self.label_outdoorTemp.setText("{:.1f} °F".format(outdoor_temp))
        self.label_outdoorMaxTemp.setText("{:.1f} °F".format(outdoor_max_temp))
        self.label_outdoorMinTemp.setText("{:.1f} °F".format(outdoor_min_temp))
        self.label_outdoorHumidity.setText("{:.1f} %".format(outdoor_humidity))

    def update_current_time(self):
        current_time = QDateTime.currentDateTime()
        self.label_currentTime.setText(current_time.toString("hh:mm:ss"))

    def update_date(self):
        current_date = QDateTime.currentDateTime()
        self.label_currentDate.setText(current_date.toString("MM/dd/yyyy"))

    def target_button_on_click(self, target):
        """ Update the pointing target
        1. Change the target button color to green
        2. Request target ephemeris
        3. Calculate the target pointing loop delta time
        4. Update the target pointing loop Qtimer
        5. Call function to update the target pointing 
        """
        # change the target button color to dark green
        targetButtonName = "target_" + target
        button = self.__getattribute__(targetButtonName)
        button.setStyleSheet("""background-color: lightgreen; 
                                border: 1px solid red;
                             """)
        button.update()

        print("target button clicked: {}".format(target))

    def closeEvent(self, event):
        """ Override closeEvent to perform actions on exit """
        print("Closing the application...")
        # Perform cleanup or other tasks here
        self.cleanup()
        event.accept()

    def cleanup(self):
        """ Perform cleanup tasks """
        print("Performing cleanup...")
        # Stop timers if necessary
        self.timer_current_time.stop()
        self.timer_room_weather.stop()
        # Hardware shutdown process
        self.pointing.shutdown()

def handle_sigint(signal, frame):
    # print("SIGINT received. Cleaning up...")
    QApplication.quit()  # Gracefully quit the application

def main():
    # Set up the signal handler
    signal.signal(signal.SIGINT, handle_sigint)

    app = QApplication(sys.argv)
    window = PointeeApp()

    # Ensure cleanup runs on both window close and Ctrl-C
    def on_exit():
        print("Exiting application...")
        window.cleanup()

    app.aboutToQuit.connect(on_exit)  # Ensure cleanup on application quit

    window.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()

