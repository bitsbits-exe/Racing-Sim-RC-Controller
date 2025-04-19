
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
        print(f"Could not open serial connection on {serial_port}: {e}")
        return

    # Initialize Pygame and check for joystick devices
    pygame.init()
    joystick_count = pygame.joystick.get_count()
    if joystick_count < 3:
        print("Less than 3 joystick devices found. Make sure your flight stick, throttle controls, and rudder are connected.")
        return

    print("Available joysticks:")
    for i in range(joystick_count):
        js = pygame.joystick.Joystick(i)
        js.init()
        print(f"{i}: {js.get_name()}")

    # Prompt user to select the joysticks for the three roles:
    flight_index   = int(input("Select index for flight stick (roll & pitch): "))
    throttle_index = int(input("Select index for throttle controls: "))
    rudder_index   = int(input("Select index for rudder (yaw): "))

    flight_stick   = pygame.joystick.Joystick(flight_index);   flight_stick.init()
    throttle_stick = pygame.joystick.Joystick(throttle_index); throttle_stick.init()
    rudder_stick   = pygame.joystick.Joystick(rudder_index);   rudder_stick.init()

    print("Starting joystick loop. Press Ctrl+C to exit.")

    while True:
        pygame.event.pump()

        # Flight stick inputs
        try:
            x_axis = int(flight_stick.get_axis(0) * 1000)      # Roll
        except:
            x_axis = 0
        try:
            y_axis = int(flight_stick.get_axis(1) * -1000)     # Pitch inverted
        except:
            y_axis = 0
        try:
            rightpaddle = int(flight_stick.get_button(19))     # Launch button
        except:
            rightpaddle = 0

        # Throttle stick inputs
        try:
            z_axis = int(throttle_stick.get_axis(3) * -1000)   # Throttle inverted
        except:
            z_axis = 0
        try:
            left_pot = int(throttle_stick.get_axis(6) * 1000)
        except:
            left_pot = 0
        try:
            right_pot = int(throttle_stick.get_axis(7) * -1000)
        except:
            right_pot = 0

        # Switch positions (E, B, C, F)
        swE_position = (-1 if throttle_stick.get_button(87)
                        else 0 if throttle_stick.get_button(86)
                        else 1 if throttle_stick.get_button(85)
                        else -1)
        swB_position = (-1 if throttle_stick.get_button(90)
                        else 0 if throttle_stick.get_button(89)
                        else 1 if throttle_stick.get_button(88)
                        else -1)
        swC_position = (-1 if throttle_stick.get_button(94)
                        else 0 if throttle_stick.get_button(93)
                        else 1 if throttle_stick.get_button(92)
                        else -1)
        swF_position = (-1 if throttle_stick.get_button(78)
                        else 0 if throttle_stick.get_button(77)
                        else 1 if throttle_stick.get_button(76)
                        else -1)

        # Air brake (invert original logic)
        try:
            leftpaddle = int(throttle_stick.get_button(18))
        except:
            leftpaddle = 0
        leftpaddle = 0 if leftpaddle == 1 else 1

        # Rudder stick input
        try:
            c_axis = int(rudder_stick.get_axis(0) * 1000)
        except:
            c_axis = 0

        # Compose and send the message:
        # x_axis, y_axis, z_axis, c_axis, leftpaddle, rightpaddle,
        # left_pot, right_pot, swE, swB, swC, swF
        msg = (
            f"{x_axis},{y_axis},{z_axis},{c_axis},"
            f"{leftpaddle},{rightpaddle},{left_pot},{right_pot},"
            f"{swE_position},{swB_position},{swC_position},{swF_position}\n"
        )
        print(msg.strip())
        ser.write(msg.encode())

if __name__ == "__main__":
    main()
