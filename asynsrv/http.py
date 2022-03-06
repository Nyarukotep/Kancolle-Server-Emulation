import asyncio
import base64,hashlib
__all__ = ['http']
class http:
    def __init__(self, loop, conn, addr, timeout):
        self.loop = loop
        self.conn = conn
        self.timeout = timeout
        self.data = {}
        self.data['type'] = 'http'
        self.data['addr'] = addr
        self.cache = ''

    def __call__(self):
        return self.data

    async def recv(self):
        while self.data.get('Content-Length',1):
            try:
                buffer = await asyncio.wait_for(self.sock_recv(self.loop, self.conn), self.timeout)
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

    async def send(self, msg):
        if msg:
            if 'Sec-WebSocket-Key' in self.data:
                wskey = self.data['Sec-WebSocket-Key']
                GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
                wskey += GUID
                wstoken = base64.b64encode(hashlib.sha1(wskey.encode('utf-8')).digest()).decode()
                self.data = {
                    'version': 'HTTP/1.1',
                    'code': '101',
                    'text':'Switching Protocols',
                    'Connection': 'Upgrade',
                    'Sec-WebSocket-Accept': wstoken,
                    'Upgrade': 'websocket',
                }
            else:
                connection = self.data.get('Connection', 'close')
                self.data = {
                    'version': 'HTTP/1.1',
                    'code': '200',
                    'text': 'OK',
                    'Connection': connection,
                }
                self.data.update(msg)
        else:
            self.data = {
                'version': 'HTTP/1.1',
                'code': '404',
            }
        rsp = ''
        rsp += ' '.join([self.data.pop(k) for k in ['version', 'code', 'text']])
        rsp += '\r\n'
        if 'body' in self.data:
            body = self.data.pop('body')
            if isinstance(body, str): body = body.encode()
            self.data['Content-Length'] = len(body)
            rsp += '\r\n'.join(['%s: %s' % item for item in self.data.items()])
            rsp += '\r\n\r\n'
            rsp = rsp.encode() + body
        else:
                rsp += '\r\n'.join(['%s: %s' % item for item in self.data.items()])
                rsp += '\r\n\r\n'
                rsp = rsp.encode()
        await self.loop.sock_sendall(self.conn, rsp)