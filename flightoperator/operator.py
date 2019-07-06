from drone.tello import Tello
import os
from datetime import datetime
import socket
import threading


class Operator:

    def __init__(self):
        self.swarm = []

        self.path_to_log = 'log'
        self.start_time = datetime.now().isoformat().replace(':', '-')

        self.MAX_COMMAND_RETRIES = 3

    def __del__(self):
        self.close()
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

    def remove_drone(self, tello):
        '''
        Remove the given drone to the swarm
        '''
        tello.close_connection()
        self.swarm.remove(tello)
        print('✅  Removed drone ' + tello.tello_ip)

    def execute_command(self, command):
        '''
        Execute the command on each drone in parallel. The execution is started in threads for each drone. The script is blocked until all drones executed the command or are removed from the swarm.
        '''
        # Execute commands as thread for each drone
        threads = []
        for tello in self.swarm:
            thread = threading.Thread(target=self._send_command_to_drone,
                                      args=(tello, command))
            thread.start()
            threads.append(thread)

        # Wait for drones to finish execution
        for thread in threads:
            thread.join()

    def _send_command_to_drone(self, tello, command):
        '''
        Sends command to the given drone. If drone is disconnected execution is skipped. Tries to execute self.MAX_COMMAND_RETRIES times. If no response is received the drone is removed from the swarm.
        '''
        # Skip execution if tello is disconnected
        if not tello.state.is_connected:
            print('❌  Tello ' + tello.tello_ip +
                  ' is disconnected. Command not sent')
            self.remove_drone(tello)
            return

        # Execute command and retry MAX_COMMAND_RETRIES times
        counter = 0
        while not tello.send_command(command).success() and counter < self.MAX_COMMAND_RETRIES:
            counter += 1

        # If the execution fails try to land drone and change state
        if counter == self.MAX_COMMAND_RETRIES:
            print('❌  Execution failed. Landing ' + tello.tello_sn)
            tello.send_command('land')
            self.remove_drone(tello)

    def register_drone(self, ip, wifi='operator', password='dronella'):
        '''
        Register drone with the given ssid and password to the given access point.
        '''
        tello = Tello(ip)
        while not tello.send_command('ap ' + wifi + ' ' + password).success():
            print('Drone not found. Retrying...')
        print('✅  Registered drone ' + tello.tello_sn + ' to ' + wifi)

    def scan_for_drones(self):
        '''
        Get the current ip network and check each ip address if its a drone. Started with 253 separate threads to speed up the process. Checks if abyss server on port 9999 is available.
        '''

        ip_address = socket.gethostbyname(socket.gethostname())

        network_prefix = ''
        for segment in ip_address.split('.')[0:3]:
            network_prefix += segment
            network_prefix += '.'

        # Start scan for all adresses in subnet 255.255.255.0
        threads = []
        for i in range(2, 254):
            address = (network_prefix + str(i), 9999)
            thread = threading.Thread(
                target=self._try_add_drone, args=(address,), daemon=True)
            thread.start()
            threads.append(thread)

        # Wait for all threads to terminate
        for thread in threads:
            thread.join()

    def _try_add_drone(self, address):
        '''
        Check if ip address is a tello drone by establishing a connection to the abyss server on port 99999. If it is available add it to the swarm.
        '''

        # Create socket
        ping_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ping_socket.settimeout(1)

        # Test if abyss server of drone is available
        if ping_socket.connect_ex(address) == 0:
            self.swarm.append(Tello(address[0]))

        # Close connection
        ping_socket.close()

    def land_swarm(self):
        '''
        Send the land command to all drones
        '''
        self.execute_command('land')

    def close(self):
        '''
        End the socket connection to each drone
        '''
        self.land_swarm()
        for tello in self.swarm:
            tello.close_connection()
            del tello

    def save_log(self):
        '''
        Print the log for each drone to the stdout and save it to the log path
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
