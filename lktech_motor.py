import time
from can_messaging import CanMessaging

#actuator class for LK TECH motor
class LKTECH_Motor:
    def __init__(self, can_id, bitrate, timeout=0.3, motor_model=None):
        self.motor_model = motor_model
        self.can_id = can_id
        self.bitrate = bitrate
        self.timeout = timeout #unit: millisecond
        self.can_messaging = CanMessaging.initialize(channel='can0', bitrate=self.bitrate)
        self.current_command = None
        self.data_received = None
        self.command_dict = {
            #actions
            'motor off':            [0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'motor stop':           [0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'motor on':             [0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            #write parameters
            'write current position as zero position': [0x19, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'write encoder value as zero position':    [0x91, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'write zero position in RAM':              [0x95, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            #read parameters
            'read PID parameters':  [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'read acceleration':    [0x33, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'read encoder command': [0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'read multi angle':     [0x92, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'read single angle':    [0x94, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            #read and clear error
            'read error/state 1':   [0x9A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'read state 2':         [0x9C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'read state 3':         [0x9D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'clear error':          [0x9B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  
        }
        
        #Motor read parameters
        #PID parameters
        self.anglePidKp = 0
        self.anglePidKi = 0
        self.speedPidKp = 0
        self.speedPidKi = 0
        self.iqPidKp = 0
        self.iqPidKi = 0
        #acceleration
        self.acceleration = 0
        #encoder command
        self.encoder_raw_minus_offset = 0
        self.encoder_raw = 0
        self.encoder_offset = 0
        #error and state 1
        self.errState = 0x00
    
    ###############################################################
    #Utility functions
    ###############################################################
    def print_cmd(self, cmd, prefix=""):
        hex_string = ' '.join(f'0x{x:02x}' for x in cmd)
        print("{}: id: 0x{} cmd: {}".format(prefix, hex(self.can_id)[2:].zfill(4), hex_string))
        
    def motor_responded(self, flag_save_data=False):
        self.data_received = None
        current_time = time.time() #float, unit: second
        if flag_save_data:
            self.data_received = self.can_messaging.receive(timeout=self.timeout)
            #self.print_cmd(self.data_received, "self.data_received")
            if self.data_received and self.data_received[0] == self.current_command[0]:
                #self.print_cmd(self.current_command, "Motor received command")
                print("success!")
                return True
            else:
                self.print_cmd(self.current_command, "Motor failed to respond to command")
                self.print_cmd(self.data_received, "Motor responded with")
                return False
        else:
            #print("im here")
            self.data_received = self.can_messaging.receive(timeout=self.timeout)
            if self.data_received and self.data_received == self.current_command:
                #self.print_cmd(self.current_command, "Motor received command")
                print("success!")
                return True
            else:
                self.print_cmd(self.current_command, "Motor failed to respond to command")
                self.print_cmd(self.data_received, "Motor responded with")
                return False
            
    
    ###############################################################
    #Read and write motor parameters
    ###############################################################
    def read_PID_parameters(self):
        self.current_command = self.command_dict['read PID parameters']
        self.can_messaging.send(self.can_id, self.current_command)
        self.motor_responded(flag_save_data=True)
        #Extract PID parameters
        self.anglePidKp = self.data_received[2]
        self.anglePidKi = self.data_received[3]
        self.speedPidKp = self.data_received[4]
        self.speedPidKi = self.data_received[5]
        self.iqPidKp = self.data_received[6]
        self.iqPidKi = self.data_received[7]
        return self.anglePidKp, self.anglePidKi, self.speedPidKp, self.speedPidKi, self.iqPidKp, self.iqPidKi
        
    def write_PID_parameters(self, writeROM=True, anglePidKp=None, anglePidKi=None, speedPidKp=None, 
                             speedPidKi=None, iqPidKp=None, iqPidKi=None):
        #ROM PID parameters are valid when power off and on again
        #RAM PID parameters are invalid when power off and on again
        #Data field:
        if writeROM:
            command_byte = 0x32
        else:
            command_byte = 0x31
        null_byte = 0x00
        
        self.read_PID_parameters()
        
        #PID parameters
        if anglePidKp is None:
            anglePidKp = self.anglePidKp
        if anglePidKi is None:
            anglePidKi = self.anglePidKi
        if speedPidKp is None:
            speedPidKp = self.speedPidKp
        if speedPidKi is None:
            speedPidKi = self.speedPidKi
        if iqPidKp is None:
            iqPidKp = self.iqPidKp
        if iqPidKi is None:
            iqPidKi = self.iqPidKi
        
        #Construct command
        self.current_command = [
            command_byte,
            null_byte,
            anglePidKp,
            anglePidKi,
            speedPidKp,
            speedPidKi,
            iqPidKp,
            iqPidKi
        ]
        
        #Send command
        self.can_messaging.send(self.can_id, self.current_command)
        return self.motor_responded()
        
    def read_acceleration(self):
        self.current_command = self.command_dict['read acceleration']
        self.can_messaging.send(self.can_id, self.current_command)
        self.motor_responded(flag_save_data=True)
        accel_bytes = self.data_received[4:8]
        self.acceleration = int.from_bytes(accel_bytes, byteorder='little', signed=True)
        return self.acceleration
    
    def write_acceleration(self, acceleration):
        #Writing to RAM
        #Data field:
        command_byte = 0x34
        null_byte = 0x00
        
        #Convert acceleration to acceleration command
        acceleration = round(acceleration)
        
        #Acceleration bytes
        accel_bytes = [
            acceleration & 0xFF,
            (acceleration >> 8) & 0xFF,
            (acceleration >> 16) & 0xFF,
            (acceleration >> 24) & 0xFF
        ]
        
        #Construct command
        self.current_command = [
            command_byte,
            null_byte,
            null_byte,
            null_byte,
            *accel_bytes
        ]
        
        #Send command
        print("RAM writing acceleration: {}".format(acceleration))
        self.can_messaging.send(self.can_id, self.current_command)
        return self.motor_responded()
        
    def read_encoder_command(self):
        self.current_command = self.command_dict['read encoder command']
        self.can_messaging.send(self.can_id, self.current_command)
        self.motor_responded(flag_save_data=True)
        
        encoder_raw_minus_offset_bytes = self.data_received[2:4]
        encoder_raw_bytes = self.data_received[4:6]
        encoder_offset_bytes = self.data_received[6:8]
        
        #combine bytes to form 16-bit unsigned integers (little-endian)
        self.encoder_raw_minus_offset = int.from_bytes(encoder_raw_minus_offset_bytes, byteorder='little', signed=False)
        self.encoder_raw = int.from_bytes(encoder_raw_bytes, byteorder='little', signed=False)
        self.encoder_offset = int.from_bytes(encoder_offset_bytes, byteorder='little', signed=False)
        return self.encoder_raw_minus_offset, self.encoder_raw, self.encoder_offset
    
    def write_encoder_offset(self, encoder_offset):
        #Writing to ROM
        #Data field:
        command_byte = 0x91
        null_byte = 0x00
        
        #Convert encoder offset to encoder offset command
        encoder_offset = round(encoder_offset)
        
        #Encoder offset bytes
        encoder_offset_bytes = [
            encoder_offset & 0xFF,
            (encoder_offset >> 8) & 0xFF
        ]
        
        #Construct command
        self.current_command = [
            command_byte,
            null_byte,
            null_byte,
            null_byte,
            null_byte,
            null_byte,
            *encoder_offset_bytes
        ]
        
        #Send command
        print("ROM Writing encoder offset: {}".format(encoder_offset))
        self.can_messaging.send(self.can_id, self.current_command)
        return self.motor_responded()
        
    def write_current_pos_as_zero_pos_in_ROM(self):
        self.current_command = self.command_dict['write current position as zero position']
        self.print_cmd(self.current_command, "current command")
        print("\nERROR: This command is not working.\n")
        print("Writing current position in ROM as the zero position. \n ***Caution: Multiple times of writing will cause ROM wear***")
        self.can_messaging.send(self.can_id, self.current_command)
        status = self.motor_responded(flag_save_data=True)
        
        #Extract encoder offset
        if status:
            encoder_offset_bytes = self.data_received[6:8]
            self.encoder_offset = int.from_bytes(encoder_offset_bytes, byteorder='little', signed=False)
            print("Write zero position complete. encoder offset: {}".format(self.encoder_offset))
        else:
            print("Write zero position failed.")
        
    def read_multi_angle(self):
        self.current_command = self.command_dict['read multi angle']
        self.can_messaging.send(self.can_id, self.current_command)
        status = self.motor_responded(flag_save_data=True)
        
        if status:
            #Extract angle
            angle_bytes = self.data_received[1:]
        
            #combine bytes to form 64-bit signed integers (little-endian)
            angle_read = int.from_bytes(angle_bytes, byteorder='little', signed=True)
        
            #convert angle reading to angle in degrees
            angle = angle_read * 0.01
        else:
            angle = None
        return angle
        
    def read_single_angle(self):
        #angle reading is in range 0 to 36000, increment by 1
        #unit is 0.01degree/LSB
        self.current_command = self.command_dict['read single angle']
        self.can_messaging.send(self.can_id, self.current_command)
        self.motor_responded(flag_save_data=True)
        
        #Extract angle
        angle_bytes = self.data_received[4:8]
        
        #combine bytes to form 32-bit unsigned integers (little-endian)
        angle_read = int.from_bytes(angle_bytes, byteorder='little', signed=False)
        
        #convert angle reading to angle in degrees
        angle = angle_read * 0.01
        return angle
    
    def write_zero_pos_in_RAM(self):
        #This command clear motor multi turn and single turn data and set current position
        # as motor zero position in RAM. It's invalid when power off and on again.
        print("\nERROR: This command is not working.\n")
        self.current_command = self.command_dict['write zero position in RAM']
        self.can_messaging.send(self.can_id, self.current_command)
        return self.motor_responded()
        
    ###############################################################
    #Read and clear motor errors
    ###############################################################
    def read_error_and_state_1(self):
        self.current_command = self.command_dict['read error/state 1']
        self.can_messaging.send(self.can_id, self.current_command)
        self.motor_responded(flag_save_data=True)
        
        #Extract motor temperature
        
        #Extract motor voltage
        
        #Extract motor error code
        
        return self.errState
        
    def clear_error(self):
        print("Note: Error can't be cleared unless the motor state is back to normal")
        self.current_command = self.command_dict['clear error']
        self.can_messaging.send(self.can_id, self.current_command)
        self.motor_responded(flag_save_data=True)
        
        #Extract motor temperature
        
        #Extract motor voltage
        
        #Extract motor error code
        
        return self.errState
    
    def read_state_2(self):
        self.current_command = self.command_dict['read state 2']
        self.can_messaging.send(self.can_id, self.current_command)
        self.motor_responded(flag_save_data=True)
        
        #Extract motor temperature
        
        #Extract motor current
        
        #Extract motor speed
        
        #Extract motor encoder position
        
    def read_state_3(self):
        self.current_command = self.command_dict['read state 3']
        self.can_messaging.send(self.can_id, self.current_command)
        self.motor_responded(flag_save_data=True)
        
        #Extract motor temperature
        
        #Extract motor A phase current
        
        #Extract motor B phase current
        
        #Extract motor C phase current

    ###############################################################
    #Motor movement commands
    ###############################################################
    def turn_on_motor(self):
        self.current_command = self.command_dict['motor on']
        self.can_messaging.send(self.can_id, self.current_command)
        return self.motor_responded()
        
    def turn_off_motor(self):
        self.current_command = self.command_dict['motor off']
        self.can_messaging.send(self.can_id, self.current_command)
        return self.motor_responded()
        
    def stop_motor(self):
        self.current_command = self.command_dict['motor stop']
        self.can_messaging.send(self.can_id, self.current_command)
        return self.motor_responded()
        
    def move_angle_speed(self, angle, max_speed):
        #angleContrl is int32_t, corresponding actual position is 0.01degree/LSB, i.e. 36000/360degree.
        #motor spin direction is determined by the difference between target position and current position.
        #maxSpeed limit the max speed, it is uint16_t, corresponding actual speed is 1dps/LSB, 
        #i.e. 360 corresponding 360dps.
        
        #Convert angle to angle command and speed to speed command
        angle_cmd = round(angle * 36000 / 360)
        max_speed_cmd = round(max_speed * 360 / 360)
        
        #Data field:
        command_byte = 0xA4
        null_byte = 0x00
        
        #Speed limit low byte and high byte
        speed_bytes = [
            max_speed_cmd & 0xFF,
            (max_speed_cmd >> 8) & 0xFF
        ]
        
        #Angle control bytes
        angle_bytes = [
            angle_cmd & 0xFF,
            (angle_cmd >> 8) & 0xFF,
            (angle_cmd >> 16) & 0xFF,
            (angle_cmd >> 24) & 0xFF
        ]
        
        #Construct command
        self.current_command = [
            command_byte,
            null_byte,
            *speed_bytes,
            *angle_bytes
        ]
        
        #Send command
        print("Moving Motor to angle: {} degree at speed: {} degree/s".format(angle, max_speed))
        self.can_messaging.send(self.can_id, self.current_command)
        status = self.motor_responded(flag_save_data=True)
        