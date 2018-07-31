#! /usr/bin/env python
# -*- coding:utf-8 -*-

import time

import sys

from websocket import create_connection
# pip install websocket-client

from PokerProtocol import PokerProtocol
from DecisionEngine_RuleBased import DecisionEngine_RuleBased


def doListen(srvAddr, myId):
    ws = create_connection(srvAddr)

    decEng = DecisionEngine_RuleBased(myId)

    poker = PokerProtocol(ws, decEng)

    poker.join_game(myId)

    while not stop:
        result = ws.recv()
        poker.react(result)

def playGame(srvAddr, myId):
    global stop
    stop = False
    while not stop:
        '''try:
            doListen(srvAddr, myId)
        except Exception, e:
            print e.message
            time.sleep(3)'''
        doListen(srvAddr, myId)

if __name__ == '__main__':
    if 3 == len(sys.argv):
        srvAddr = sys.argv[1]
        myId = sys.argv[2]
    else:
        srvAddr = "ws://atxholdem2.tplab.tippingpoint.com:3001"
        myId = "415a1c20eb"
    playGame(srvAddr, myId)
