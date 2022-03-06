import asyncio, socket
from .http import httpreq, httprsp
from .websocket import wsrecv, wssend
__all__ = ['server']

class server:
    def __init__(self, ip = 'localhost', port = 6655):
        self.ip = ip
        self.port = port
        self.timeout = 5
        self.loop = asyncio.new_event_loop()
    
    def start(self, func, param = {}):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.server.bind((self.ip, self.port))
                break
            except OSError:
                self.port = self.port+1
        self.server.listen()
        self.server.setblocking(False)
        self.func = func
        self.param = param
        self.param['SVRIP'] = self.ip
        self.param['SVRPORT'] = self.port
        self.param['WSCONN'] = {}
        print('Start server at %s:%d' %(self.ip, self.port))
        self.loop.run_until_complete(self.listen())
    
    async def listen(self):
        while True:
            conn, addr = await self.loop.sock_accept(self.server)
            self.loop.create_task(self.httpconn(conn,addr))

    async def httpconn(self, conn, addr):
        self.debug(str(addr) + 'Start connection')
        while True:
            req = httpreq(addr)
            try:
                await req.recv(self.loop, conn, self.timeout) #message from client
            except:
                conn.close()
                return
            print(req)
            msg, self.param = self.func(req.data, self.param)
            phdict = msg.pop('WSPUSH',0)
            rsp = httprsp(msg, req.data)
            await rsp.send(self.loop, conn)
            if phdict:
                for key in phdict:
                    if self.param['WSCONN'].get(key, 0):
                        print('key:',key)
                        print('wspushkey', phdict[key])
                        wsrsp = wssend(self.loop, {}, phdict[key])
                        await wsrsp.send(self.param['WSCONN'][key])
            self.debug(str(addr) + 'Complete response')
            if rsp.data.get('Upgrade','None') == 'websocket':
                self.loop.create_task(self.wsconn(conn, addr, msg))
                self.debug(str(addr) + 'Start websocket connection')
                return
            elif rsp.data.get('Connection','None') != 'keep-alive':
                break
            self.debug(str(addr) + 'Connection reuse')
        conn.close()
        self.debug(str(addr) + 'Connection close')
    
    async def wsconn(self, conn, addr, msg):
        self.debug(str(addr) + 'Start websocket connection')
        self.param['WSCONN'][addr] = conn
        print('WS:', self.param['WSCONN'])
        while True:
            wsreq = wsrecv(self.loop, addr)
            try:
                await wsreq.recv(conn) #message from client
            except:
                conn.close()
                break
            print(wsreq)
            if wsreq.data['opcode'] == 9:
                wsrsp = wssend(self.loop, wsreq.data, {})
                await wsrsp.send(conn)
            else:
                msg, self.param = self.func(wsreq.data, self.param)
                if 'WSPUSH' in msg:
                    self.loop.create_task(self.wsph(conn, addr, msg))
                    print('start wsph')
                elif 'body' in msg:
                    wsrsp = wssend(self.loop, wsreq.data, msg)
                    await wsrsp.send(conn)
            if not msg:
                conn.close()
                break
            print(addr, 'Complete response')
        print(addr, 'websocket close')
        self.param['WSCONN'].pop(addr)
        key = self.param['WSTOKEN'].keys()
        for i in key:
            if self.param['WSTOKEN'][i] == addr:
                self.param['WSTOKEN'].pop(i)
        print('drop success',self.param['WSTOKEN'])
        

    async def wsph(self, conn, addr, msg):
        msg['addr'] = addr
        while 'WSPUSH' in msg and addr in self.param['WSCONN']:
            msg, self.param = self.func(msg, self.param)
            if 'body' in msg:
                wsrsp = wssend(self.loop, {}, msg)
                await wsrsp.send(conn)
            await asyncio.sleep(msg.get('WSPUSH',0))
        print('end ws push')
    
    def debug(self, c):
        if self.param.get('DEBUG', 1):
            print(c)