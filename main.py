from drone.tello import Tello
from flightoperator.operator import Operator
import sys
import time
import os


def execute_commands_from_file(command_file_name):
    print('Command file found. Executing script')
    f = open(command_file_name, "r")
    commands = f.readlines()

    for command in commands:
        if command != '' and command != '\n':
            command = command.rstrip()

            if command.find('delay') != -1:
                sec = float(command.partition('delay')[2])
                print('delay %s' % sec)
                time.sleep(sec)
            else:
                operator.execute_command(command)


def get_swarm_file():
    '''
    Get the swarm file either from the argument list or as the standard file. If not file is found return None
    '''
    # Try to get the swarm file from argument list
    try:
        swarm_file = sys.argv[1]
    # If not try standard file
    except IndexError:
        swarm_file = 'swarm.txt'

    # If no parameter was given try standard file
    return swarm_file


def get_command_file():
    '''
    Get the command file either from the argument list or as the standard file. If not file is found return None
    '''
    # Try to get the command file from argument list
    try:
        command_file = sys.argv[2]
    # If no parameter was given try standard file
    except IndexError:
        command_file = 'command.txt'
    return command_file


def get_swarm_ips_from_keyboard():

    swarm_ips = []

    tello_ip = ''
    while (tello_ip != 'end'):
        tello_ip = input(
            'Swarm file not found. Specify drone ips (empty for single mode)\nExit input with \'end\'\n')

        if tello_ip == 'end':
            break

        if (tello_ip == '' and operator.swarm == None):
            swarm_ips.append('192.168.10.1')
            break

        swarm_ips.append(tello_ip)

    return swarm_ips


operator = Operator()

# Get drone ip adresses
swarm_file_name = get_swarm_file()
if (swarm_file_name == None):
    swarm_ips = get_swarm_ips_from_keyboard()
else:
    f = open(swarm_file_name, "r")
    ips = f.readlines()

    swarm_ips = []
    for ip in ips:
        swarm_ips.append(ip.rstrip())

# Add drones to swarm
for drone_ip in swarm_ips:
    operator.add_drone(Tello(drone_ip))

# Check for command file and execute if found
command_file_name = get_command_file()
if os.path.isfile(command_file_name):
    execute_commands_from_file(command_file_name)

# If no command file has been given start in interactive mode
else:
    print('Command file not found. Starting in interactive mode\nExit with \'end\'')
    print('Ready for takeoff... 🚀\nTry typing takeoff:')

    while True:
        try:
            command = input()

        except KeyboardInterrupt:
            operator.land_swarm()
            break

        if not command:
            break

        if 'end' in command:
            operator.land_swarm()
            break

        # Send command to tello drone. If return is None end communication
        operator.execute_command(command)

del operator
