from drone.tello import Tello
import sys
from datetime import datetime
import time
import os
import shutil

start_time = datetime.now().isoformat().replace(':', '-')
path_to_log = 'log'

file_name = ''
if len(sys.argv) >= 2:
    print('Using file %s' % sys.argv[1])
    file_name = sys.argv[1]
else:
    print('No parameter given. Trying to use command.txt')
    file_name = 'command.txt'

tello = Tello()

# Scripted mode
if os.path.isfile(file_name):

    print('command.txt found. Executing script')
    f = open(file_name, "r")
    commands = f.readlines()

    for command in commands:
        returncode = 0
        if command != '' and command != '\n':
            command = command.rstrip()

            if command.find('delay') != None:
                sec = float(command.partition('delay')[2])
                print('delay %s' % sec)
                time.sleep(sec)
                pass
            else:
                if tello.send_command(command) == None:
                    break

# Interactive mode
else:
    print('command.txt does not exist. Starting in interactive mode\nExit with \'end\'')
    print('Ready for takeoff... 🚀\nTry typing takeoff:')

    while True:
        try:
            command = input()
            if not command:
                break

            if 'end' in command:
                tello.send_command('land')
                break

            # Send command to tello drone
            if tello.send_command(command) == None:
                break

        except KeyboardInterrupt:
            tello.send_command('land')
            break

tello.close_connection()

# Save log to log-path
if not os.path.isdir(path_to_log):
    os.mkdir(path_to_log)
out = open('log' + os.path.sep + start_time + '.txt', 'w')

log = tello.log
for entry in log:
    print(entry)
    out.write(str(entry))
