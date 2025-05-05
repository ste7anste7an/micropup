# PUPRemote for MicroBlocks = MicroPUP

## Firmware

To flash the LMS-ESP32 with the MicroBlocks firmware, head over to [firmware.antonsmindstorms.com](https://firmware.antonsmindstorms.com).


# Library for communicating with LEGO hubs
## MicroBlocks

A library is available for the communication with LEGO hubs. The LMS-ESP32 emulated a lpup lego sensor and uses that protocol to send and receive data to and from the LEGO hub. Add the [micropup.ubl](lirary/micropup.ubl) to your MicroBlocks project. 

## Pybricks
Download [library/micropup.py] in pybricks. This is the library fro the Pybrcks side that is compatible with the MicroBlocks library.


# Demo code


# Changes to MicroBlocks firmware

In the repo https://bitbucket.org/john_maloney/smallvm/src/dev/ you will find the source code for MicroBlocks. This is a PlatformIO project for different architectures (ESP32, NRF52, Pi Pico). The basic assumption of MicroBlcoks is that some hardware interfaces are fixed to a specific set of GPIOs. The I2C and SPI pins are configured in the firmware.
Therefore, to meet the requirements for porting MicroBlcoks to the LMS-ESP32 platform, some changes had to be made:

- I2C needs to be mapped to GPIO4 (SCL) and GPIO5 (SDA)
- for using the 10-pin connector on the LMS-ESP32v2, we had to remap the SPI pins for the TFT screen. Currently the firmware supports the ILI9341 controller. Support for ST7789 controllers will be added later.
- The functions for controlling Serial  communications are limited. We added a `Serial.available` and `Serial.read(n)` for only reading `n` bytes
- Because the different pin-out of the MCU's used on the LMS-ESP32 and LMS-ESP32v2, we had to add a function for reading the ESP32 CPU type, so we can remap serial port pins based on the LMS-ESP32 model.
