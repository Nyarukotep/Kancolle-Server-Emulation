import http
from .database import database
from .login import login
import uuid
def route(msg, param):
    print('114514', param['WSTOKEN'])
    msg_type = pid(msg)
    cat = {
        'hypertext': hypertext,
        'protupgrade': protupgrade,
        'websocket': websocket,
    }
    func = cat.get(msg_type, hypertext)
    return func(msg, param)

def pid(msg):
    if 'version' in msg:
        if msg.get('Upgrade', 0) == 'websocket':
            return 'protupgrade'
        else:
            return 'hypertext'
    else:
        return 'websocket'

def hypertext(msg, param):
    user = cookie(msg, param)
    if user:
        cat = {
            '/': newconn,
            '/background.png': resource,
            '/favicon.ico': resource,
            '/UDShinGoPro_Regular.woff2': resource,
        }
        func = cat.get(msg['target'], newconn)
        return func(msg, param)
    else:
        cat = {
            '/': login,
            '/favicon.ico': resource,
            '/UDShinGoPro_Regular.woff2': resource,
        }
        func = cat.get(msg['target'], redirect)
        return func(msg, param)
    
def protupgrade(msg, param):
    print('accept wsup')
    user = cookie(msg, param)
    if user:
        param['WSTOKEN'][msg['Cookie']['token']] = msg['addr']
        msg = {'AUTH': 1,
        'body':b''
        }
    return msg, param

def websocket(msg, param):
    msg = {'body':msg['body'].encode()}
    return msg, param

def cookie(msg, param):
    if 'Cookie' not in msg:
        return 0
    else:
        token = msg['Cookie']['token']
        if token in param['USER']:
            return param['USER'][token]
        else:
            return 0

def redirect(msg, param):
    msg = {'AUTH': 1,
        'code': '303',
        'text': 'See Other',
        'Location': '/',
        }
    return msg, param

def newconn(msg, param):
    oldtoken = msg['Cookie']['token']
    wsaddr = param['WSTOKEN'][oldtoken]
    param['WSCONN'][wsaddr].close()
    newtoken = str(uuid.uuid4())
    param['USER'][newtoken] = param['USER'].pop(oldtoken)
    body = param['db'].blob('$resource', 'index')
    body = body.replace(b'$Title$',b'KSE - ' + param['USER'][newtoken].encode())
    addr = 'ws://'+param['SVRIP'] + ':' + str(param['SVRPORT'])
    body = body.replace(b'$ws$', addr.encode())
    msg = {
        'AUTH': 1,
        'text': 'OK',
        'Set-Cookie': 'token=' + newtoken,
        'body': body,
    }
    print('WSCONN1',param['WSCONN'])
    print('WSTOKEN1',param['WSTOKEN'])
    print('user1',param['USER'])
    return msg, param

def resource(msg, param):
    file_name = msg['target'].rsplit("/",1)[1]
    file_type = file_name.rsplit(".",1)[1]
    cat = {
        'png': 'image/png',
        'ico': 'image/x-icon',
        'woff2': 'font/woff2',
    }
    msg = {'AUTH': 1,
        'text': 'OK',
        'Content-Type': cat.get(file_type, 'text/html; charset=UTF-8'),
        'body': param['db'].blob('$resource', file_name),
        }
    return msg, param


def test():
    str='成功'
    str = str.encode('unicode-escape')
    msg = b'HTTP/1.1 Hello World\r\n'\
        b'Connection: keep-alive\r\n'\
        b'Content-Length: 20\r\n\r\n'\
        b'<h1>Hello World</h1>'
    return msg