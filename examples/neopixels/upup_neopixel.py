from pybricks.hubs import PrimeHub
from pybricks.parameters import Port
from micropup import MicroPUP

hub = PrimeHub()

p=MicroPUP(Port.A)
p.add_command('led',to_hub=0,from_hub=4)

while(1):
    for i in range(0,100,10):
        for n in range(1,10):
            p.call('led',n,(100-i-n*3)%100,(i+n)%100,(i+50-n*2)%100)