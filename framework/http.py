class Request:
    def __init__(self):
        self.method = ''
        self.url = ''
        self.version = ''
        self.connection = ''
        self.length = -1
        self.type = ''
        self.frame = ''
        self.cache = ''
        self.header = dict()
        self.body = ''

    def hdict(self, temp):
        key, value = temp.split(': ', 1)
        self.header[key] = value
        if key == 'Connection': self.connection = value
        if key == 'Content-Length': self.length = int(value)
        if key == 'Content-Type': self.type = value

    def reqdec(self, buffer):
        if not self.frame:
            self.cache = self.cache + buffer.decode()
            while '\r\n' in self.cache and not self.body:
                temp, self.cache = self.cache.split('\r\n', 1)
                if not self.method:
                    self.method, self.url, self.version = temp.split()
                elif temp:
                    self.hdict(temp)
                elif not temp and self.cache:
                    self.body = self.body + self.cache
                    self.length = self.length - len(self.cache)
                    self.cache = ''
                elif self.length:
                    self.length = 0
            if self.body:
                self.body = self.body + self.cache
                self.length = self.length - len(self.cache)
                self.cache = ''
        else:
            self.method = self.method
    
    def debug(self):
        print('\n'.join(['%s:%s' % item for item in self.__dict__.items()]))