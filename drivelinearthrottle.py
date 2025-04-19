
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

def select_serial_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found. Make sure your Arduino is plugged in.")
        return None
    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} — {port.description}")
    idx = int(input("Select the Arduino port index: "))
    return ports[idx].device

def main():
    # Serial‑port selection by index
    serial_port = select_serial_port()
    if not serial_port:
        return
    try:
        ser = serial.Serial(serial_port, 57600, timeout=1)
        print(f"Opened serial on {serial_port}")
    except Exception as e:
        print(f"Failed to open {serial_port}: {e}")
        return

    # Initialize Pygame & detect joysticks
    pygame.init()
    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        print("No joysticks found.")
        return

    print("Available joysticks:")
    for i in range(joystick_count):
        js = pygame.joystick.Joystick(i)
        js.init()
        print(f"{i}: {js.get_name()}")

    primary_index = int(input("Select joystick index for driving controls: "))
    primary = pygame.joystick.Joystick(primary_index)
    primary.init()

    use_secondary = input("Use a second joystick for extra controls? (y/n): ").lower().startswith('y')
    if use_secondary:
        secondary_index = int(input("Select joystick index for additional controls: "))
        secondary = pygame.joystick.Joystick(secondary_index)
        secondary.init()
    else:
        secondary = None

    print("Running... Ctrl+C to quit.")
    while True:
        pygame.event.pump()

        # Primary axes/buttons
        x_axis = int(primary.get_axis(0) * 1000) if primary.get_numaxes() > 0 else 0
        y_axis = int(primary.get_axis(1) * 1000) if primary.get_numaxes() > 1 else 0
        z_axis = int(primary.get_axis(2) * 1000) if primary.get_numaxes() > 2 else 0
        leftpaddle  = int(primary.get_button(0)) if primary.get_numbuttons() > 0 else 0
        rightpaddle = int(primary.get_button(1)) if primary.get_numbuttons() > 1 else 0

        # Secondary for pots & switches
        if secondary:
            left_pot  = int(secondary.get_axis(0) * 1000) if secondary.get_numaxes() > 0 else 0
            right_pot = int(secondary.get_axis(1) * 1000) if secondary.get_numaxes() > 1 else 0
            # buttons 0/1 → switch E, 2/3 → B, 4/5 → C, 6/7 → F
            swE =  1 if secondary.get_button(0) else (-1 if secondary.get_button(1) else 0)
            swB =  1 if secondary.get_button(2) else (-1 if secondary.get_button(3) else 0)
            swC =  1 if secondary.get_button(4) else (-1 if secondary.get_button(5) else 0)
            swF =  1 if secondary.get_button(6) else (-1 if secondary.get_button(7) else 0)
        else:
            left_pot = right_pot = 0
            swE = swB = swC = swF = 0

        # Combine throttle/brake
        neutral = 1000
        thr = neutral - y_axis
        brk = neutral - z_axis
        combined = int((thr if thr>brk else -brk) / 2)

        # Build & send
        msg = f"{combined},{x_axis},0,0,{leftpaddle},{rightpaddle},{left_pot},{right_pot},{swE},{swB},{swC},{swF}\n"
        print(msg.strip())
        ser.write(msg.encode())

if __name__ == "__main__":
    main()
