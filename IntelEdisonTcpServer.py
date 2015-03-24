import SocketServer
import mraa
import json
import sys

dic = {"Intel":"Edison"}

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
    if 'gpio'+str(n) in dic:
        x = dic['gpio'+str(n)]
    else:
        x = mraa.Gpio(n)
        if d == 'out':
            x.dir(mraa.DIR_OUT)
        else:
            x.dir(mraa.DIR_IN)
        dic['gpio'+str(n)] = x
    x.write(v)

def gpio_parser(j):
    print (json.dumps(j, sort_keys=True, indent=4, separators=(',', ':')))
    gpio_handler(j['num'], j['dir'], j['value'])


def pwm_handler(n, p, v):
    if 'pwm'+str(n) in dic:
        pwm = dic['pwm' + str(n)]
    else:
        pwm = mraa.Pwm(n)
        dic['pwm'+str(n)] = pwm
        pwm.period_us(p)
        pwm.enable(True)

    pwm.write(v)
    return pwm

def pwm_parser(j):
    print (json.dumps(j, sort_keys=True, indent=4, separators=(',', ':')))
    pwm = pwm_handler(j['num'], j['period'], j['value'])
    return pwm

def json_parser(j):
    if 'type' in j:
        if j['type'] == 'gpio':
            gpio_parser(j)
        elif j['type'] == 'pwm':
            pwm = pwm_parser(j)
        else:
            print 'type ' + j['type'] + ' no supported'
        return j

def handle_request(request):
    data = request.recv(1024)
    if not data: return 0
    print (json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))
    json.loads(data, object_hook=json_parser)

    return 1

if len(sys.argv) > 1 :
    port = sys.argv[1]
else:
    port = "8086" #default port

# start server forever
SocketServer.ThreadingTCPServer(('', int(port)), IntelEdisonThreadedServer).serve_forever()
