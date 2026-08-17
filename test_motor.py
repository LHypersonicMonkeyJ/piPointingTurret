"""
Standalone CAN motor test - talks to a single LKTECH_Motor directly,
without initializing Horizons, BMM150, BME280, etc.

Usage:
    python3 test_motor.py az      # test the azimuth motor (can_id 0x0141)
    python3 test_motor.py el      # test the elevation motor (can_id 0x0142)
"""
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from lktech_motor import LKTECH_Motor

MOTORS = {
    'az': {'can_id': 0x0141, 'tag': 'MS4010-CAN_az'},
    'el': {'can_id': 0x0142, 'tag': 'MS4010-CAN_el'},
}
BITRATE = 250000
TIMEOUT = 3  # seconds (see note in lktech_motor.py - this is passed straight to
             # python-can's bus.recv(timeout=...), which expects seconds, not ms)


def print_menu():
    print("""
--- Motor test menu ---
1) Turn motor ON
2) Turn motor OFF
3) Read single angle
4) Read multi-turn angle
5) Read error/state
6) Move to angle at speed (WILL MOVE THE MOTOR)
q) Quit
""")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in MOTORS:
        print(f"Usage: python3 {sys.argv[0]} [az|el]")
        sys.exit(1)

    choice = MOTORS[sys.argv[1]]
    print(f"Connecting to {choice['tag']} (can_id=0x{choice['can_id']:04x}, bitrate={BITRATE})...")
    motor = LKTECH_Motor(can_id=choice['can_id'], bitrate=BITRATE,
                          timeout=TIMEOUT, motor_tag=choice['tag'])

    try:
        while True:
            print_menu()
            cmd = input("Select: ").strip().lower()

            if cmd == '1':
                status = motor.turn_on_motor()
                print(f"turn_on_motor() -> {status}")
            elif cmd == '2':
                status = motor.turn_off_motor()
                print(f"turn_off_motor() -> {status}")
            elif cmd == '3':
                angle = motor.read_single_angle()
                print(f"read_single_angle() -> {angle}")
            elif cmd == '4':
                angle = motor.read_multi_angle()
                print(f"read_multi_angle() -> {angle}")
            elif cmd == '5':
                err = motor.read_error_and_state_1()
                print(f"read_error_and_state_1() -> {err}")
            elif cmd == '6':
                try:
                    angle = float(input("Target angle (degrees): ").strip())
                    speed = float(input("Max speed (degrees/sec): ").strip())
                except ValueError:
                    print("Invalid number, aborting move.")
                    continue
                confirm = input(f"About to move {choice['tag']} to {angle} deg "
                                 f"at {speed} deg/s. Confirm? [y/N]: ").strip().lower()
                if confirm == 'y':
                    status = motor.move_angle_speed(angle, speed)
                    print(f"move_angle_speed() -> {status}")
                else:
                    print("Cancelled.")
            elif cmd == 'q':
                break
            else:
                print("Unknown option.")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        print("Turning motor off before exit...")
        motor.turn_off_motor()


if __name__ == '__main__':
    main()
