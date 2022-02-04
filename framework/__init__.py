from .http import *
#from .websocket import *
def id(i,addr):
    cat={
        1:Request,
    }
    msg = cat.get(i,Request)
    return msg(addr)