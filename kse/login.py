__all__ = ['login']
import uuid
def login(msg, param):
    if msg['method'] == 'GET':
        body = param['db'].blob('$resource', 'login')
        body = body.replace(b'$Title$',b'KSE')
        msg = {'AUTH': 1,
            'text': 'OK',
            'body': body,
            }
        return msg, param
    else:
        if msg['body']:
            userinfo = [i.split('=',1)[1] for i in msg['body'].split('&')]
            if len(userinfo) == 2:
                try:
                    pwd = param['db'].select('$user', ['pwd'], ['id', userinfo[0]])[0][0]
                except:
                    body = param['db'].blob('$resource', 'login')
                    body = body.replace(b'\xe3\x80\x80', b'Invalid username or password')
                    body = body.replace(b'$Title$',b'KSE')
                    msg = {'AUTH': 1,
                        'text': 'OK',
                        'body': body,
                        }
                    return msg, param
                if pwd == userinfo[1]:
                    token = str(uuid.uuid4())
                    for key in list(param['token']):
                        if param['token'][key] == userinfo[0]:
                            param['token'].pop(key)
                    param['token'][token] = userinfo[0]
                    body = param['db'].blob('$resource', 'index')
                    body = body.replace(b'$Title$',b'KSE - ' + userinfo[0].encode())
                    addr = 'ws://'+param['ip'] + ':' + str(param['port']) + '/ws'
                    body = body.replace(b'$ws$', addr.encode())
                    msg = {'AUTH': 1,
                        'text': 'OK',
                        'Set-Cookie': 'token=' + token,
                        'body': body}
                    return msg, param
                else:
                    body = param['db'].blob('$resource', 'login')
                    body = body.replace(b'\xe3\x80\x80', b'Invalid username or password')
                    body = body.replace(b'$Title$',b'KSE')
                    msg = {'AUTH': 1,
                        'text': 'OK',
                        'body': body,
                        }
                    return msg, param
            else:
                if userinfo[1] != userinfo[2]:
                    body = param['db'].blob('$resource', 'register')
                    body = body.replace(b'\xe3\x80\x80', b'Password and confirm password does not match')
                    body = body.replace(b'$Title$',b'KSE')
                    msg = {'AUTH': 1,
                        'text': 'OK',
                        'body': body,
                        }
                    return msg, param
                else:
                    param['db'].insert('$user', userinfo[:2])
                    body = param['db'].blob('$resource', 'login')
                    body = body.replace(b'\xe3\x80\x80', b'Registered successfully')
                    body = body.replace(b'$Title$',b'KSE')
                    msg = {'AUTH': 1,
                        'text': 'OK',
                        'body': body,
                        }
                    return msg, param
                