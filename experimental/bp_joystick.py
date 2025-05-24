from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

hub = PrimeHub()

from micropup import MicroPUP
p=MicroPUP(Port.A)
p.add_command('bp',3,0)

while(1):
    hub.display.off()
    x,y,b=p.call('bp')
    hub.display.pixel(int((x+512)/205),int((y+512)/205))
