import asyncio, numpy, socket
import framework as prot
import emulation as kse
#Request
#method url version
#GET /images/logo.png HTTP/1.1
#Host: hostname
#request req response rsp Client clnt permconn
#Response:
# HTTP/1.1 200 OK
#version status phrase header body
class server:
    def __init__(self, ip = 'localhost', port = 11456):
        self.ip = ip
        self.port = port
        self.timeout = 5
        self.loop = asyncio.new_event_loop()
    
    def start(self, func = kse.asg):
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
        print('Start server at %s:%d' %(self.ip, self.port))
        self.loop.run_until_complete(self.listen())
    
    async def listen(self):
        while True:
            conn, addr = await self.loop.sock_accept(self.server)
            self.loop.create_task(self.connection(conn,addr))
    
    async def connection(self,conn,addr):
        print(addr,'Start connection')
        tag = 0
        #tag, 0: standard; 1: websocket
        while True:
            t = self.timeout
            mfc = prot.id(tag,addr) #message from client
            while mfc.header.get('Content-Length',1):
                try:
                    buffer = await asyncio.wait_for(self.recv(conn),t)
                except asyncio.TimeoutError:
                    print(addr, 'Connection close due to timeout')
                    conn.close()
                    return
                if buffer:
                    mfc.parse(buffer)
                else:
                    conn.close()
                    print(addr, 'Connection closed by client')
                    return
            print(mfc)
            mtc = self.func(mfc)
            await self.loop.sock_sendall(conn, mtc)
            print(addr, 'Complete response')
            if mfc.header.get('Connection','None') != 'keep-alive':
                print(addr, 'Connection close')
                break
            print(addr, 'Connection reuse')
        conn.close()
        print(addr, 'Connection close')


    async def recv(self,conn):
        data = await self.loop.sock_recv(conn,1024)
        return data
s=server()
s.start(kse.asg)