from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch


from micropup import MicroPUP
NUMLEDS = 9

hub = PrimeHub()

p=MicroPUP(Port.A)
p.add_command('aap',1,1)
p.add_command('kat',8,8)
p.add_command('muis',0,3)
p.add_command('time',1,0)

N=1000
i=0
print("start tests")
t=StopWatch()
for i in range(1000):
    q=p.call('aap',i)
print("1000 calls to 'aap'",t.time())

t=StopWatch()
for i in range(1000):
    q=p.call('kat',*[(j+i)%100 for j in range(8)])

print("1000 calls to 'kat'",t.time())

t=StopWatch()
for i in range(1000):
    q=p.call('time')

print("1000 calls to 'time'",t.time())

i=0
t=StopWatch()
while True:
    p.call('muis',i,N-i,2*i)
    i+=1
    if i>N:
        print("t=",t.time())
        i=0
        t=StopWatch()
    #wait(10)