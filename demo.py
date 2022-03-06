import asynsrv
import time
def asg(req, param):
    if 'FIN' in req:
        if 'Time' in req['body']:
            msg = {'ws_wait':int(req['body'].split()[1]), 'body':b'time'}
            return msg, param
        else:
            msg = {'body':req['body'].encode()}
            return msg, param
    elif 'ws_wait' in req:
        return {'ws_wait':5,'PUSHID':1, 'body': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()).encode()},param
    elif 'exit' in req:
        return {}, param
    else:
        cat={
            '/':hw,
            '/ws':ws,
        }
        task = cat.get(req['target'], hw)
        return task(req, param)

def ws(reqd, param):
    body=template('ws.html')
    addr = 'ws://'+param['ip'] + ':' + str(param['port']) +'/ws114514'
    body = body.replace('$websocket$', addr)
    print(body)
    msg = {'AUTH': 1,
            'text': 'ws',
            'body': body.encode()}
    return msg, param

def hw(reqd, param):
    msg = {'AUTH': 1,
        'text': 'Hello World',
        'body': b'<h1>Hello World</h1>'}
    if param['ws_list']:
        wsdict = {}
        for key in param['ws_list']:
            wsdict[key] = {'body':b'helloworld'}
        msg['ws_push'] = wsdict
    return msg, param

def template(filename):
    f=open(filename,'r',encoding='utf-8')
    return f.read()

s=asynsrv.server(asg, {}, 10)
s.start('localhost', 6655)