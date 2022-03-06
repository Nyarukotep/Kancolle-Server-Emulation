__all__ = ['wstoken', 'wsrecv', 'wssend']
import base64,hashlib
from cmath import exp
import asyncio

def wstoken(wskey):
    GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    wskey = wskey + GUID
    return base64.b64encode(hashlib.sha1(wskey.encode('utf-8')).digest()).decode()

class wsrecv:
    def __init__(self, loop, addr):
        self.data = {}
        self.data['addr'] = addr
        self.loop = loop
        self.cache = b''
        self.body = ''
    
    async def recv(self, conn):
        while True:
            while self.data.get('length',1):
                buffer = await self.loop.sock_recv(conn,1024)
                if buffer:
                    self.parse(buffer)
                else:
                    print('Connection closed by client')
                    raise Exception
            self.unmask()
            if self.data['FIN'] == 1: break
            else:
                self.reset()
        self.data['body'] = self.body

    def parse(self, buffer):
        self.cache = self.cache + buffer
        if 'KEY' not in self.data:
            try:
                x = self.cache[1] & 127
            except:
                return
            if x < 126: start, end, hlen, max = 1, 2, 6, 127
            elif x == 126: start, end, hlen, max = 2, 4, 8, 65535
            else: start, end, hlen, max = 2, 10, 14, 18446744073709551615
            if len(self.cache) >= hlen:
                    self.data['FIN'] = (self.cache[0] >> 7) & 1
                    self.data['RSV'] = (self.cache[0] >> 4) & 7 #7:0b0111
                    self.data['opcode'] = self.data.get('opcode',self.cache[0] & 15) #15:0b1111
                    self.data['MASK'] = (self.cache[1] >> 7) & 1
                    self.data['length'] = int(self.cache[start:end].hex(),16) & max
                    self.data['KEY'] = self.cache[end:hlen]
                    self.data['body'] = self.cache[hlen:hlen + self.data['length']]
                    self.data['length'] -= len(self.data['body'])
                    self.cache = b''
            else: return
        else:
            t = self.data['length']
            self.data['body'] += self.cache[:t]
            self.data['length'] -= len(self.cache[:t])
            self.cache = self.cache[t:]

    def unmask(self):
        msg = b''
        for i in range(len(self.data['body'])):
            msg += bytes.fromhex('{0:0{1}x}'.format(self.data['body'][i] ^ self.data['KEY'][i%4],2))
        self.body += msg.decode()

    def reset(self):
        self.data.pop('length')
        self.data.pop('KEY')
        self.data.pop('body')
        self.cache = b''

    def __repr__(self):
        return 'Data:\n\t' + '\n\t'.join(['%s:%s' % item for item in self.data.items()])\
            + '\nBody:\n\t'+self.body\
            + '\ncache:\n\t'+ repr(self.cache)

class wssend:
    def __init__(self, loop, wsreq, upg):
        self.loop = loop
        self.data = {'FIN': 0b1,
                'RSV': 0b000,
                'opcode':0b1,
                'body': b'',
                }
        if upg:
            self.data.update(upg)
        else:
            if wsreq['opcode'] == 9:
                self.data['opcode'] == 10
            else:
                self.data['body'] = b'exit'

    async def send(self, conn):
        if self.data.pop('AUTH', 1):
            msg = b''
            fstr = (((self.data['FIN']<<3)^self.data['RSV'])<<4)^self.data['opcode']
            msg += bytes.fromhex('{0:0{1}x}'.format(fstr, 2))
            body = self.data['body']
            if len(body) < 126:
                msg += bytes.fromhex('{0:0{1}x}'.format(len(body), 2))
            elif len(body) < 65536:
                msg += b'\x7e'
                msg += bytes.fromhex('{0:0{1}x}'.format(len(body), 4))
            else:
                msg += b'\x7f'
                msg += bytes.fromhex('{0:0{1}x}'.format(len(body), 16))
            msg += body
            print(msg)
            await self.loop.sock_sendall(conn, msg)
        else:
            err = b'HTTP/1.1 404\r\n'\
                  b'Connection: keep-alive\r\n'\
                  b'Content-Length: 22\r\n\r\n'\
                  b'<h1>404 not found</h1>'
            await self.loop.sock_sendall(conn, err)