__author__ = "Ste7an & Anton Vanhoucke"
__copyright__ = "Copyright 2023,2024 AntonsMindstorms.com"
__license__ = "GPL"
__version__ = "1.1"
__status__ = "Production"


from pybricks.parameters import Port, Color
from pybricks.iodevices import PUPDevice
from micropython import const
MODE = const(0)
NAME = const(1)
TO_HUB = const(2)
FROM_HUB = const(3)

class MicroPUP:
    """
    Class to communicate an LMS-ESP32 in MicroBlocks. Use this class on the Pybricks side.
    Connect an ESP32 board that runs MicroBlocks and the micropup library. Connect 
    the lego port to anyu poprt available on a Pybcricks hub.
    
    :param port: The port to which the PUPRemoteSensor is connected.
    :type port: Port (Example: Port.A)
    """

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
        to_hub: int = 0,
        from_hub: int = 0,
        #data_type: int = 0,
    ):
        """
        Registers a command defined in MicroBlocks.

        :param to_hub: The number of arguments sent to MicroBlocks
        :type to_hub: integer
        :param from_hub: The number of values returned from the hub
        :type from_hub: integer
        """        
        self.commands[command_name] = [
                self.nr_commands, to_hub, from_hub  #, data_type
            ]
        self.nr_commands+=1

    def call(self, command_name: str, *argv):
        """
        Calls a remote MicroBlocks function defined on the MicroBlocks side.

        :param command_name: The name of the command
        :type command_name: string
        :param Optionally, you can pass the <n_from_hub> number of parameters. 
        
        :return: It will return a single value, or a list, depending on the value of <n_to_hub>.

        """
        mode, to_hub, from_hub = self.commands[command_name]
        if from_hub>0 and len(argv)>0:
            # convert to int (in case values are float)
            arg_int = [int(arg) for arg in argv]
            self.pup_device.write(mode,arg_int)
            
        if to_hub > 0:
            response =  self.pup_device.read(mode)
            response = response[:to_hub]
            if len(response)==1:
                response = response[0]
            return response

## Some functions to import in block code
p=None

def init(port):
    global p
    p=MicroPUP(eval('Port.'+port))

def add_command(command_name: str,
        to_hub: int = 0,
        from_hub: int = 0,
    ):
    global p
    p.add_command(command_name, to_hub, from_hub)

def call(*argv):
    global p
    command_name = argv[0]
    response = p.call(command_name,*argv[1:])
    return response