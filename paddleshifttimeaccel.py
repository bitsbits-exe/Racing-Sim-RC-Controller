
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

def select_serial_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found. Make sure your Arduino is plugged in.")
        return None
    print("Available serial ports:")
    for i, p in enumerate(ports):
        print(f"{i}: {p.device} — {p.description}")
    idx = int(input("Select the Arduino port index: "))
    return ports[idx].device

def main():
    # Serial‑port selection by index
    serial_port = select_serial_port()
    if not serial_port:
        return
    try:
        ser = serial.Serial(serial_port, 115200, timeout=1)
        print(f"Opened serial connection on {serial_port}")
    except Exception as e:
        print(f"Could not open serial port {serial_port}: {e}")
        return

    # Initialize Pygame and require at least one joystick
    pygame.init()
    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        print("No joysticks detected. Please connect your controller.")
        return

    print("Available joysticks:")
    for i in range(joystick_count):
        js = pygame.joystick.Joystick(i)
        js.init()
        print(f"{i}: {js.get_name()}")

    # Single joystick for all controls
    idx = int(input("Select joystick index for all controls: "))
    j = pygame.joystick.Joystick(idx)
    j.init()

    print("Controller initialized. Press Ctrl+C to exit.")

    # Gear and acceleration setup
    gear = 1
    max_gear = 6
    acceleration_durations = [0, 0.65, 0.9, 1.25, 1.875, 2.3, 2.5]
    right_paddle_pressed = False
    left_paddle_pressed = False
    combined_output_current = 0
    combined_output_target = 0
    acceleration_start_time = None
    acceleration_duration = acceleration_durations[gear]
    interpolation_start_value = 0

    while True:
        pygame.event.pump()

        # Steering, throttle, brake from axes 0, 1, 4
        try:
            x_axis = int(j.get_axis(0) * 1000)
        except:
            x_axis = 0
        try:
            y_axis = int(j.get_axis(1) * 1000)
        except:
            y_axis = 0
        try:
            z_axis = int(j.get_axis(4) * 1000)
        except:
            z_axis = 0

        # Paddle buttons for shifting (buttons 5=downshift, 4=upshift)
        try:
            leftpaddle = int(j.get_button(5))
        except:
            leftpaddle = 0
        try:
            rightpaddle = int(j.get_button(4))
        except:
            rightpaddle = 0

        # Compute raw combined output
        neutral = 1000
        thr = neutral - y_axis
        brk = neutral - z_axis
        combined = thr if thr > brk else -brk
        combined = int(combined / 2)

        # Gear shifting with debouncing
        if rightpaddle and not right_paddle_pressed:
            if gear < max_gear:
                gear += 1
                acceleration_duration = acceleration_durations[gear]
                acceleration_start_time = time.time()
                interpolation_start_value = combined_output_current
            right_paddle_pressed = True
        elif not rightpaddle:
            right_paddle_pressed = False

        if leftpaddle and not left_paddle_pressed:
            if gear > 1:
                gear -= 1
                acceleration_duration = acceleration_durations[gear]
                acceleration_start_time = time.time()
                interpolation_start_value = combined_output_current
            left_paddle_pressed = True
        elif not leftpaddle:
            left_paddle_pressed = False

        # Apply gear ratio
        if combined > 0:
            combined_output_target = int(combined * (gear / max_gear))
        else:
            combined_output_target = combined

        # Interpolate acceleration / immediate braking
        if combined < 0:
            combined_output_current = combined_output_target
            acceleration_start_time = None
        elif combined > 0:
            if combined_output_current < 0:
                combined_output_current = 0
                acceleration_start_time = time.time()
                interpolation_start_value = 0
            if acceleration_start_time is None:
                acceleration_start_time = time.time()
                interpolation_start_value = combined_output_current
            elapsed = time.time() - acceleration_start_time
            frac = min(elapsed / acceleration_duration, 1.0)
            combined_output_current = int(
                interpolation_start_value + (combined_output_target - interpolation_start_value) * frac
            )
            if frac >= 1.0:
                acceleration_start_time = None
        else:
            combined_output_current = combined_output_target

        # Potentiometers on axes 6 and 7
        try:
            left_pot = int(j.get_axis(6) * 1000)
        except:
            left_pot = 0
        try:
            right_pot = int(j.get_axis(7) * 1000)
        except:
            right_pot = 0

        # Build and send message:
        # combined_output_current, x_axis, 0, 0, leftpaddle, rightpaddle, left_pot, right_pot, gear
        msg = (
            f"{combined_output_current},{x_axis},0,0,"
            f"{leftpaddle},{rightpaddle},{left_pot},{right_pot},{gear}\n"
        )
        print(msg.strip())
        ser.write(msg.encode())

if __name__ == "__main__":
    main()
