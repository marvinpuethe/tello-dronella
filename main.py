from drone.tello import Tello
from flightoperator.operator import Operator
import sys
import time
import os


def execute_commands_from_file(command_file_name):
    print('Command file found. Executing script')
    f = open(command_file_name, 'r')
    commands = f.readlines()

    for command in commands:
        if command != '' and command != '\n':
            command = command.rstrip()

            if command.find('delay') != -1:
                sec = float(command.partition('delay')[2])
                print('✅  Delaying ' + sec)
                time.sleep(sec)
            else:
                operator.execute_command(command)


operator = Operator()

# Check if in single or multiflight mode
in_string = input(
    'Welcome! 👋\nWould you like to connect to multiple drones? (Y/n)\n')
if (in_string in ('y', 'Y', 'yes', '')):
    connect_to_multiple_drones = True
else:
    connect_to_multiple_drones = False

# Check if drones need to be registered
if (connect_to_multiple_drones):
    in_string = input('Are your drones already registered? (Y/n)\n')
    if (in_string not in ('y', 'Y', 'yes', '')):
        wifi = input('Which WiFi SSID should be used? (Empty for operator) ')
        if (wifi != ''):
            password = input(
                'Which WiFi password should be used? ')
        while (input('Connect to your drone wifi and press Enter (End with \'end\')') != 'end'):
            if wifi == '':
                operator.register_drone('192.168.10.1')
            else:
                operator.register_drone('192.168.10.1', wifi, password)
        input('Connect to the management wifi now and press Enter')

# Scan for drones on local network
while (operator.swarm == []):
    operator.scan_for_drones()

# Try to get the command file from argument list
command_file = 'command.txt'
try:
    command_file = sys.argv[2]
# If no parameter was given try standard file
except IndexError:
    print('No command file given by startupt. Trying command.txt')

# Check if command file has been found
if os.path.isfile(command_file):
    print('command.txt found. Executing...')
    execute_commands_from_file(command_file)

# If no command file has been given start in interactive mode
else:
    print('Command file not found. Starting in interactive mode\nExit with \'end\'')
    print('Ready for takeoff... 🚀\nTry typing takeoff:')

    while True:
        try:
            command = input()

        except KeyboardInterrupt:
            break

        if not command or 'end' in command:
            break

        # Send command to tello drone. If return is None end communication
        operator.execute_command(command)

operator.save_log()
