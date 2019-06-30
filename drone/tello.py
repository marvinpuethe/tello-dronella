import socket
import threading
import time
from drone.logentry import LogEntry
from drone.state import State
from drone.response import Response


class Tello:
    def __init__(self, tello_ip='192.168.10.1', send_keepalives=True):

        # Server information
        self.local_ip = ''
        self.local_port = 8889
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket.bind((self.local_ip, self.local_port))

        # Drone information
        self.tello_ip = tello_ip
        self.tello_port = 8889
        self.tello_address = (self.tello_ip, self.tello_port)
        self.tello_sn = None

        # Thread for receiving command acknowledges
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # Drone state
        self.state = State(self.tello_address)

        # Log storage
        self.log = []

        # Maximum time to wait for an acknowledgement. Otherwise abort the flight.
        self.MAX_TIME_OUT = 10.0

        # Initialize drone
        if not self.send_command('command').success():
            print('Initialization failed. Check if you can reach the drone at %s' %
                  self.tello_ip)
            return
        self.tello_sn = self.send_command('sn?').returnvalue

        # Thread for keep-alive-messages
        self.KEEPALIVE_INTERVAL = 5.0
        self.send_keepalives = send_keepalives
        self.keepalive_thread = threading.Thread(target=self._keepalive_thread)
        self.keepalive_thread.daemon = True
        self.keepalive_thread.start()

    @property
    def __tello_address__(self):
        return self.tello_address

    @__tello_address__.setter
    def __tello_address__(self, tello_address):
        self.tello_address = tello_address
        self.state.tello_address = tello_address

    @property
    def __local_port__(self):
        return self.local_port

    @__local_port__.setter
    def __local_port__(self, local_port):
        self.local_port = local_port

    @property
    def __local_ip__(self):
        return self.local_ip

    @__local_ip__.setter
    def __local_ip__(self, local_ip):
        self.local_ip = local_ip
        self.state.local_ip = local_ip

    @property
    def __state__(self):
        return self.state

    @__state__.setter
    def __state__(self, state):
        self.state = state

    @property
    def __log__(self):
        return self.log

    def send_command(self, command):
        '''
        Send a command to the tello drone. Will be blocked until the last command receives an 'OK'. If the command fails (either b/c time out or error), will try to send a  land command
        :param command: (str) the command to send
        '''

        # If we try to receive the serial number return the stored value if it exists
        if command == 'sn?' and self.tello_sn != None:
            print('Serial Number: %s' % self.tello_sn)
            return Response('b\'' + self.tello_sn)

        # Stores the current command and an id in the log
        self.log.append(LogEntry(command, len(self.log)))

        # Send command as utf-8 to the specified tello address
        self.socket.sendto(command.encode(
            'utf-8'), self.tello_address)
        print('Sending command: %s to %s' %
              (command, self.tello_ip))

        # Start timer and wait for response
        start = time.time()
        while not self.log[-1].got_response():
            now = time.time()
            diff = now - start

            # If the maximum timeout is reached try to land the drone
            if diff > self.MAX_TIME_OUT:
                print('❗ Max timeout exceeded ❗\nCommand %s' % command)

                # Land drone to avoid damage
                self.socket.sendto('land'.encode(
                    'utf-8'), self.tello_address)
                print('Trying to land drone\nBe careful!')
                return None

        if self.log[-1].response.success:
            print('Succeeded command %s to %s ✔' % (command, self.tello_ip))
        else:
            print('Failed command %s to %s ❌' % (command, self.tello_ip))

        return self.log[-1].response

    def close_connection(self):
        self.send_keepalives = False
        print('Waiting for threads to terminate...')
        self.keepalive_thread.join(self.KEEPALIVE_INTERVAL)

    def enable_missionpads(self):
        if self.send_command('mon') != -1:
            self.state.missionpads_enabled = True

    def disable_missionpads(self):
        if self.send_command('moff') != -1:
            self.state.missionpads_enabled = False

    def _keepalive_thread(self):
        '''
        Send dummy command to the drone to keep the connection alive.
        Runs as a thread
        '''
        while self.send_keepalives:
            command = 'sn?'
            self.socket.sendto(command.encode(
                'utf-8'), self.tello_address)
            time.sleep(self.KEEPALIVE_INTERVAL)

    def _receive_thread(self):
        '''
        Listen to responses from the Tello.
        Runs as a thread, sets self.response to whatever the Tello last returned.
        '''

        while True:
            try:
                response, ip = self.socket.recvfrom(1024)
            except socket.error as exc:
                print("⚠ Caught exception socket.error : %s" % exc)

            self.response = Response(response)

            # Skip output if keepalive message was sent
            if (self.response.returnvalue == self.tello_sn):
                continue

            print('from %s: %s' % (ip, self.response))
            self.log[-1].add_response(self.response)
