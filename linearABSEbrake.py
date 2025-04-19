
# -----------------------------------------------------------------------------
# Project Name: Racing Simulator-RC Controller
# Author: bitsbits [https://www.youtube.com/@bits-bits]
# License: Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
#
# You are free to use, modify, and share this code for non-commercial purposes,
# provided you credit the original author. Commercial use of this code or any
# derivatives is not permitted without explicit permission.
#
# For full license details, see: https://creativecommons.org/licenses/by-nc/4.0/
# -----------------------------------------------------------------------------

import pygame
import serial
import serial.tools.list_ports
import time

# -------------------------------
# ABS and Brake Smoothing Config
# -------------------------------
BRAKE_DECEL_RATE = 3500    # Max deceleration rate (units/sec)
ENABLE_ABS       = True    # Toggle ABS simulation
ABS_FREQUENCY    = 20      # Pulses per second for ABS
ABS_DUTY_CYCLE   = 0.75    # Fraction of each pulse where brakes are applied

def apply_braking_smooth(current_throttle, brake_target, dt, now, brake_val):
    """
    Ramp current_throttle down to brake_target at BRAKE_DECEL_RATE.
    When ABS engaged (brake_val >= 1400), pulse per ABS_FREQUENCY & duty cycle.
    """
    decel = BRAKE_DECEL_RATE * dt
    if ENABLE_ABS and brake_val >= 1400:
        period = 1.0 / ABS_FREQUENCY
        if (now % period) >= (ABS_DUTY_CYCLE * period):
            return current_throttle
    if current_throttle > brake_target:
        return max(current_throttle - decel, brake_target)
    return brake_target

def select_serial_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found. Plug in your Arduino.")
        return None
    print("Available serial ports:")
    for i, p in enumerate(ports):
        print(f"{i}: {p.device} — {p.description}")
    idx = int(input("Select the Arduino port index: "))
    return ports[idx].device

def main():
    # Open serial
    port = select_serial_port()
    if not port:
        return
    try:
        ser = serial.Serial(port, 57600, timeout=1)
        print(f"Serial opened on {port}")
    except Exception as e:
        print(f"Failed to open {port}: {e}")
        return

    # Init Pygame & joystick
    pygame.init()
    count = pygame.joystick.get_count()
    if count == 0:
        print("No joystick detected.")
        return
    print("Available joysticks:")
    for i in range(count):
        js = pygame.joystick.Joystick(i)
        js.init()
        print(f"{i}: {js.get_name()}")
    idx = int(input("Select joystick index to use: "))
    j = pygame.joystick.Joystick(idx)
    j.init()
    print("Joystick initialized. Press Ctrl+C to exit.")

    engine_output = 0
    neutral = 1000
    last_time = time.time()

    while True:
        pygame.event.pump()
        now = time.time()
        dt = now - last_time
        last_time = now

        # Axes
        x_axis = int(j.get_axis(0) * 1000) if j.get_numaxes() > 0 else 0
        y_axis = int(j.get_axis(1) * 1000) if j.get_numaxes() > 1 else 0
        z_axis = int(j.get_axis(4) * 1000) if j.get_numaxes() > 4 else 0

        # Paddles
        leftpaddle  = int(j.get_button(5)) if j.get_numbuttons() > 5 else 0
        rightpaddle = int(j.get_button(4)) if j.get_numbuttons() > 4 else 0

        # Linear throttle/brake
        thr = neutral - y_axis
        brk = neutral - z_axis
        combined = thr if thr > brk else -brk
        combined = int(combined / 2)

        # ABS/brake smoothing
        if combined < 0:
            engine_output = apply_braking_smooth(engine_output, combined, dt, now, brk)
        else:
            engine_output = combined

        # Handbrake (axis 6)
        try:
            hb = j.get_axis(6)
        except:
            hb = 1.0
        if hb <= 0.5:
            frac = (0.5 - hb) / 1.5
            engine_output = int(-250 - 750 * frac)

        # Pots
        left_pot  = int(j.get_axis(6) * 1000) if j.get_numaxes() > 6 else 0
        right_pot = int(j.get_axis(7) * 1000) if j.get_numaxes() > 7 else 0

        # Switches (use same button IDs)
        swE = (-1 if j.get_button(87)
               else 0 if j.get_button(86)
               else 1 if j.get_button(85)
               else -1)
        swB = (-1 if j.get_button(90)
               else 0 if j.get_button(89)
               else 1 if j.get_button(88)
               else -1)
        swC = (-1 if j.get_button(94)
               else 0 if j.get_button(93)
               else 1 if j.get_button(92)
               else -1)
        swF = (-1 if j.get_button(78)
               else 0 if j.get_button(77)
               else 1 if j.get_button(76)
               else -1)

        # Build & send
        out = (
            f"{int(engine_output)},{x_axis},0,0,"
            f"{leftpaddle},{rightpaddle},"
            f"{left_pot},{right_pot},"
            f"{swE},{swB},{swC},{swF}\n"
        )
        print(out.strip())
        ser.write(out.encode())

        time.sleep(0.01)

if __name__ == "__main__":
    main()
