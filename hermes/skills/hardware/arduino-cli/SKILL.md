---
name: arduino-cli
description: "Use when flashing Arduino sketches via arduino-cli."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  commands: [arduino-cli]
metadata:
  hermes:
    tags: [Arduino, Embedded, Hardware, Upload, Serial]
---

# Arduino CLI (compile + upload sketches)

Flash code to an attached Arduino or compatible board from the terminal.

## When to use

Any request to "upload/flash this sketch to my Arduino", or to build/verify Arduino
code against real hardware.

## Workflow

Run these in order. Do not skip step 1 — never assume the board model.

### 1. Identify the board and the port

```bash
arduino-cli board list
```

Output gives the port, the detected **Board Name**, the **FQBN**, and the core
namespace, for example:

```
Port         Protocol Type              Board Name          FQBN                          Core
/dev/ttyACM0 serial   Serial Port (USB) Arduino UNO R4 WiFi arduino:renesas_uno:unor4wifi arduino:renesas_uno
```

If the board is unknown, check the USB ID too:

```bash
lsusb | grep -iE "arduino|ch340|ftdi|2341"
```

### 2. Install the core

`board list` resolves the FQBN from a built-in USB VID/PID table, so it can name
a board whose core is **not installed**. Always confirm:

```bash
arduino-cli core list        # "No platforms installed." means install it
arduino-cli core update-index
arduino-cli core install arduino:renesas_uno
```

The first core install pulls a large toolchain (arm-none-eabi-gcc is ~95 MB) and
needs a long timeout — allow 10+ minutes.

Common cores: `arduino:avr` (Uno/Nano/Mega), `arduino:renesas_uno` (UNO R4),
`arduino:samd` (MKR/Zero), `arduino:mbed_nano` (Nano 33).

Third-party cores (ESP32, ESP8266, RP2040) need their board-manager URL first:

```bash
arduino-cli config add board_manager.additional_urls <url>
arduino-cli core update-index
arduino-cli core install esp32:esp32
```

### 3. Fix serial permissions on Linux (the usual blocker)

A permission problem surfaces as this — note the message blames the port reset, not
your setup:

```
Cannot perform port reset: 1200-bps touch: opening port at 1200bps: Permission denied
No device found on ttyACM0
Failed uploading: uploading error: exit status 1
```

That means permissions. Check ownership and groups:

```bash
ls -l /dev/ttyACM0     # typically crw-rw---- root:uucp (Arch) or root:dialout (Debian)
groups                 # is your user in that owning group?
```

Fixes, in order of preference:

```bash
sudo usermod -aG uucp $USER      # Arch/CachyOS. Persistent, needs log out + back in.
sudo usermod -aG dialout $USER   # Debian/Ubuntu equivalent.
sudo chown $USER /dev/ttyACM0    # Immediate, this session only; resets on replug.
```

`groups` in the current shell will NOT show a newly added group until you re-login,
but a `chown` takes effect at once. If `sudo` needs a password, ask the user to run
the command themselves — never accept a password in chat.

### 4. Compile

The sketch directory name must match the `.ino` filename (`button_led/button_led.ino`).
Build by pointing at the directory:

```bash
cd ~/Arduino/button_led
arduino-cli compile --fqbn arduino:renesas_uno:unor4wifi .
```

Success looks like:

```
Sketch uses 52040 bytes (19%) of program storage space. Maximum is 262144 bytes.
Global variables use 6740 bytes (20%) of dynamic memory...
```

Compiling proves nothing about hardware access — do it before uploading so a
permission failure is not confused with a code error.

### 5. Upload

```bash
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:renesas_uno:unor4wifi .
```

Success:

```
Erase flash
Write 52048 bytes to flash (13 pages)
[==============================] 100% (13/13 pages)
Done in 3.108 seconds
New upload port: /dev/ttyACM0 (serial)
```

"New upload port" means the board re-enumerated after reset. A successful upload is
NOT yet proof the code behaves correctly — verify on hardware (step 6).

### 6. Verify on hardware

Open the serial monitor at the sketch's baud rate:

```bash
arduino-cli monitor -p /dev/ttyACM0 --config baudrate=9600
```

Then ask the user to trigger the code path (press the button, cover the sensor) and
confirm the expected line appears. **An empty monitor is not a failed flash** — it
means the sketch printed nothing, e.g. a `digitalRead`-gated `Serial.println` while
the pin is low. Say so rather than reporting failure.

## Pitfalls

- **FQBN shown by `board list` != core installed.** Verify with `core list`.
- **Arch's serial group is `uucp`**, not `dialout`. Deb-based distros use `dialout`.
- **A group add needs a fresh login**; `chown` on the device node works immediately.
- **`arduino-cli monitor` can exit instantly with code 0 and no output** when started
  without a TTY. Give it a pseudo-terminal (`pty=true` in Hermes terminal) and run it
  in the background, or fall back to `python -m serial.tools.miniterm`.
- **`INPUT` without a pull-down/up resistor floats.** A sketch using
  `pinMode(pin, INPUT)` and `digitalRead()` will flood serial with a constant "pressed"
  message and blink the LED on, even with nothing wired to the pin. Prefer
  `INPUT_PULLUP` plus a button wired to GND (read active-LOW), or fit a real pull-down
  resistor. Continuous output from an `INPUT` pin is the floating-input signature, not
  a stuck button.
- **Sketch folder name must equal the `.ino` name**, otherwise the build fails.
- **Classic-Uno code usually runs unchanged on an UNO R4** for plain digital pins,
  but `LED_BUILTIN`/pin 13, PWM capability, and analog behavior differ. R4 WiFi =
  `arduino:renesas_uno:unor4wifi`, R4 Minima = `arduino:renesas_uno:unor4minima`.
- **`Serial.begin(9600)` on a native-USB board (R4, Leonardo, Micro)** does not wait
  for the host; early output before the monitor attaches is dropped.
- The `-v` flag on upload/compile prints the full toolchain commands when debugging.
- Hermes writes scratch files under `${HERMES_SCRATCH:-~/.hermes/cache/scratch}`; keep
  generated sketches in the user's `~/Arduino/` tree instead so they persist.
