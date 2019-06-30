from datetime import datetime


class LogEntry:
    def __init__(self, command, id):
        self.command = command
        self.response = None
        self.id = id

        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None

    def add_response(self, response):
        self.response = response
        self.end_time = datetime.now()
        self.duration = self.get_duration()

    def get_duration(self):
        diff = self.end_time - self.start_time
        return diff.total_seconds()

    @property
    def __response__(self):
        return self.response

    def got_response(self):
        if self.response is None:
            return False
        else:
            return True

    def __repr__(self):
        str = ''
        str += '\nid: %s\n' % self.id
        str += 'command: %s\n' % self.command
        str += 'response: %s\n' % self.response
        str += 'start time: %s\n' % self.start_time
        str += 'end_time: %s\n' % self.end_time
        str += 'duration: %s\n' % self.duration
        return str
