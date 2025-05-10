from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch
from micropup import MicroPUP

hub = PrimeHub()

timer = StopWatch()

# Initialize variables.
count = 0

# The main program starts here.
p = MicroPUP(Port.A)
# pup_add_command <name> <to_hub> <from_hub>
p.add_command('show', to_hub = 0, from_hub = 1)
p.add_command('add', to_hub = 1, from_hub = 2)
p.add_command('count', to_hub = 1, from_hub = 0)


while True:
    p.call('show', timer.time())
        # counts increases to 1000 and restarts at 0
    count = (count + 1) % 1000
    s = p.call('add', count, count * 2)
    print(f'sum of {count} and {count * 2} =? {s}')
    print('received counter = ', p.call('count'))
    wait(100)