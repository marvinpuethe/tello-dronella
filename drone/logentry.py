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
        string = ''
        string += 'id: ' + str(self.id)
        string += '\ncommand: ' + str(self.command)
        string += '\nresponse: ' + str(self.response)
        string += '\nstart time: ' + str(self.start_time)
        string += '\nend_time: ' + str(self.end_time)
        string += '\nduration: ' + str(self.duration)
        string += '\n'
        return string
