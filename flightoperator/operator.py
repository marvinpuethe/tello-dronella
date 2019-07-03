from drone.tello import Tello
import os
from datetime import datetime


class Operator:

    def __init__(self):
        self.swarm = []

        self.path_to_log = 'log'
        self.start_time = datetime.now().isoformat().replace(':', '-')

        self.MAX_COMMAND_RETRIES = 3

    def __del__(self):
        self.end_connection()
        self.save_log()

    def add_drone(self, tello):
        '''
        Add the given drone to the swarm
        '''
        self.swarm.append(tello)
        if self.swarm.index(tello) != -1:
            print('✅  Added drone ' + tello.tello_ip)
        else:
            print('❌  Failed to add drone ' + tello.tello_ip)

    def execute_command(self, command):
        '''
        Execute the command on each drone
        '''
        for tello in self.swarm:
            # TODO Execute command as thread

            # Skip execution if tello is disconnected
            if not tello.state.is_connected:
                # TODO Try to reconnect the drone
                print('❌  Tello ' + tello.tello_ip +
                      ' is disconnected. Command not sent')
                continue

            # Execute command and retry MAX_COMMAND_RETRIES times
            counter = 0
            while not tello.send_command(command).success() and counter < self.MAX_COMMAND_RETRIES:
                counter += 1

            # If the execution fails try to land drone and change state
            if counter == self.MAX_COMMAND_RETRIES:
                print('❌  Execution failed. Landing ' + tello.tello_sn)
                tello.send_command('land')
                tello.state.is_connected = False

    def register_drone(self, ip, wifi='operator', ap='dronella'):
        '''
        Register drone with the given op to the given access point
        '''
        tello = Tello(ip)
        if tello.send_command('ap ' + wifi + ' ' + ap).success():
            self.add_drone(tello)
        print('✅  Registered drone ' + tello.tello_sn + ' to ' + wifi)

    def land_swarm(self):
        '''
        Send the land command to all drones
        '''
        self.execute_command('land')
        self.end_connection()

    def end_connection(self):
        '''
        End the socket connection of each drone
        '''
        for tello in self.swarm:
            tello.close_connection()
            del tello
            self.swarm.remove(tello)

    def save_log(self):
        '''
        Print the log for each drone to the stdout
        '''
        if not os.path.isdir(self.path_to_log):
            os.mkdir(self.path_to_log)
        out = open('log' + os.path.sep + self.start_time + '.txt', 'w')

        for tello in self.swarm:
            log = tello.log
            print(tello.tello_sn)
            for entry in log:
                print(entry)
                out.write(str(entry))
