from pybricks.hubs import PrimeHub
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.tools import wait, StopWatch
from micropup import MicroPUP

hub = PrimeHub()

p=MicroPUP(Port.A)
p.add_command('joystick',to_hub=3,from_hub=0)

while 1:
    hub.display.off()
    x,y,button=p.call('joystick')
    hub.display.pixel(x//51,y//51, brightness=100)
    wait(10)

