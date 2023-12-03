import os
import can

os.system('sudo ip link set can0 type can bitrate 500000')
os.system('sudo ifconfig can0 up')

with can.interface.Bus(channel = 'can0', bustype = 'socketcan') as can0:
    msg = can.Message(arbitration_id=0x123, data=[0, 1, 2, 3, 4, 5, 6, 7], is_extended_id=False)
    try:
        can0.send(msg)
        print("Message sent!")
    except can0.CanError:
        print("Error! Message NOT sent")

os.system('sudo ifconfig can0 down')
