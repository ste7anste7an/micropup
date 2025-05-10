from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop, Axis
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

from micropup import MicroPUP

hub = PrimeHub()

p=MicroPUP(Port.A)
p.add_command('disp',to_hub=1,from_hub=0)

old_d=0

def show(d):
    global old_d
    if d!=old_d:
        hub.display.off()
        for i in range(5):
            for j in range(5):
                if d&(1<<(i*5+j)):
                    hub.display.pixel(j,4-i)
        old_d=d

cnt=0

s=StopWatch()
hub.display.off()
#for i in range(1000//9):
while (1):
    cnt+=1
    cnt%=64
    d=p.call('disp')
    show(d)
        