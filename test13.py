#import RPi.GPIO as GPIO
import time
from tkinter import *
import os
from subprocess import Popen
from subprocess import PIPE
import threading
import sys,tty,termios
import socket
from flask import Flask, render_template, request, redirect, url_for, make_response
from multiprocessing import Process
from random import random

fd = sys.stdin.fileno()
oldtermios=termios.tcgetattr(fd)

#GPIO.setmode(GPIO.BOARD)

fini = False
direction = 0
origin = (0.53,0.33,0.54)
campos = 0.48

roues = [7,2]
camid = 15

ipattes = [[0 for i in range(3)] for j in range(6)]
pattes = [[0 for i in range(3)] for j in range(6)]
opattes = [[0 for i in range(3)] for j in range(6)]

ipattes[0][0] = 4
ipattes[0][1] = 17
ipattes[0][2] = 27

ipattes[1][0] = 22
ipattes[1][1] = 5
ipattes[1][2] = 11

ipattes[2][0] = 13
ipattes[2][1] = 19
ipattes[2][2] = 26


ipattes[3][0] = 18
ipattes[3][1] = 23
ipattes[3][2] = 24

ipattes[4][0] = 25
ipattes[4][1] = 8
ipattes[4][2] = 12

ipattes[5][0] = 16
ipattes[5][1] = 20
ipattes[5][2] = 21


#frequencyhertz = 50
#mspercycle = 1000/frequencyhertz

st = " --gpio "
for i in range(6):
    for j in range(3):
        #GPIO.setup(ipattes[i][j],GPIO.OUT)
        if i == 0 and j == 0:
            st+=str(ipattes[i][j])
        else:
            st+=","+str(ipattes[i][j])
        #pattes[i][j] = GPIO.PWM(ipattes[i][j],frequencyhertz)

        #pattes[i][j].start(30+j*10)
st+=","+str(roues[0])
st+=","+str(roues[1])
st+=","+str(camid)
os.system("sudo /etc/pi-blaster-master/pi-blaster"+st)

movelist = []


def movet(i,j,pos):
    global movelist
    movelist.append((i,j,pos))

def disablecam():
    st = 'sudo echo "'+str(camid)+'='+str(0)+'">/dev/pi-blaster'
    #Popen(st,shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
    
def disableroues():
    st = 'sudo echo "'+str(roues[0])+'='+str(0)+'">/dev/pi-blaster'
    st+= ' && '+ 'sudo echo "'+str(roues[1])+'='+str(0)+'">/dev/pi-blaster'
    Popen(st,shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)

def movecam(f):
    global campos
    if campos+f<0.95 and campos+f>0.14:
        campos = campos+f
    
    pos = min(0.9,campos)
    if pos != 0:
        pos = pos*0.12
        pos+=0.01
    st = 'sudo echo "'+str(camid)+'='+str(pos)+'">/dev/pi-blaster'

    Popen(st,shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)

def moveroues(a,b):
    b = 1-b
    a+=0.04
    b+=0.04

    a = a*0.12
    a+=0.01

    b = b*0.12
    b+=0.01
    
    st = 'sudo echo "'+str(roues[0])+'='+str(a)+'">/dev/pi-blaster'+" && "+'sudo echo "'+str(roues[1])+'='+str(b)+'">/dev/pi-blaster'
    Popen(st,shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)

def moveg(i,j,pos):
    global movelist, opattes
    opattes[i][j] = (pos,100)
    movelist.append((i,j,pos))

def moveh(i,j,pos,speed):
    global opattes
    opattes[i][j] = (pos,speed)

def applymove():
    global movelist, pattes
    if len(movelist)>0:
        args = []
        k = 0
        for ele in movelist:
            k+=1
            i,j,pos = ele
            pattes[i][j] = pos
            if pos != 0:
                pos = pos*0.12
                pos+=0.01
            args.append('sudo echo "'+str(ipattes[i][j])+'='+str(pos)+'">/dev/pi-blaster')
            if k < len(movelist):
                args.append(" & ")
        Popen("".join(args),shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
    movelist = []
    
def move(i,j,pos):
    global opattes, pattes
    opattes[i][j] = (pos,100)
    pattes[i][j] = pos
    if pos != 0:
        pos = pos*0.12
        pos+=0.01
    st = 'sudo echo "'+str(ipattes[i][j])+'='+str(pos)+'">/dev/pi-blaster'

    Popen(st,shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
    #print('sudo echo "'+str(ipattes[i][j])+'='+str(pos)+'">/dev/pi-blaster')


def moveorigin():
    for i in range(6):
        for j in range(3):
            pass
            moveg(i,j,origin[j])
    disableroues()
    applymove()
    time.sleep(0.4)
    
moveorigin()
movecam(0)




app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')







def shutserver():
    global app
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        print("FLASKERROR")
    func()
    
def setfini():
    global fini,fd,oldtermios
    fini = True
    for i in range(6):
        for j in range(3):
            move(i,j,0)

    disablecam()
    time.sleep(0.5)
    termios.tcsetattr(fd,termios.TCSADRAIN,oldtermios)
    print("OK")
    sys.exit()
    
def getfini():
    global fini
    return fini


def shut():
    setfini()
    shutserver()
    return "Shutdown..."

@app.route('/<changepin>', methods=['POST'])
def reroute(changepin):

    changePin = int(changepin) #cast changepin to an int

    if changePin == 1:
        setdir(3)
    elif changePin == 2:
        setdir(4)
    elif changePin == 3:
        setdir(5)
    elif changePin == 4:
        setdir(6)
    elif changePin == 5:
        setdir(1)
    elif changePin == 6:
        setdir(2)
    elif changePin == 7:
        movecam(-0.15)
    elif changePin == 8:
        movecam(0.15)
    elif changePin == 0:
        setdir(0)
    elif changePin == 10:
        shut()
    elif changePin == 11:
        setdir(10)
    elif changePin == 12:
        setdir(9)
    elif changePin == 13:
        setdir(7)
    elif changePin == 14:
        setdir(8)
    elif changePin == 15:
        setdir(11)
    elif changePin == 16:
        setdir(12)
    elif changePin == 17:
        setdir(13)
    elif changePin == 18:
        setdir(-3)
    elif changePin == 19:
        setdir(-4)
    elif changePin == 20:
        setdir(14)
    elif changePin == 21:
        setdir(15)
    elif changePin == 22:
        setdir(16)    

    response = make_response(redirect(url_for('index')))
    return(response)


sltime = 0.3

decay = 0

def setdecay(x):
    global decay
    decay = float(x)/100



def walk(direc):
    global sltime,origin
    
    if direc>0:
        d = direc

        for k in range(2):
            off1 = decay
            vh = origin[1]+off1
            vho = origin[1]-off1
            
            va2 = origin[2]-0.1
            vb2 = origin[2]+0.1

            va1 = origin[1]+0.3
            vb1 = origin[1]-0.07
            vc1 = origin[1]+0.07
            vd1 = origin[1]+0.3
            dc = d%2
            if k == 1:
                vh,vho = vho,vh
                va2,vb2 = vb2,va2
                va1,vb1 = vb1,va1
                vd1,vc1 = vc1,vd1
                dc = 1-dc

            #######
            for i in range(dc,6,2):
                moveg(i,1,origin[1]+0.15)
                moveg(i,0,origin[0]+0.2)
            applymove()
            
            time.sleep(sltime)
            #######

            #moveg((d+2+(dc+d+1)%2*3)%6,1,vho)
            
            moveg((d+0)%6,2,vb2)
            moveg((d+0)%6,1,va1)

            moveg((d+4)%6,2,va2)
            moveg((d+4)%6,1,va1)

            ##

            moveg((d+1)%6,2,va2)
            moveg((d+1)%6,1,vc1)

            moveg((d+3)%6,2,vb2)
            moveg((d+3)%6,1,vc1)
            
            applymove()
            
            time.sleep(sltime)
            #######
            '''for i in range(1-dc,6,2):
                if i != (d+5)%6 and i != (d+2)%6:
                    moveg(i,1,vh)'''
            
            for i in range(dc,6,2):
                if i != (d+5)%6 and i != (d+2)%6:
                    moveg(i,1,vh)
                    moveg(i,0,origin[0])
            
            moveg((d+2+(dc+d)%2*3)%6,1,vho)
            moveg((d+2+(dc+d)%2*3)%6,0,origin[0])
            applymove()
            time.sleep(sltime)

def walk2(direc):
    global sltime,origin
    
    if direc>0:
        d = direc

        for k in range(2):
            '''off1 = decay
            vh = origin[1]+off1
            vho = origin[1]-off1'''
            
            va2 = origin[2]-0.1
            vb2 = origin[2]+0.1

            '''va1 = origin[1]+0.3
            vb1 = origin[1]-0.07
            vc1 = origin[1]+0.07
            vd1 = origin[1]+0.3'''
            dc = d%2
            if k == 1:
                #vh,vho = vho,vh
                va2,vb2 = vb2,va2
                #va1,vb1 = vb1,va1
                #vd1,vc1 = vc1,vd1
                dc = 1-dc

            #######
            
            moveg(i,1,origin[1]+0.15)
            moveg(i,0,origin[0]+0.2)
            applymove()
            
            time.sleep(sltime)
            #######

            #moveg((d+2+(dc+d+1)%2*3)%6,1,vho)
            
            moveg((d+0)%6,2,vb2)
            moveg((d+0)%6,1,va1)

            moveg((d+4)%6,2,va2)
            moveg((d+4)%6,1,va1)

            ##

            moveg((d+1)%6,2,va2)
            moveg((d+1)%6,1,vc1)

            moveg((d+3)%6,2,vb2)
            moveg((d+3)%6,1,vc1)
            
            applymove()
            
            time.sleep(sltime)
            #######
            '''for i in range(1-dc,6,2):
                if i != (d+5)%6 and i != (d+2)%6:
                    moveg(i,1,vh)'''
            
            for i in range(dc,6,2):
                if i != (d+5)%6 and i != (d+2)%6:
                    moveg(i,1,vh)
                    moveg(i,0,origin[0])
            
            moveg((d+2+(dc+d)%2*3)%6,1,vho)
            moveg((d+2+(dc+d)%2*3)%6,0,origin[0])
            applymove()
            time.sleep(sltime)

def take():
    global sltime,origin
    moveg(2,1,origin[1]+0.3)
    moveg(2,0,origin[0]+0.2)
    moveg(3,1,origin[1]+0.3)
    moveg(3,0,origin[0]+0.2)
    applymove()
    time.sleep(sltime*2)

    moveg(2,2,origin[0]-0.18)
    moveg(3,2,origin[0]+0.18)
    
    applymove()
    time.sleep(sltime*2)

    moveg(2,1,origin[1]+0.4)
    moveg(3,1,origin[1]+0.4)
    applymove()
    time.sleep(sltime*2)

def release():
    global sltime,origin
    

    moveg(2,1,origin[1]+0.3)
    moveg(3,1,origin[1]+0.3)
    applymove()
    time.sleep(sltime*2)

    moveg(2,2,origin[0]+0.15)
    moveg(3,2,origin[0]-0.15)
    
    applymove()
    time.sleep(sltime*2)

    moveg(2,1,origin[1]+0.55)
    moveg(2,0,origin[0]+0.55)
    moveg(3,1,origin[1]+0.55)
    moveg(3,0,origin[0]+0.55)
    applymove()
    time.sleep(sltime*2)

def turnleft():
    global sltime,origin
    
    for i in range(3):
        moveg(i*2,1,origin[1]+0.3)
        moveg(i*2,2,origin[2]+0.2)
    applymove()
    time.sleep(sltime*1)

    for i in range(3):
        moveg(i*2,1,origin[1])
    applymove()
    time.sleep(sltime*1)

    for i in range(3):
        moveg(i*2,2,origin[2])
        moveg(i*2+1,1,origin[1]+0.3)
    applymove()
    time.sleep(sltime*1)

    for i in range(3):
        moveg(i*2+1,1,origin[1])
    applymove()
    time.sleep(sltime)


def turnright():
    global sltime,origin
    
    for i in range(3):
        moveg(i*2,1,origin[1]+0.3)
        moveg(i*2,2,origin[2]-0.2)
    applymove()
    time.sleep(sltime*1)

    for i in range(3):
        moveg(i*2,1,origin[1])
    applymove()
    time.sleep(sltime*1)

    for i in range(3):
        moveg(i*2,2,origin[2])
        moveg(i*2+1,1,origin[1]+0.3)
    applymove()
    time.sleep(sltime*1)

    for i in range(3):
        moveg(i*2+1,1,origin[1])
    applymove()
    time.sleep(sltime)

def front(i):
    global sltime,origin

    i0 = (0+i)%6
    i1 = (1+i)%6
    i2 = (2+i)%6
    i3 = (3+i)%6
    i4 = (4+i)%6
    i5 = (5+i)%6

    moveg(i0,1,origin[1]+0.3)
    moveg(i1,1,origin[1])
    moveg(i2,1,origin[1]+0.3)
    moveg(i3,1,origin[1])
    moveg(i4,1,origin[1]+0.3)
    moveg(i5,1,origin[1])

    applymove()
    time.sleep(sltime*0.2)
    
    moveg(i0,2,origin[2]-0.101)
    moveg(i2,2,origin[2]-0.1)
    moveg(i4,2,origin[2]+0.12)
    
    moveg(i1,2,origin[2]+0.12)
    moveg(i3,2,origin[2]-0.101)
    moveg(i5,2,origin[2]-0.1)
    applymove()
    time.sleep(sltime)

    moveg(i0,1,origin[1])
    moveg(i2,1,origin[1])
    moveg(i4,1,origin[1])
    applymove()
    time.sleep(sltime)

    moveg(i1,1,origin[1]+0.3)
    moveg(i3,1,origin[1]+0.3)
    moveg(i5,1,origin[1]+0.3)

    applymove()
    time.sleep(sltime*0.2)

    moveg(i1,2,origin[2]-0.12)
    moveg(i3,2,origin[2]+0.1)
    moveg(i5,2,origin[2]+0.101)

    moveg(i0,2,origin[2]+0.1)
    moveg(i2,2,origin[2]+0.101)
    moveg(i4,2,origin[2]-0.12)
    
    applymove()
    time.sleep(sltime)

    moveg(i1,1,origin[1])
    moveg(i3,1,origin[1])
    moveg(i5,1,origin[1])
    applymove()
    time.sleep(sltime)

    pass

def back():
    pass

def getdir():
    global direction
    return direction

def setdir(x):
    global direction
    direction = int(x)

def turtlemode():
    global sltime,origin
    for j in range(6):
        moveg(j,1,origin[1]+0.55)
        if j<3:
            moveg(j,2,origin[2]+0.15)
        else:
            moveg(j,2,origin[2]-0.15)
        moveg(j,0,origin[0]+0.55)
    applymove()
    time.sleep(sltime*0.5)

def dabmode():
    moveg(3,2,origin[2]+0.4)
    moveg(2,1,origin[1]+0.45)
    moveg(3,1,origin[1]+0.45)
    moveg(2,0,origin[0]+0.15)
    moveg(3,0,origin[0]+0.15)
    applymove()
    time.sleep(sltime*0.5)

def randomode():
    global sltime,origin
    for j in range(6):
        moveg(j,1,origin[1]+0.6-0.25*random())
        moveg(j,2,origin[2]+0.3-0.3*random())
        moveg(j,0,origin[0]+0.1+0.5-0.7*random())
    applymove()
    time.sleep(sltime*0.5)

class MoveThread(threading.Thread):
    global fini
    def run(self):
        oldd = getdir()
        while True:
            gd = getdir()
            if (not (oldd>=7 and oldd<14)) and (gd==9 or gd==10):
                setdir(8-gd)
            gd = getdir()
            if gd>=7 and gd<18:
                if not (oldd>=7 and oldd<18):
                   moveorigin()

                   for i in range(10):
                       for j in range(6):
                           moveg(j,1,origin[1]+i*0.05)
                        
                       applymove()
                       time.sleep(0.1)
                   for j in range(6):
                       moveg(j,1,origin[1]+0.55)
                       if j<3:
                           moveg(j,2,origin[2]+0.15)
                       else:
                           moveg(j,2,origin[2]-0.15)
                       moveg(j,0,origin[0]+0.55)
                   applymove()
                if oldd != gd or gd == 15:
                    if gd == 11:
                        disableroues()
                    elif gd == 12:
                        take()
                    elif gd == 13:
                        release()
                    elif gd == 14:
                        turtlemode()
                    elif gd == 15:
                        randomode()
                    elif gd == 16:
                        dabmode()
                    else:
                        dawaz = (1,1)
                        if gd == 8:
                            dawaz = (-1,-1)
                        elif gd == 9:
                            dawaz = (-0.2,0.2)
                        elif gd == 10:
                            dawaz = (0.15,-0.15)
                           
                        moveroues(dawaz[0]*0.1+0.5,dawaz[1]*0.1+0.5)

            else:
                
                if oldd != gd:
                    if (oldd>=7 and oldd<14):
                       disableroues()
                    moveorigin()
                
                if gd==-2:
                    turnleft()
                elif gd==-1:
                    turnright()
                elif gd==-3:
                    front(0)
                elif gd==-4:
                    front(3)
                elif gd==4:
                    front(1)
                elif gd==6:
                    front(2)
                elif gd==1:
                    front(4)
                elif gd==3:
                    front(5)
                elif gd>0 and gd<7:
                    walk(gd)

            oldd = gd
            time.sleep(0.02)
    pass
thread = MoveThread()
thread.daemon = True
thread.start()

def getpattes():
    global opattes, pattes
    return (opattes,pattes)

'''
class TransitionThread(threading.Thread):
    def run(self):
        aopattes, apattes = getpattes()
        t = time.time()
        while True:
            delta = time.time()-t
            t = time.time()
            for i in range(6):
                for j in range(3):
                    diff = aopattes[i][j][0] - apattes[i][j]
                    if abs(diff)>0.001:
                        
                        if diff<0:
                            newpos = apattes[i][j]-delta*aopattes[i][j][1]
                        elif diff>0:
                            newpos = apattes[i][j]+delta*aopattes[i][j][1]
                        diff2 = aopattes[i][j][0] - newpos
                        if aopattes[i][j][1]>50 or diff*diff2<0:
                            movet(i,j,aopattes[i][j][0])
                        else:
                            movet(i,j,newpos)
                        
            applymove()
            time.sleep(0.005)
    pass
'''


class ServerThread(threading.Thread):
    def run(self):
        

        
        '''server_adress = '/tmp/socky'
        try:
            os.unlink(server_adress)
        except OSError:
            if os.path.exists(server_adress):
                raise
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(server_adress)
        sock.listen(1)
        time.sleep(0.2)

        while True:
            print(22)
            connexion, client_adress = sock.accept()
            print(23)
            try:
                while True:
                    data = connexion.recv(16)
                    print(data)
                    if not data:
                        break
            finally:
                connexion.close()
            time.sleep(0.005)
        '''
    pass

thread = ServerThread()
thread.daemon = True
thread.start()


def getch():
    global oldtermios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    oldtermios = old
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd,termios.TCSADRAIN,old)
    return ch





    
class InputThread(threading.Thread):
    def run(self):
        while not getfini():
            car = getch()
            letr = ["n","a","z","e","d","s","q","r","f"]
            #print(333)
            for i in range(9):
                if car == letr[i]:
                    setdir(i)
            if car == "p":
                setfini()
                
            time.sleep(0.005)
    pass

thread = InputThread()
thread.daemon = True
thread.start()
"""
thread2 = TransitionThread()
thread2.daemon = True
thread2.start()
"""

def shutdown(rien=0):
    Popen("sudo shutdown -h now",shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
"""
class App:

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        scales = []
        fs = []

        for i in range(6):
            fs.append(lambda x,z=i:self.update(z,x))

        for i in range(6): 
            scale = Scale(frame, from_=-0, to=100,
                  orient=HORIZONTAL, command=fs[i])
            scale.set(30+(i%3)*10)
            scale.grid(row=i)
            scales.append(scale)
        b = Scale(frame,from_=0, to=6, orient=VERTICAL, command = setdir)
        b.grid(row=6)

        b = Scale(frame,from_=0, to=10, orient=VERTICAL, command = setdecay)
        b.grid(row=6, column = 1)
        '''
        letr = ['<Return>','a','z','e','d','s','q']
        for i in range(7):
            master.bind(letr[i], lambda x,z=i:setdir(z))
            #master.bind("<Return>", lambda z=i:print(z))
        '''



    def update(self, idi, angle):
        '''duty = float(angle) / 10.0 + 2.5
        rana = 0
        if idi>2:
            idi-=3
            rana = 1
        for i in range(rana,6,2):
            move(i,idi,float(angle)/100)'''
            

root = Tk()
root.wm_title('Servo Control')
app = App(root)
root.geometry("800x600+0+0")
root.mainloop()
"""



if len(sys.argv)<2:
    app.run(debug=False, host='192.168.43.181', port=8000) #set up the server in debug mode to the port 8000

else:
    while True:
        time.sleep(0.1)
'''

while not fini:
    time.sleep(0.1)

for i in range(6):
    for j in range(3):
        move(i,j,0)
time.sleep(1)
'''
"""for i in range(6):
    for j in range(3):
        pattes[i][j].stop()


#GPIO.cleanup()
"""
