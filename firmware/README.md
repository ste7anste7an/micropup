# Changes to MicroBlcoks firmware

In the repo https://bitbucket.org/john_maloney/smallvm/src/dev/ you will find the source code for MicroBlocks. This is a PlatformIO project for different architectures (ESP32, NRF52, Pi Pico). The basic assumption of MicroBlcoks is that some hardware interfaces are fixed to a spcific ser of GPIO. The I2C and SPI pins are configured in the firmware.
Therefore, to meet the requirements for porting MicroBlcoks to the LMS-ESP32 platform, some changes had to be made:

- I2C needs tpo be mapped to GPIO4 (SCL) and GPIO5 (SDA)
- for using the 10-pin connector on the LMS-ESP32v2, we had to remap the SPI pins for the TFT screen. We support two different types of controllers: ILI9341 and ST7789. This willl be supported by two different firmwares.
- The functions for controling Serial  communications are limited. We added a `Serial.available` and `Serial.read(n)` for only reading `n` bytes
- No hardware microsecond counter is available. We added `millis` which is a counter counting milliseconds
- Because the different pin-out of the MCU's used on the LMS-ESP32 and LMS-ESP32v2, we had to add a function for reading the ESP32 CPU type, so we can remap serial port pins based on the LMS-ESP32 model.
