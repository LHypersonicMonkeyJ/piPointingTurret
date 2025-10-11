import signal
import os
import sys
import time
import can
from datetime import datetime
from PyQt5 import uic
from PyQt5.QtCore import Qt, QTime, QTimer, QDateTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtWidgets import QPushButton, QButtonGroup
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
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)  # Only one button can be checked at a time

        qss = """
            QPushButton:checked {
                background-color: lightgreen;
                border: 1px solid red;
            }
            QPushButton {
                background-color: white;
                border: 1px solid transparent;
            }
        """

        for target in self.pointing.available_targets:
            btn = getattr(self, "target_" + target)
            btn.setCheckable(True)
            btn.setStyleSheet(qss)  # apply per button only
            self.group.addButton(btn)
            btn.clicked.connect(lambda _, target=target: self.target_button_on_click(target))

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
        1) Save the selected target
        2) Request target ephemeris
        3) Calculate the target pointing loop delta time
        4) Update / restart the target pointing QTimer
        5) Do one immediate point_to_target() to move motors now
        """

        print("current target: {}".format(target))

        # If same target is clicked again, ignore (already selected)
        if target == self.pointing.current_target:
            print("[GUI] Same target re-selected; no re-initialization needed.")
            return
        
        try:
            # Initialize target: Fetch ephemeris if needed and trun loop period (ms)
            delta_time = self.pointing.initialize_target(target)

            # Basic sanity check for delta_time
            if delta_time is None or delta_time <= 0:
                print("[WARN] Initialize_target returned None; falling back to 1000 ms.")
                delta_time = 1000  # Default to 1 second if invalid
            delta_time = int(max((50, min((3600000, delta_time)))))  # Clamp between 50 ms and 1 hour

            # Get current azimuth and elevation from Horizons
            self.pointing.az_el.get_az_el(datetime.now())
            print("Current azimuth: {:.2f}, elevation: {:.2f}".format(
                self.pointing.az_el.current_azimuth,
                self.pointing.az_el.current_elevation))
            print("Current azimuth rate: {:.2f}, elevation rate: {:.2f}".format(
                self.pointing.az_el.current_azimuth_rate,
                self.pointing.az_el.current_elevation_rate))
            
            # First immediate move to current azimuth and elevation, using initial motor speed
            v0 = abs(self.pointing.initial_motor_speed)
            self.pointing.point_to_target(
                self.pointing.az_el.current_azimuth,
                self.pointing.az_el.current_elevation,
                v0,
                v0)
            
            # (Re)start periodic poitning updates
            # Stop previous timer if it exists
            if hasattr(self, "timer_target_pointing") and self.timer_target_pointing is not None:
                try:
                    self.timer_target_pointing.stop()
                    self.timer_target_pointing.timeout.disconnect()
                except Exception as e:
                    print(f"[WARN] Exception stopping previous timer: {e}")

            # Create 9 or recreate) the timer
            self.timer_target_pointing = QTimer(self)
            # If you want tighter scheduling jitter:
            # self.timer_target_pointing.setTimerType(Qt.PreciseTimer)
            self.timer_target_pointing.timeout.connect(self.pointing.update_pointing)
            self.timer_target_pointing.start(delta_time)

            # Save the selected target only after successful init
            self.pointing.current_target = target
            print("Current target updated to: {}".format(self.pointing.current_target))

        except Exception as e:
            # Graceful failure path (keep old target/timer running)
            print(f"[ERROR] Failed to initialize target '{target}': {e}")

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

