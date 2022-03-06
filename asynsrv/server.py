import asyncio, socket
from .http import http
from .websocket import websocket, wssend
__all__ = ['server']
class server:
    def __init__(self, func, param = {}, timeout = 10):
        self.func = func
        self.param = param
        self.timeout = timeout
        self.loop = asyncio.new_event_loop()
    
    def start(self, ip, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.server.bind((ip, port))
                break
            except OSError:
                port += 1
        self.server.listen()
        self.server.setblocking(False)
        self.param['ip'] = ip
        self.param['port'] = port
        self.param['ws_list'] = {}
        print('Start server at %s:%d' %(ip, port))
        self.loop.run_until_complete(self.listen())
    
    async def listen(self):
        while True:
            conn, addr = await self.loop.sock_accept(self.server)
            self.loop.create_task(self.httpconn(conn,addr))

    async def httpconn(self, conn, addr):
        print(addr, 'Start connection')
        while True:
            httpmsg = http(self.loop, conn, addr, self.timeout)
            try:
                await httpmsg.recv() #message from client
            except:
                conn.close()
                return
            print(addr, 'request: ', httpmsg())
            msg, self.param = self.func(httpmsg(), self.param)
            ws_push = msg.pop('ws_push',0)
            await httpmsg.send(msg)
            print(addr, 'response: ', httpmsg())
            if ws_push:
                for key in ws_push:
                    if self.param['ws_list'].get(key, 0):
                        print('key:',key)
                        print('wspushkey', ws_push[key])
                        await wssend(self.loop, self.param['ws_list'][key], key, ws_push[key])
            print('Complete response')
            if httpmsg().get('Upgrade',0) == 'websocket':
                self.loop.create_task(self.wsconn(conn, addr))
                print(addr, 'Start websocket connection')
                return
            elif httpmsg().get('Connection','None') != 'keep-alive':
                break
            print(addr, 'Connection reuse')
        conn.close()
        print(addr, 'Connection close')
    
    async def wsconn(self, conn, addr):
        print(addr, 'Start websocket connection')
        self.param['ws_list'][addr] = conn
        print('ws_list: ', self.param['ws_list'])
        ws = websocket(self.loop, conn, addr)
        while True:
            try:
                await ws.recv()
            except:
                msg, self.param = ws.exit(self.param)
                msg, self.param = self.func(msg, self.param)
                return
            print('ws recv: ', ws())
            if ws()['opcode'] == 8:
                msg, self.param = ws.exit(self.param)
                msg, self.param = self.func(msg, self.param)
                return
            elif ws()['opcode'] == 9:
                await ws.send()
            else:
                msg, self.param = self.func(ws(), self.param)
                if msg:
                    if 'ws_wait' in msg:
                        self.loop.create_task(self.wswait(ws, msg))
                        print('start wsph')
                    print(ws())
                    await ws.send(msg)
                else:
                    msg, self.param = ws.exit(self.param)
                    msg, self.param = self.func(msg, self.param)
                    return

    async def wswait(self, ws, msg):
        msg['type'] = 'wswait'
        conn = ws.conn
        addr = ws.addr
        while addr in self.param['ws_list']:
            msg, self.param = self.func(msg, self.param)
            if msg.get('body',0):
                await wssend(self.loop, conn, addr, msg)
            if msg.get('ws_wait',0):
                await asyncio.sleep(msg['ws_wait'])
            else:
                return
        print('end ws push')