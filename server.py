import asyncio, numpy, socket

async def client(conn, addr):
    print('connection start')
    #data = await loop.sock_recv(client, 1024)
    resp = b'HTTP/1.1 Hello World\r\n\r\n<h1>Hello World</h1>'
    await loop.sock_sendall(conn, resp)
    conn.close()

async def server():
    while True:
        conn, addr = await loop.sock_accept(server)
        await loop.create_task(client(conn,addr))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 3000))
server.listen(8)
loop = asyncio.get_event_loop()
loop.run_until_complete(server())