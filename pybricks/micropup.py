from pybricks.parameters import Port, Color
from pybricks.iodevices import PUPDevice
from micropython import const
MODE = const(0)
NAME = const(1)
TO_HUB = const(2)
FROM_HUB = const(3)
#DATA_TYPE = const(4)
#DATA_TYPES = ['b':0, 'w':1, 'i':2]

class MicroPUP:
    def __init__(self, port):
        self.port = port
        self.commands = {}
        self.nr_commands = 0
        try:
            self.pup_device = PUPDevice(port)
        except OSError:
            self.pup_device = None
            print("PUPDevice not ready on port", port)

    def add_command(
        self,
        command_name: str,
        to_hub_cnt: int = 0,
        from_hub_cnt: int = 0,
        #data_type: int = 0,
    ):
        
        self.commands[command_name] = [
                self.nr_commands, to_hub_cnt, from_hub_cnt  #, data_type
            ]
        self.nr_commands+=1

    def call(self, command_name: str, *argv):
        """
        Call a remote function on the sensor side with the mode_name you defined on both sides.

        """
        #mode, to_hub_cnt, from_hub_cnt, data_type = self.commands[command_name]
        mode, to_hub_cnt, from_hub_cnt = self.commands[command_name]
        if from_hub_cnt>0 and len(argv)>0:
            self.pup_device.write(mode,argv)
            
        if to_hub_cnt > 0:
            response =  self.pup_device.read(mode)
            if len(response)==1:
                response = response[0]
            return response
p=None

def pup_init(port):
    global p
    p=MicroPUP(eval('Port.'+port))

def pup_add_command(command_name: str,
        to_hub_cnt: int = 0,
        from_hub_cnt: int = 0,
        # data_type: int = 0,
    ):
    global p
    p.add_command(command_name, to_hub_cnt, from_hub_cnt)# , data_type)


def pup_call(*argv):
    global p
    command_name = argv[0]
    response = p.call(command_name,*argv[1:])
    return response