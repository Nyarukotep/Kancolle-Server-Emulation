from .database import database
from .login import login
import uuid
def route(input, param):
    cat = {
        'http': hypertext,
        'websocket': websocket,
        'wswait': wswait,
    }
    func = cat.get(input['type'], hypertext)
    return func(input, param)

def hypertext(input, param):
    user = cookie(input, param)
    if user:
        cat = {
            '/': newconn,
            '/ws': protupgrade,
            '/logout': logout,
            '/background.png': resource,
            '/favicon.ico': resource,
            '/UDShinGoPro_Regular.woff2': resource,
        }
        func = cat.get(input['target'], newconn)
        return func(input, param)
    else:
        cat = {
            '/': login,
            '/favicon.ico': resource,
            '/UDShinGoPro_Regular.woff2': resource,
        }
        func = cat.get(input['target'], redirect)
        return func(input, param)

def protupgrade(input, param):
    user = cookie(input, param)
    if user:
        param['ws_token'][input['addr']] = user
        msg = {'AUTH': 1,
        'body':b'start'
        }
    return msg, param

def websocket(input, param):
    if input['body'] == 'exit':
        param['ws_token'].pop(input['addr'], 0)
        return {}, param
    else:
        msg = {'body':input['body'].encode()}
        if input['body'] == 'wstoken': print(param['ws_token'])
        if input['body'] == 'token': print(param['token'])
        return msg, param

def wswait():
    a=1

def cookie(input, param):
    if 'Cookie' not in input:
        return 0
    else:
        token = input['Cookie']['token']
        if token in param['token']:
            return param['token'][token]
        else:
            return 0

def redirect(input, param):
    msg = {'AUTH': 1,
        'code': '303',
        'text': 'See Other',
        'Location': '/',
        }
    return msg, param

def newconn(input, param):
    oldtoken = input['Cookie']['token']
    user = param['token'][oldtoken]
    ws_push = {}
    for key in param['ws_token']:
        if param['ws_token'][key] == user:
            ws_push[key] = {'body':b'exit',}
    newtoken = str(uuid.uuid4())
    param['token'][newtoken] = param['token'].pop(oldtoken)
    body = param['db'].blob('$resource', 'index')
    body = body.replace(b'$Title$',b'KSE - ' + param['token'][newtoken].encode())
    addr = 'ws://'+param['ip'] + ':' + str(param['port']) + '/ws'
    body = body.replace(b'$ws$', addr.encode())
    msg = {
        'AUTH': 1,
        'text': 'OK',
        'Set-Cookie': 'token=' + newtoken,
        'body': body,
    }
    if ws_push: msg['ws_push'] = ws_push
    return msg, param

def resource(input, param):
    file_name = input['target'].rsplit("/",1)[1]
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

def logout(input, param):
    token = input['Cookie']['token']
    user = param['token'].pop(token)
    ws_push = {}
    for key in param['ws_token']:
        if param['ws_token'][key] == user:
            ws_push[key] = {'body':b'exit',}
    msg = {'AUTH': 1,
        'code': '303',
        'text': 'See Other',
        'Location': '/',
        }
    if ws_push: msg['ws_push'] = ws_push
    return msg, param    