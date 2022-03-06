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
        print('Start connection')
        while True:
            httpmsg = http(self.loop, self.conn, self.addr, self.timeout)
            try:
                await httpmsg.recv() #message from client
            except:
                conn.close()
                return
            print(httpmsg())
            msg, self.param = self.func(httpmsg(), self.param)
            ws_push = msg.pop('ws_push',0)
            await httpmsg.send(msg)
            if ws_push:
                for key in ws_push:
                    if self.param['ws_list'].get(key, 0):
                        print('key:',key)
                        print('wspushkey', ws_push[key])
                        wsrsp = wssend(self.loop, {}, ws_push[key])
                        await wsrsp.send(self.param['ws_list'][key])
            print('Complete response')
            if httpmsg().get('Upgrade',0) == 'websocket':
                self.loop.create_task(self.wsconn(conn, addr))
                self.debug(str(addr) + 'Start websocket connection')
                return
            elif httpmsg().get('Connection','None') != 'keep-alive':
                break
            self.debug(str(addr) + 'Connection reuse')
        conn.close()
        self.debug(str(addr) + 'Connection close')
    
    async def wsconn(self, conn, addr):
        self.debug(str(addr) + 'Start websocket connection')
        self.param['ws_list'][addr] = conn
        print('WS:', self.param['ws_list'])
        ws = websocket(self.loop, conn, addr)
        while True:
            try:
                await ws.recv()
            except:
                msg, self.param = self.func({'exit':1}, self.param)
                self.param = ws.exit(self.param)
                return
            print(ws())
            if ws()['opcode'] == 8:
                msg, self.param = self.func({'exit':1}, self.param)
                self.param = ws.exit(self.param)
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
                    msg, self.param = self.func({'exit':1}, self.param)
                    self.param = ws.exit(self.param)
                    return

    async def wswait(self, ws, msg):
        conn = ws.conn
        addr = ws.addr
        while addr in self.param['ws_list']:
            msg, self.param = self.func(msg, self.param)
            if msg.get('body',0):
                await wssend(self.loop, conn, addr, msg)
            if msg.get('ws_wait',0):
                await asyncio.sleep(msg.get('WSPUSH',0))
            else:
                return
        print('end ws push')
    
    def debug(self, c):
        if self.param.get('DEBUG', 1):
            print(c)