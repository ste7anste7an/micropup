from pybricks.hubs import PrimeHub
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.tools import wait, StopWatch
from micropup import MicroPUP

hub = PrimeHub()

p=MicroPUP(Port.A)
p.add_command('gp',to_hub=4,from_hub=0)

while 1:
    hub.display.off()
    x,y,x2,y2=p.call('gp')
    hub.display.pixel((y+512)//205,(x+512)//205, brightness=100)
    hub.display.pixel((y2+512)//205,(x2+512)//205, brightness=60)
    wait(10)

