import gpiod
import os
import pwd
import logging, time, math
from smbus2 import SMBus

print("Setting motors ...")

chip0 = gpiod.Chip("/dev/gpiochip0")
# print(chip0)
pwd.getpwuid(os.getuid())[0]


SMBUS_INTERFACE = 0
FREQUENCY = 50

# Registers/etc:
PCA9685_ADDRESS    = 0x40
MODE1              = 0x00
MODE2              = 0x01
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04
PRESCALE           = 0xFE
LED0_ON_L          = 0x06
LED0_ON_H          = 0x07
LED0_OFF_L         = 0x08
LED0_OFF_H         = 0x09
ALL_LED_ON_L       = 0xFA
ALL_LED_ON_H       = 0xFB
ALL_LED_OFF_L      = 0xFC
ALL_LED_OFF_H      = 0xFD

# Bits:
RESTART            = 0x80
SLEEP              = 0x10
ALLCALL            = 0x01
INVRT              = 0x10
OUTDRV             = 0x04


logger = logging.getLogger(__name__)

class PCA9685(object):
    """PCA9685 PWM LED/servo controller."""

    def __init__(self, freq_hz=FREQUENCY, interface=SMBUS_INTERFACE, address=PCA9685_ADDRESS):
        """
        Initialize the PCA9685 chip at the provided address on the specified I2C bus number.
        The default address is 0x40 and the default bus is 0.

        Args:
            freq_hz (int): The frequency of PWM signal for the servo (default 50Hz)
            interface (int): The I2C bus number to use (default 0)
            address (int): The I2C address of the PCA9685 chip (default 0x40)
        """
        self.interface = interface
        self.address = address

        self.set_all_pwm(0, 0)
        with SMBus(self.interface) as bus:
            bus.write_byte_data(self.address, MODE2, OUTDRV)
            bus.write_byte_data(self.address, MODE1, ALLCALL)
            time.sleep(0.005) # wait for oscillator
            mode1 = bus.read_byte_data(self.address, MODE1)
            mode1 = mode1 & ~SLEEP # wake up (reset sleep)
            bus.write_byte_data(self.address, MODE1, mode1)
            time.sleep(0.005) # wait for oscillator

        """
        Set the PWM frequency of the PCA9685 module.
        freq_hz (float): The desired frequency in Hz. Valid from 24 Hz to 1526 Hz.
        """
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        logger.debug('Setting PWM frequency to {0} Hz'.format(freq_hz))
        logger.debug('Estimated pre-scale: {0}'.format(prescaleval))
        prescale = int(math.floor(prescaleval + 0.5))
        logger.debug('Final pre-scale: {0}'.format(prescale))
        with SMBus(self.interface) as bus:
            oldmode = bus.read_byte_data(self.address, MODE1)
            newmode = (oldmode & 0x7F) | 0x10    # sleep
            bus.write_byte_data(self.address, MODE1, newmode)  # go to sleep
            bus.write_byte_data(self.address, PRESCALE, prescale)
            bus.write_byte_data(self.address, MODE1, oldmode)
            time.sleep(0.005)
            bus.write_byte_data(self.address, MODE1, oldmode | 0x80)

    def set_pwm(self, channel, on, off):
            """
            Sets the on and off time for a specific channel on the PCA9685 PWM controller.
            
            Args:
                channel (int): The channel number to set the on and off time for.
                on (int): The value for the on time of the PWM signal.
                off (int): The value for the off time of the PWM signal.
            """
            with SMBus(self.interface) as bus:
                bus.write_byte_data(self.address, LED0_ON_L+4*channel, on & 0xFF)
                bus.write_byte_data(self.address, LED0_ON_H+4*channel, on >> 8)
                bus.write_byte_data(self.address, LED0_OFF_L+4*channel, off & 0xFF)
                bus.write_byte_data(self.address, LED0_OFF_H+4*channel, off >> 8)

    def set_all_pwm(self, on, off):
            """
            Sets the on and off values for all channels of the PCA9685 PWM controller.
            
            Args:
                on (int): The value to set the on time for all channels.
                off (int): The value to set the off time for all channels.
            """
            with SMBus(self.interface) as bus:
                bus.write_byte_data(self.address, ALL_LED_ON_L, on & 0xFF)
                bus.write_byte_data(self.address, ALL_LED_ON_H, on >> 8)
                bus.write_byte_data(self.address, ALL_LED_OFF_L, off & 0xFF)
                bus.write_byte_data(self.address, ALL_LED_OFF_H, off >> 8)

    def software_reset(self):
        """Sends a software reset (SWRST) command to all servo drivers on the bus."""
        #self._device.writeRaw8(0x06)
        with SMBus(self.interface) as bus:
            bus.write_byte_data(self.address, 0x06, 0x00)
pwm_ctl = PCA9685(50) # defaults to using frequency 50 Hz, i2c-0 and address 0x40

motor_map = {
    'left_shoulder': 4,
    'left_elbow': 2,
    'right_shoulder': 1,
    'right_elbow': 0,
    'torso': 6,
    'neck': 5
}
motor_bounds = {
    'left_shoulder': (200, 500), #up, down
    'left_elbow': (425, 500), #far, close
    'right_shoulder': (200, 500), #down, up
    'right_elbow': (400, 475), #close, far
    'torso': (156, 356, 256), # right, left, middle
    'neck': (350, 500 ,425) # right, left, middle
}

home_position = {
    'left_shoulder': 500, #up, down
    'left_elbow': 500, #far, close
    'right_shoulder': 200, #down, up
    'right_elbow': 200, #close, far
    'torso': 256, # right, left, middle
    'neck': 425 # right, left, middle
}

current_position = home_position


# motors_ = dictionary, with keys=motor name, value=pwd (angle)
def move_motors(motors_):
    for mot, ang in motors_.items():
        ang = max([min([ang, motor_bounds[mot][1]]), motor_bounds[mot][0]])
        current_position[mot] = ang
        pwm_ctl.set_pwm(motor_map[mot], 0, ang)


def move_sequence(motor_seq):
    start_time = time.time()
    for seq in motor_seq:
        current_time = time.time() - start_time
        delay = seq['time'] - current_time
        if delay > 0:
            time.sleep(delay)
        move_motors(seq['motors'])


def movement_thread(motor_seq, stop_event, stop_condition):
    start_time = time.time()
    for seq in motor_seq:
        current_time = time.time() - start_time
        delay = seq['time'] - current_time
        if delay > 0:
            time.sleep(delay)
        move_motors(seq['motors'])
        
        if stop_event.is_set():
            break
    if "movement" in stop_condition:
        stop_event.set()

    
def run_hello_seq():
    hello_seq = [
    {
        'time': 0,
        'motors': home_position
    },
    {
        'time': 2,
        'motors': {'right_shoulder': 500}
    }
    ]
    for i in range(0, 3):
        hello_seq.append({'time': (2.5 + (i * 0.8)), 'motors': {'right_elbow': 500}})
        hello_seq.append({'time': (2.9 + (i * 0.8)), 'motors': {'right_elbow': 200}})
    hello_seq.append({
        'time': hello_seq[-1]['time'] + 1.0,
        'motors': home_position
    })
    move_sequence(hello_seq)

# run_hello_seq()
move_motors(home_position)