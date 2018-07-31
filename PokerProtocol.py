
#! /usr/bin/env python
# -*- coding:utf-8 -*-

import time
import json
import hashlib
from IDecisionEngine import OneRound

class PokerProtocol:
    def __init__(self, ws, decisionEngine):
        self.ws = ws
        self.myMd5 = ""
        self.decisionEngine = decisionEngine
        self.currentRound = None

    def react(self, result):
        """
        React to events
        """

        msg = json.loads(result)
        event = msg["eventName"]
        data = msg["data"]
        #print event
        #print data

        if event == "__new_peer":
            pass
        elif event == "__new_peer_2":
            pass
        elif event == "_join":
            pass
        elif event == "__show_action":
            if self.currentRound is not None:
                self.currentRound.newAction(data)
                self.decisionEngine.newAction(self.currentRound)
        elif event == "__deal":
            if self.currentRound is not None:
                self.currentRound.newDeal(data)
                self.decisionEngine.newDeal(self.currentRound)
        elif event == "__start_reload":
            if self.currentRound is not None:
                if self.decisionEngine.needReload(self.currentRound):
                    self.ws.send(json.dumps({"eventName": "__reload"}))
        elif event == "__round_end":
            if self.currentRound is not None:
                self.currentRound.endRound(data)
                self.currentRound.outputActionHistory("ActionHistory" + time.strftime("%Y%m%d", time.gmtime()) + ".csv")
                print "==== Round end : Win money ==== %d" % self.currentRound.winMoney
        elif event == "__new_round":
            self.currentRound = OneRound(self.myMd5)
            self.currentRound.newRound(data)
            self.decisionEngine.newRound(self.currentRound)
        elif event == "__bet":
            # time.sleep(2)
            if self.currentRound is not None:
                self.currentRound.requestAction(data)
                self.evaluate(self.currentRound)
        elif event == "__action":
            # time.sleep(2)
            if self.currentRound is not None:
                self.currentRound.requestAction(data)
                self.evaluate(self.currentRound)
        elif event == "__game_over":
            max_chips = 0
            my_chips = 0
            '''for winner in data["winners"]:
                if winner["chips"] > max_chips:
                    max_chips = winner["chips"]
                if winner["playerName"] == self.myMd5:
                    my_chips = winner["chips"]
            if my_chips == max_chips:
                print "==== Game over : YOU ARE THE WINNER!! ==== Final chips %d" % max_chips
            else:
                print "==== Game over : So close... ==== %d vs %d" % (my_chips, max_chips)'''
        else:
            print "==== unknown event ==== : " + event
            #print data

    def evaluate(self, oneRound):
        """
        Make decision of each stage
        """

        hole_cards = oneRound.holeCards
        board_cards = oneRound.boardCards

        print "==== my cards ==== " + str(hole_cards)
        print "==== board ==== " + str(board_cards)
        print "==== Current pot ==== %d" % (oneRound.pot)
        print "==== Minbet ==== %d" % (oneRound.minBet)

        if oneRound.roundName == "Deal":
            res = self.decisionEngine.evaluateDeal(oneRound)
        elif oneRound.roundName == "Flop":
            res = self.decisionEngine.evaluateFlop(oneRound)
        elif oneRound.roundName == "Turn":
            res = self.decisionEngine.evaluateTurn(oneRound)
        elif oneRound.roundName == "River":
            res = self.decisionEngine.evaluateRiver(oneRound)
        else:
            print('unknown round name')
            res = ('fold', 0)

        action = res[0]
        if (len(res) > 1):
            amount = res[1]
        else:
            amount = 0;

        if "fold" == action and 0 == oneRound.minBet:
            action = "check"

        self.take_action(action, amount)

    def join_game(self, myId):
        self.myMd5 = hashlib.md5(myId).hexdigest()
        self.ws.send(json.dumps({
            "eventName": "__join",
            "data": {
                "playerName": myId
            }
        }))

    def take_action(self, action="check", amount=0):
        """
        Take an action
        """
        #global my_round_action

        '''if ("bet" in my_round_action or "raise" in my_round_action) \
            and action in ["bet", "raise"]:
                action = "call" '''

        message = {
            "eventName": "__action",
            "data": {}
        }
        message["data"]["action"] = action
        message["data"]["amount"] = int(amount)

        print "==== Take Action ==== : %s %s" % (action, str(amount))
        self.ws.send(json.dumps(message))