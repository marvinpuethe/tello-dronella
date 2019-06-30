class Response:

    def __init__(self, response=None):
        if response == None:
            self.returncode = None
            self.returnvalue = None
        else:
            self.returncode = str(response)[0:1]
            self.returnvalue = str(response).split('\'')[1][:-4]

    @property
    def __returncode__(self):
        return self.returncode

    def success(self):
        return not self.returnvalue.startswith('e')

    @property
    def __returnvalue__(self):
        return self.returnvalue

    def __repr__(self):
        return self.returncode + ' / ' + self.returnvalue
