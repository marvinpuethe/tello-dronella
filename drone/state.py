import socket
import threading
import time


class State:

    def __init__(self):

        # Missionpad variables
        self.missionpads_enabled = False
        self.mid = None
        self.mx = None
        self.my = None
        self.mz = None
        self.mpry = None

        # Drone inflight information
        self.pitch = None
        self.roll = None
        self.yaw = None
        self.vgx = None
        self.vgy = None
        self.vgz = None
        self.agx = None
        self.agy = None
        self.agz = None

        # Temperature information
        self.templ = None
        self.temph = None

        # Position information
        self.tof_in_cm = None
        self.height = None

        # Drone information
        self.battery = None
        self.barometer = None
        self.motor_time = None

        self.local_ip = ''
        self.local_port = 0

        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)  # socket for receiving state
        self.socket.bind((self.local_ip, self.local_port))

        # thread for receiving state
        self.state_thread = threading.Thread(target=self._state_thread)
        self.state_thread.daemon = True
        self.state_thread.start()

    @property
    def __missionpads_enabled__(self):
        return self.missionpads_enabled

    @__missionpads_enabled__.setter
    def __missionpads_enabled__(self, missionpads_enabled):
        self.missionpads_enabled = missionpads_enabled

    @property
    def __mid__(self):
        return self.mid

    @property
    def __mx__(self):
        return self.mx

    @property
    def __my__(self):
        return self.my

    @property
    def __mz__(self):
        return self.mz

    @property
    def __mpry__(self):
        return self.mpry

    @property
    def __pitch__(self):
        return self.pitch

    @property
    def __roll__(self):
        return self.roll

    @property
    def __yaw__(self):
        return self.yaw

    @property
    def __vgx__(self):
        return self.vgx

    @property
    def __vgy__(self):
        return self.vgy

    @property
    def __vgz__(self):
        return self.vgz

    @property
    def __agx__(self):
        return self.agx

    @property
    def __agy__(self):
        return self.agy

    @property
    def __agz__(self):
        return self.agz

    @property
    def __templ__(self):
        return self.templ

    @property
    def __temph__(self):
        return self.temph

    @property
    def __tof_in_cm__(self):
        return self.tof_in_cm

    @property
    def __height__(self):
        return self.height

    @property
    def __battery__(self):
        return self.battery

    @property
    def __barometer__(self):
        return self.barometer

    @property
    def __motor_time__(self):
        return self.motor_time

    def _state_thread(self):
        '''
        Listen to the state of the Tello.
        Runs as a thread, sets self.state to whatever the Tello last returned.
        '''

        while True:
            try:
                response = self.socket.recvfrom(1024)

            except socket.error as exc:
                print('⚠ Caught exception socket.error : %s' % exc)

            statelist = str(response).split(';')

            # Remove first two characters
            statelist[0] = statelist[0][3:]

            stateswitcher = {
                'mid': 'mid',
                'x': 'mx',
                'y': 'my',
                'z': 'mz',
                'mpry': 'mpry',
                'pitch': 'pitch',
                'roll': 'roll',
                'yaw': 'yaw',
                'vgx': 'vgx',
                'vgy': 'vgy',
                'vgz': 'vgz',
                'agx': 'agx',
                'agy': 'agy',
                'agz': 'agz',
                'templ': 'templ',
                'temph': 'temph',
                'tof': 'tof_in_cm',
                'h': 'height',
                'bat': 'battery',
                'baro': 'barometer',
                'time': 'motor_time'
            }

            self.friendlyname = ''
            for entry in statelist:

                # Continue if the last attribute has been parsed
                if entry.startswith('\\r\\n\''):
                    continue

                # Set values to the corresponding attributes
                identifier = entry.split(':')[0]
                value = entry.split(':')[1]

                attribute = stateswitcher[identifier]

                setattr(self, attribute, value)
                self.friendlyname += identifier
                self.friendlyname += ' : '
                self.friendlyname += value
                self.friendlyname += '\n'

    def __repr__(self):
        return self.friendlyname
