__all__ = ['Request']
class Request:
    def __init__(self):
        self.method = ''
        self.url = ''
        self.version = ''
        self.connection = ''
        self.length = -1
        self.type = ''
        self.cache = ''
        self.header = dict()
        self.body = ''
        self.websocket = 0

    def hdict(self, temp):
        key, value = temp.split(': ', 1)
        self.header[key] = value
        if key == 'Connection': self.connection = value
        if key == 'Content-Length': self.length = int(value)
        if key == 'Content-Type': self.type = value

    def parse(self, buffer):
        self.cache = self.cache + buffer.decode()
        while '\r\n' in self.cache and not self.body:
            line, self.cache = self.cache.split('\r\n', 1)
            if not self.method:
                self.method, self.url, self.version = line.split()
            elif line:
                self.hdict(line)
            elif not line:
                if self.length < 0:
                    self.length = 0
                else:
                    self.body = self.body + self.cache[:self.length]
                    self.length = self.length - len(self.cache)
                    self.cache = ''
        if self.body:
            self.body = self.body + self.cache[:self.length]
            self.length = self.length - len(self.cache)
            self.cache = ''
    
    def error(self):
        self.method = self.method

    def debug(self):
        print('\n'.join(['%s:%s' % item for item in self.__dict__.items()]))