import asyncio, numpy, socket
import framework.http as http
#Request
#method url version
#GET /images/logo.png HTTP/1.1
#Host: hostname
#request req response rsp Client clnt permconn
#Response:
# HTTP/1.1 200 OK
#version status phrase header body
class server:
    def __init__(self, ip = 'localhost', port = 11455):
        self.ip = ip
        self.port = port
        self.timeout = 5
        self.loop = asyncio.new_event_loop()
    
    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen()
        self.server.setblocking(False)
        print(self.port)
        self.loop.run_until_complete(self.listen())
    
    async def listen(self):
        while True:
            conn, addr = await self.loop.sock_accept(self.server)
            self.loop.create_task(self.access(conn,addr))
    
    async def access(self,conn,addr):
        print(addr,'Start connection')
        while True:
            t = self.timeout
            req = http.Request()
            while req.length:
                try:
                    buffer = await asyncio.wait_for(self.recv(conn),t)
                except asyncio.TimeoutError:
                    print(addr, 'Connection close due to timeout')
                    conn.close()
                    return
                if buffer:
                    req.parse(buffer)
                else:
                    conn.close()
                    print(addr, 'Connection closed by client')
                    return
            req.debug()
            resp = b'HTTP/1.1 Hello World\r\nConnection: keep-alive\r\nContent-Length: 20\r\n\r\n<h1>Hello World</h1>'
            await self.loop.sock_sendall(conn, resp)
            print(addr, 'Complete response')
            if req.connection != 'keep-alive':
                print(addr, 'Connection close')
                break
            print(addr, 'Connection reuse')
        conn.close()
        print(addr, 'Connection close')

    async def recv(self,conn):
        data = await self.loop.sock_recv(conn,1024)
        return data

s=server()
s.start()