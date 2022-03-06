import asyncio
from .websocket import wstoken
__all__ = ['httpreq', 'httprsp']
class httpreq:
    def __init__(self, addr):
        self.data = {}
        self.data['addr'] = addr
        self.cache = ''
    async def recv(self, loop, conn, timeout):
        while self.data.get('Content-Length',1):
            try:
                buffer = await asyncio.wait_for(self.sock_recv(loop, conn),timeout)
            except asyncio.TimeoutError:
                print(self.data['addr'], 'Connection close due to timeout')
                raise Exception
            if buffer:
                self.parse(buffer)
            else:
                print(self.data['addr'], 'Connection closed by client')
                raise Exception
    async def sock_recv(self, loop, conn):
        msg = await loop.sock_recv(conn,1024)
        return msg

    def parse(self, buffer):
        self.cache = self.cache + buffer.decode()
        while '\r\n' in self.cache and 'body' not in self.data:
            line, self.cache = self.cache.split('\r\n', 1)
            if 'version' not in self.data:
                self.data['method'], self.data['target'], self.data['version'] = line.split()
                if '?' in self.data['target']:
                    self.data['target'], temp = self.data['target'].split('?',1)
                    self.data['query'] = {}
                    args=temp.split('&')
                    for arg in args:
                        k,v=arg.split('=')
                        self.data['query'][k]=v
            elif line:
                k, v = line.split(': ', 1)
                if v.isdigit():
                    self.data[k] = int(v)
                else:
                    if k == 'Cookie':
                        self.data[k] = {}
                        args=v.split('&')
                        for arg in args:
                            a,b=arg.split('=')
                        self.data[k][a]=b
                    else:
                        self.data[k] = v
            elif not line:
                self.data['Content-Length'] = self.data.get('Content-Length', 0)
                t = self.data['Content-Length']
                self.data['body'] = self.cache[:t]
                self.data['Content-Length'] = self.data['Content-Length'] - len(self.cache[:t])
                self.cache = self.cache[t:]
        if 'body' in self.data:
            t = self.data['Content-Length']
            self.data['body'] = self.data['body'] + self.cache[:t]
            self.data['Content-Length'] = self.data['Content-Length'] - len(self.cache[:t])
            self.cache = self.cache[t:]

    def __repr__(self):
        return '\nRequest content\n'+\
            '\n'.join(['%s: %s' % item for item in self.data.items()])

class httprsp:
    def __init__(self, msg, dreq):
        self.data = {'version': 'HTTP/1.1',
                     'code': '200',
                     'text': 'OK'}
        self.data['Connection'] = dreq.get('Connection', 'close')
        self.data.update(msg)
        if 'Sec-WebSocket-Key' in dreq:
            self.data.pop('body')
            self.wsrsp(dreq['Sec-WebSocket-Key'])
        else:
            self.data['Content-Type'] = 'Content-Type: text/html; charset=utf-8'
    def wsrsp(self,key):
        self.data['code'] = '101'
        self.data['text'] = 'Switching Protocols'
        self.data['Connection'] = 'Upgrade'
        self.data['Sec-WebSocket-Accept'] = wstoken(key)
        self.data['Upgrade'] = 'websocket'

    async def send(self, loop, conn):
        if self.data.pop('AUTH', 0):
            rsp = ''
            rsp += ' '.join([self.data.pop(k) for k in ['version', 'code', 'text']])
            rsp += '\r\n'
            if 'body' in self.data:
                body = self.data.pop('body')
                self.data['Content-Length'] = len(body)
                rsp += '\r\n'.join(['%s: %s' % item for item in self.data.items()])
                rsp += '\r\n\r\n'
                rsp = rsp.encode() + body
            else:
                rsp += '\r\n'.join(['%s: %s' % item for item in self.data.items()])
                rsp += '\r\n\r\n'
                rsp = rsp.encode()
        else:
            rsp = b'HTTP/1.1 404\r\n'\
                  b'Connection: keep-alive\r\n'\
                  b'Content-Length: 22\r\n\r\n'\
                  b'<h1>404 not found</h1>'
        await loop.sock_sendall(conn, rsp)
    def __repr__(self):
        return '\nResponse content\n'+\
            '\n'.join(['%s: %s' % item for item in self.data.items()])