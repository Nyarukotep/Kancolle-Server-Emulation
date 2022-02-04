def asg(mfc):
    cat={
        1:test,
    }
    mtc = cat.get(1,test)
    return mtc()
 
def test():
    str='成功'
    str = str.encode('unicode-escape')
    msg = b'HTTP/1.1 Hello World\r\n'\
        b'Connection: keep-alive\r\n'\
        b'Content-Length: 20\r\n\r\n'\
        b'<h1>Hello World</h1>'
    return msg