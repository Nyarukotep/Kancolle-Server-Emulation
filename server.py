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

async def client(conn, addr):
    print('connection start')
    req = http.Request()
    while req.length:
        recv = await loop.sock_recv(conn, 1024)
        req.reqdec(recv)
    req.debug()
    resp = b'HTTP/1.1 Hello World\r\n\r\n<h1>Hello World</h1>'
    await loop.sock_sendall(conn, resp)
    conn.close()
    print('close')

async def accon(svr):
    while True:
        conn, addr = await loop.sock_accept(svr)
        await loop.create_task(client(conn,addr))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 3000))
server.listen()
loop = asyncio.get_event_loop()
loop.run_until_complete(accon(server))