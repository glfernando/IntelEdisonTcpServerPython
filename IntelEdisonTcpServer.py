import SocketServer
import mraa
import json
import sys

class IntelEdisonThreadedServer(SocketServer.BaseRequestHandler):
    def setup(self):
        print (self.client_address, 'connected!')

    def handle(self):
        while 1:
            if handle_request(self.request) == 0:
                return

    def finish(self):
        print (self.client_address, 'disconnected!')

# GPIO_PATH='/sys/kernel/debug/gpio_debug/'

def gpio_handler(n, d, v):
    # Use mraa library instead of sysfs
    x = mraa.Gpio(n)
    if d == 'out':
        x.dir(mraa.DIR_OUT)
        x.write(v)
    elif d == 'in':
        x.dir(mraa.DIR_IN)
    else:
        print "Invalid dir option" # this should never happen

def gpio_parser(j):
    print (json.dumps(j, sort_keys=True, indent=4, separators=(',', ':')))
    gpio_handler(j['num'], j['dir'], j['value'])

def json_parser(j):
    if 'type' in j:
        if j['type'] == 'gpio':
            gpio_parser(j)
        else:
            print 'type ' + j['type'] + ' no supported'
        return j


def handle_request(request):
    data = request.recv(1024)
    if not data: return 0
    f = data.makefile()
    for l in f.readlines():
        print (json.dumps(l, sort_keys=True, indent=4, separators=(',', ':')))
        json.loads(l, object_hook=json_parser)

    return 1


if len(sys.argv) > 1 :
    port = sys.argv[1]
else:
    port = "8086" #default port

# start server forever
SocketServer.ThreadingTCPServer(('', int(port)), IntelEdisonThreadedServer).serve_forever()
