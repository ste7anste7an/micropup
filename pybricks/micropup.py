from pybricks.iodevices import PUPDevice
from micropython import const
MODE = const(0)
NAME = const(1)
TO_HUB = const(2)
FROM_HUB = const(3)
DATA_TYPE = const(4)

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
        data_type: int = 0,
    ):
        
        self.commands[command_name] = [
                self.nr_commands, to_hub_cnt, from_hub_cnt, data_type
            ]
        self.nr_commands+=1

    def call(self, command_name: str, *argv):
        """
        Call a remote function on the sensor side with the mode_name you defined on both sides.

        """

        mode, to_hub_cnt, from_hub_cnt, data_type = self.commands[command_name]
        if from_hub_cnt>0 and len(argv)>0:
            self.pup_device.write(mode,argv)
            
        if to_hub_cnt > 0:
            response =  self.pup_device.read(mode)
            return response