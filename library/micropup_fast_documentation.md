# MicroPUP fast UART support for Pybricks 4

## Purpose

`micropup_fast.ubl` makes an LMS-ESP32 running MicroBlocks appear as a Powered Up
(LPF2) device to Pybricks 4. It replaces the old 2400-baud startup with the fast
physical handshake used by current Pybricks firmware, then performs all LPF2
registration and runtime communication at 115200 baud.

The timing-sensitive GPIO-to-UART transition is implemented by the new SmallVM
primitive `serial:pupFastOpen`. Mode registration and application data remain in
the MicroBlocks library.

Files:

- `serialPrims.cpp`: SmallVM source containing `primSerialPUPFastOpen`.
- `pupFastOpen_serialPrims.patch`: patch for an existing SmallVM tree.
- `micropup_fast.ubl`: MicroBlocks library using the native primitive.
- `micropup.ubl`: original library, left unchanged.

## Why the original startup stopped working

The original library used the traditional LPF2 startup:

1. Generate an identification pulse using interpreted MicroBlocks GPIO blocks.
2. Wait 450 ms.
3. Open UART at 2400 baud.
4. Send LPF2 registration information.
5. Change to 115200 baud.

Pybricks 4 can request the fast startup before the 2400-baud registration. The
hub returns a GPIO pulse train after the sensor's identification pulse. One
short pulse in that train tells the sensor to start UART directly at 115200.

Implementing this in `.ubl` code was unreliable for two reasons:

- MicroBlocks task scheduling and block dispatch add variable delays while the
  GPIO pulses are being measured and while the pins are changed to UART mode.
- The normal SmallVM `serial:open` primitive waits 250 microseconds after opening
  the UART and deliberately discards up to 16 bytes as startup garbage. During
  the fast LPF2 handshake those bytes may be valid bytes from the hub.

The native primitive avoids both problems by keeping the complete physical
handshake in one C++ call and by invoking the internal `serialOpen(115200)`
function directly. It does not run the normal receive-byte discard code.

## Connection sequence

```text
LMS-ESP32 / MicroPUP                         Pybricks hub
        |                                         |
        |-- 5 ms GPIO identification pulse ------>|
        |                                         |
        |<------- GPIO detection pulse train -----|
        |                                         |
        |  detect clearly short fast pulse        |
        |  switch pins to UART, 115200 baud       |
        |-- 04 fast-start ACK -------------------->|
        |-- TYPE --------------------------------->|
        |-- MODES -------------------------------->|
        |-- SPEED = 115200 ----------------------->|
        |-- VERSION ------------------------------>|
        |-- information for each mode ----------->|
        |-- 04 registration complete ------------>|
        |-- initial mode-0 data packet ---------->|
        |<======= normal LPF2 communication ======>|
```

## How a sensor starts negotiation

Negotiation begins before either side is using the pins as an ordinary UART.
The sensor must first make itself electrically visible to the hub. For the fast
path implemented here, the sequence is:

1. **Sensor prepares the port as GPIO.** The LMS-ESP32 RX pin is an input and
   its TX pin is an output. The TX output is initially low.
2. **Sensor sends a hello pulse.** It drives TX high for 5 ms and then drives it
   low. This is the sensor's request for the hub to begin port detection.
3. **Hub starts active detection.** The hub drives the line connected to the
   sensor's RX input through a sequence of high and low intervals. At this point
   these are observed as GPIO levels, not parsed by MicroPUP as UART bytes.
4. **Sensor measures the hub waveform.** It times each high interval and waits
   for the following low interval. The first eleven measured intervals are not
   eligible to select fast mode. This prevents the normal beginning of the hub's
   port-detection sequence from being mistaken for the fast indication.
5. **Hub produces the fast indication.** A clearly shorter high interval tells
   a fast-capable sensor to change to 115200-baud UART. In the successful test it
   was the 22nd measured interval and lasted 14.160 ms.
6. **Sensor changes pin function atomically.** The native primitive immediately
   changes the same GPIO pins to 115200-baud, 8-data-bit, no-parity, one-stop-bit
   UART operation. UART RX is active during a 5 ms settling time.
7. **Sensor acknowledges fast startup.** It transmits `0x04` (`BYTE_ACK`). The
   native primitive completes this step before returning to interpreted
   MicroBlocks code.
8. **Sensor identifies itself.** The `.ubl` library sends TYPE, MODES, SPEED,
   VERSION and the information records for every mode, followed by another
   `BYTE_ACK` to finish registration.
9. **Hub validates registration.** If all registration messages and checksums
   are valid, the hub acknowledges the information phase and exposes the device
   and its modes to `PUPDevice`.

The sensor therefore initiates detection with the 5 ms GPIO hello. The hub
controls the next part by returning the detection/fast-selection waveform. Once
fast selection succeeds, negotiation continues as bidirectional LPF2 UART
messages.

Here, “high” and “low” describe the logical GPIO values used by the firmware
(`HIGH`/`LOW`). If the LMS-ESP32 cable interface contains an inverting driver,
the voltage observed on the Powered Up connector will have the opposite
polarity. Protocol analysis should therefore state whether a trace was measured
at the ESP32 GPIO or at the hub connector.

## Pulses generated by the hub

The hub-side waveform seen by `primSerialPUPFastOpen()` is a succession of high
periods separated by low periods. The primitive records one `pulseNumber` for
each high/low cycle:

```text
Sensor TX:  ____|----- 5 ms -----|________________________________
                                      sensor hello

Hub TX /    _____|--- normal ---|_|--- normal ---|_ ...
Sensor RX:                         detection cycles

            ... _|-- short fast --|______________________________
                       ^
                       switch sensor pins to UART here
```

The native implementation handles the hub waveform as follows:

- It examines at most 25 cycles, so a disconnected or unresponsive port cannot
  block SmallVM forever.
- Each high interval has a 25 ms safety timeout.
- Each following low interval has a 30 ms safety timeout.
- Pulses 1 through 11 are observed but cannot select fast mode.
- From pulse 12 onward, only a high interval shorter than 15,000 microseconds is
  accepted as the fast indication.
- If no valid short interval is found, UART is not opened and no LPF2 metadata
  is sent. The MicroBlocks heartbeat later starts a new attempt.

The measured number and duration are characteristics of the current Pybricks
hub implementation and the particular hardware timing, not fields encoded in
an LPF2 packet. They should not be treated as universal constants. Two observed
examples explain the chosen margin:

| Result | Pulse | High time | Interpretation |
|---|---:|---:|---|
| Working | 22 | 14,160 us | Clearly short fast indication. |
| Failed with old threshold | 12 | 15,960 us | Normal approximately 16 ms interval falsely accepted as fast. |

The original Python `lpf2.py` implementation measured time in whole
milliseconds and used a boundary near 16 ms. Native C++ measures microseconds,
so using the same numeric boundary was too sensitive to normal jitter. The
15,000 us threshold adds separation while still accepting the measured 14.160
ms fast interval.

### Relationship to the UART `CMD_SPEED` exchange

The GPIO waveform above belongs to the hub's physical port-detection and fast
startup behavior. At the LPF2 message layer, newer devices can synchronize at
115200 baud: the controller initiates the high-speed path and the device replies
with `BYTE_ACK`. The device must still include its 115200-baud `CMD_SPEED`
information in the following registration sequence.

MicroPUP does not attempt to decode the fast probe while RX is still configured
as GPIO. Instead, it recognizes the measured fast waveform, enables UART without
discarding received bytes, and sends the required acknowledgement. This is why
the GPIO detection, UART handoff and first `0x04` must remain together in one
native primitive.

## Native GPIO implementation

The primitive closes an existing secondary UART, selects the LMS-ESP32 pins,
and generates the five-millisecond LPF2 identification pulse.

The GPIO selection is identical to the existing `serialOpen()` implementation:

| Board | RX GPIO | TX GPIO |
|---|---:|---:|
| LMS-ESP32 v1 | 18 | 19 |
| LMS-ESP32 v2 | 8 | 7 |

The version is obtained with `getESPVersion()`.

## Native fast-pulse implementation

The primitive examines up to 25 pulses returned by the hub. It ignores the
initial eleven pulses and selects fast UART when it measures a clearly short
high pulse:

```cpp
if ((pulse > 10) && sawHigh && (lastHighTime < 15000)) {
    fastDetected = true;
}
```

The threshold uses microseconds. An earlier 16000-microsecond threshold caused
a normal pulse measured at 15960 microseconds to be accepted accidentally. A
15000-microsecond limit provides a margin between the approximately 16 ms normal
pulses and the approximately 14 ms fast-selection pulse observed in testing.

If no fast pulse is detected, the primitive does not open UART and does not send
registration data. The MicroBlocks process will try again after its reconnect
timeout. There is intentionally no 2400-baud fallback.

## Atomic UART handoff

After detecting the fast pulse, the primitive:

1. Calls the existing internal `serialOpen(115200)` function. This uses the same
   version-dependent pins shown above.
2. Leaves UART RX enabled during a 5 ms settling interval.
3. Sends byte `0x04` as the fast-start acknowledgement.
4. Flushes UART TX before returning to MicroBlocks.

It bypasses `primSerialOpen()`, so received bytes are not discarded.

## LPF2 device registration

When the native result reports success, `micropup_fast.ubl` sends the standard
LPF2 registration sequence at 115200 baud:

| Registration item | Purpose |
|---|---|
| `TYPE` (`0x40`) | Announces the configured sensor/device type ID. |
| `MODES` (`0x49`) | Announces the highest mode and view indices. |
| `SPEED` (`0x52`) | Declares 115200 baud in little-endian form. |
| `VERSION` (`0x5F`) | Supplies protocol/firmware version information. |
| Mode information | Supplies name, ranges, units, mapping and data format. |
| `ACK` (`0x04`) | Marks the end of registration. |
| Initial data (`C0 00 3F`) | Supplies a valid initial value for mode 0. |

Although UART is already operating at 115200, the `SPEED` message is retained
because it is part of the LPF2 registration information expected by the hub.

Each MicroBlocks `add command` block creates one LPF2 mode. Consequently, one
`add command` block produces a one-mode device in the Pybricks device listing.
Commands must be added after `init` and before the continuous `process` loop is
started. Only ordinary modes 0 through 7 are used; extended mode numbering is
not implemented or required by this library.

## Runtime communication

The runtime protocol is inherited from the original MicroPUP library:

- Hub heartbeat/NACK byte `0x02` refreshes the connection timer.
- Mode-select and write messages update the current mode and pass data to the
  associated MicroBlocks command or reporter.
- Sensor data packets use the LPF2 data header, power-of-two payload sizing and
  XOR checksum.
- Byte, 16-bit signed integer and 32-bit integer payload formats remain
  supported through the `b`, `h` and `i` command types.
- If no valid hub traffic is received for four seconds, the library starts a
  new native fast-handshake attempt.

## Native primitive result and debugging

`serial:pupFastOpen` returns a six-item list:

```text
[detected, pulse_number, high_time_us, detection_time_ms, rx_gpio, tx_gpio]
```

`micropup_fast.ubl` exposes this list through the `fast handshake status`
reporter.

| Position | Meaning |
|---:|---|
| 1 | `1` when the fast-selection pulse was detected; otherwise `0`. |
| 2 | Number of the last pulse examined. |
| 3 | Duration of its high period in microseconds. |
| 4 | Total GPIO detection time in milliseconds. |
| 5 | RX GPIO selected by `getESPVersion()`. |
| 6 | TX GPIO selected by `getESPVersion()`. |

Example from a successful LMS-ESP32 v2 connection:

```text
[1, 22, 14160, 384, 8, 7]
```

This means that the fast pulse was detected at pulse 22, its high time was
14.160 ms, detection took 384 ms, and GPIO8/GPIO7 were used.

The `PUP connected` reporter returns the library's local connection flag. It is
set after the registration sequence has been transmitted. Seeing the device and
its modes in Pybricks is the stronger confirmation that the hub accepted the
registration.

## Installation

1. Add `primSerialPUPFastOpen()` to the `#if defined(LMS_ESP32)` section of
   `vm/serialPrims.cpp`. The supplied patch places it there under an additional
   `#if defined(ESP32_ORIGINAL)` guard.
2. Add the primitive table entry:

   ```cpp
   {"pupFastOpen", primSerialPUPFastOpen},
   ```

3. Rebuild the LMS-ESP32 SmallVM firmware and flash it to the board.
4. Import `micropup_fast.ubl` into MicroBlocks.
5. Run `init`, add one or more commands, and then run `process` continuously.
6. Start or recreate the Pybricks `PUPDevice` after MicroPUP begins its attach
   sequence.

The library will report an unknown primitive if it is used with an older
SmallVM firmware that does not contain `serial:pupFastOpen`.

## Troubleshooting

| Symptom/status | Interpretation |
|---|---|
| First status item is `0` | No valid fast pulse was found. Check wiring, hub port state and GPIO selection. |
| Detection near 15900-16000 us | Normal pulse; ensure the firmware uses the corrected `< 15000` test. |
| Status ends in `8, 7` | LMS-ESP32 v2 pins were selected. |
| Status ends in `18, 19` | LMS-ESP32 v1 pins were selected. |
| Handshake succeeds but no device appears | Inspect Pybricks registration logging and confirm at least one `add command` ran before `process`. |
| Only one mode appears | Only one command was registered; each command maps to one LPF2 mode. |
| Primitive is unknown | Rebuild and flash SmallVM with the new primitive table entry. |

## Scope of the changes

The changes are deliberately limited:

- The timing-sensitive physical attach and initial `0x04` are native C++.
- LPF2 metadata, checksums, modes and application payloads remain in the `.ubl`
  library and follow the original MicroPUP implementation.
- No 2400-baud startup or fallback remains in `micropup_fast.ubl`.
- No extended-mode feature was added.
- The original `micropup.ubl` was not modified.

## Protocol references

- [Pybricks Powered Up UART protocol notes](https://github.com/pybricks/technical-info/blob/master/uart-protocol.md)
  describe the information-message order, acknowledgements, heartbeat NACK and
  newer 115200-baud synchronization.
- [Pybricks LUMP message definitions](https://github.com/pybricks/pybricks-micropython/blob/master/lib/lego/lego/lump.h)
  define `BYTE_ACK`, `BYTE_NACK`, TYPE, MODES, SPEED and the other UART message
  identifiers.
- The repository's `lpf2.py` `connect()` method is the direct implementation
  reference for the 5 ms sensor hello and measured fast-start waveform.
