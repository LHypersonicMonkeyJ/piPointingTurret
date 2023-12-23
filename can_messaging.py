import os
import can
import time

class CanMessaging:
    _bus_instance = None
    _shutdown_executed = False
    
    @classmethod
    def initialize(cls, channel='can0', bitrate=500000):
        if cls._bus_instance is None:
            os.system(f'sudo ip link set {channel} type can bitrate {bitrate}')
            os.system(f'sudo ifconfig {channel} up')
            cls._bus_instance = can.interface.Bus(channel=channel, bustype='socketcan')
        return cls(cls._bus_instance, channel=channel, bitrate=bitrate)
    
    def __init__(self, bus, channel='can0', bitrate=500000):
        self.channel = channel
        self.bitrate = bitrate
        self.bus = bus
        
    def send(self, can_id, data, extended=False):
        msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=extended)
        try:
            self.bus.send(msg)
            #print out message as hex
            data_string = ' '.join(f'0x{x:02x}' for x in msg.data)
            print(f"Sent message: id: 0x{hex(msg.arbitration_id)[2:].zfill(4)} cmd: {data_string}")
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
            
    def receive(self, timeout=0.1): #default timeout set to 0.1ms
        messages = []
        start_time = time.time() #float. Unit: seconds
        #print("timeout: {}".format(timeout))
        divider = timeout / 1 #ensure bus.recv() timeout is 1ms
        try:
            #print("Waiting for message...")
            msg = self.bus.recv(timeout=timeout) #recv requires timeout in seconds
            if msg:
                #print out message as hex
                hex_string = ' '.join(f'{x:02x}' for x in msg.data)
                print(f"Received message: {msg.arbitration_id:x} {hex_string}")
                #convert to 8 bytes data
                hex_list = [int(f'{byte:02x}', 16) for byte in msg.data]
                messages.append(hex_list)
        except Exception as e:
            print(f"Error receiving message: {e}")
            
        #only expect for one message
        if not messages:
            print("Timeout! No message received.")
            return None
        return messages[0]
    
    # class destructor
    def __del__(self):
        if not self._shutdown_executed:
            self.bus.shutdown()
            os.system(f'sudo ifconfig {self.channel} down')
            print(f"{self.channel} bus shut down.")
            self._shutdown_executed = True