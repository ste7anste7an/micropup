# Examples

This directory contains a number of examples. For these example some additional hardware is needed. Each example contains MicroBlocks code running on the LMS-ESP32 and Pybricks code (either in Python or in Blocks).

Hardware needed:
## TFT

You need a TFT screen using the ILI9241 controller and a XPT2046 touch controller. The SPI pins of the TFT panel are shared with the touch controller. 

## Neopixel
We connected a 9-pixel NeoPixel panel to GPIO21

## Joystick

We assume you have an I2C joystick connected to the Grove's connector (SCL=GPIO5 and SDA=GPIO4). The model we use can be found here: https://docs.m5stack.com/en/unit/joystick

## IMU

No additional hardware is neccessary if you plot the acceleration using the grpah in de MicroBlocks IDE. Optional you can use a TFT panel.
