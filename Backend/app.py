from __future__ import print_function

from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import json

import cluster

import sys 

import touchPad

import time

import touching_phones

###########



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

global sensor
sensor = touchPad.SensorInterface()
try:
    sensor.connect()
except:
    print("Error connecting to sensor")
    raise

print ("Sensor Connected!")

global contactHistory
contactHistory = False

global speedConstant
speedConstant = 1000

global RADIUS
RADIUS = 4

global is_init
is_init = True

global ballPos
ballPos = [RADIUS, RADIUS]
global ballVel
ballVel = [0, 0]
global globalPos
globalPos = None

global prevTime
prevTime = None

# Server side

@socketio.on('connect')
def on_connect():
    #emit('position', test)
    for i in xrange(100000):
        data = getData()
        if data:
            print(data)
            emit('position', data)
            time.sleep(0.2)
            break
        else:
            print("TRY AGAIN 1")
            time.sleep(0.2) 


@socketio.on('more')
def more(more):
    
    for i in xrange(100000):
        data = getData()
        if data:
            print(data)
            emit('position', data)
            time.sleep(0.1)
            break
        else:
            print("TRY AGAIN 1")
            time.sleep(0.1)
    
    
def getData():
    global prevTime
    global is_init
    images = sensor.getAllImages()
    if len(images) > 0:
        centers = cluster.findClusterCenters(images[-1]["image"])
        if centers is not None and centers.shape[0] == 8:
            result = touching_phones.assignPoints(centers)
            if result:
                (touchpoints1, touchpoints2), (tL1, tR1, bL1, bR1), (tL2, tR2, bL2, bR2) = result
                
                #Empty?
                touch = False
                if touchpoints1:
                    touch = True
                
                if prevTime is None:
                    prevTime = time.time() 
                else:
                    prevTime = time.time() - prevTime                
                
                if is_init:
                    data = makeInitData(tL1, tR1, bL1, bR1, tL2, tR2, bL2, bR2)
                    is_init = False
                else:
                    data = makeData(tL1, tR1, bL1, bR1, tL2, tR2, bL2, bR2)
                
                return data 
    return None


def makeInitData(tL1, tR1, bL1, bR1, tL2, tR2, bL2, bR2):
    global ballPos
    global ballVel
    global globalPos
    global phone
    ballPos = [RADIUS, 0.5 * (bL1[1] + tL1[1])]
    ballVel = [1, 1]
    globalPos = [tL1[0] + RADIUS, 0.5 * (bL1[1] + tL1[1])]
    phone = 0
    
    json = {"data":[{"clients": [{"client0":
                                  [{"tl": tL1 },
                                  {"tr": tR1 },
                                  {"bl": bL1 },
                                  {"br": bR1 }]
                                  },
                                 {"client1":
                                  [{"tl": tL2 },
                                  {"tr": tR2 },
                                  {"bl": bL2 },
                                  {"br": bR2 }]
                                 }]
                     },
                    {"balls":
                        [
                            {'phone': phone},
                            {"globalPosition": globalPos},
                            {"position": ballPos},
                            {"velocity": ballVel}
                        ]
                    }
                ]
            }
    return json

def makeData(tL1, tR1, bL1, bR1, tL2, tR2, bL2, bR2):
    global globalPos
    global prevTime
    global ballPos
    
    global phone
    global contactHistory
    
    
    globalPos[0] = globalPos[0] + ballVel[0] * prevTime * speedConstant
    globalPos[1] = globalPos[1] + ballVel[1] * prevTime * speedConstant
    
    
    ballPos[0] = globalPos[0] - tL1[0]
    ballPos[1] = globalPos[1] - tL1[1]
    
    num = 7.2
    
    print(abs(tL1[0] - tR2[0]) <= num or abs(tR1[0] - tL2[0]) <= num)
    
    if (abs(tL1[0] - tR2[0]) <= num or abs(tR1[0] - tL2[0]) <= num):
        if not contactHistory:
            phone = 1 - phone
            contactHistory = True
    else:
        if contactHistory:
            contactHistory = False
            
                
    
    
    json = {"data":[{"clients": [{"client0":
                                  [{"tl": tL1 },
                                  {"tr": tR1 },
                                  {"bl": bL1 },
                                  {"br": bR1 }]
                                  },
                                 {"client1":
                                  [{"tl": tL2 },
                                  {"tr": tR2 },
                                  {"bl": bL2 },
                                  {"br": bR2 }]
                                 }]
                     },
                    {"balls":
                        [
                            {'phone': phone},
                            {"globalPosition": globalPos},
                            {"position": [10,10]},
                            {"velocity": ballVel}
                        ]
                    }
                ]
            }
    wallCollision(tL1, tR1, bL1, bR1, tL2, tR2, bL2, bR2)
    return json

def wallCollision(tL1, tR1, bL1, bR1, tL2, tR2, bL2, bR2):
    global phone
    global ballVel
    if phone == 0:
        if ballPos[0] + RADIUS >= bR1[0] and ballVel[0] > 0:
            ballVel[0] = -1 * ballVel[0]
        elif ballPos[0] - RADIUS <= bL1[0] and ballVel[0] < 0:
            ballVel[0] = -1 * ballVel[0]
        
        if ballPos[1] + RADIUS >= bR1[1] and ballVel[1] > 0:
            ballVel[1] = -1 * ballVel[1]
        elif ballPos[1] - RADIUS <= tR1[1] and ballVel[1] < 0:
            ballVel[1] = -1 * ballVel[1]
    
    else:
        if ballPos[0] + RADIUS >= bR2[0] and ballVel[0] > 0:
            ballVel[0] = -1 * ballVel[0]
        elif ballPos[0] - RADIUS <= bL2[0] and ballVel[0] < 0:
            ballVel[0] = -1 * ballVel[0]
        
        if ballPos[1] + RADIUS >= bR2[1] and ballVel[1] > 0:
            ballVel[1] = -1 * ballVel[1]
        elif ballPos[1] - RADIUS <= tR2[1] and ballVel[1] < 0:
            ballVel[1] = -1 * ballVel[1]        

if __name__ == '__main__':
    
    for i in range(300):
        sensor.setBaseline()
    
    for num in xrange(0,10):
        print(str(9-num))
        time.sleep(0.15)
    
    
    socketio.run(app, host="0.0.0.0", port=80)