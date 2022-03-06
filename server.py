import asynsrv, kse
import time
param = {'db': kse.database('data.db'),
        'token':{},
        'ws_token':{}
        }
s=asynsrv.server(kse.route,param, 10)
s.start('localhost', 6655)