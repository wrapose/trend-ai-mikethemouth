
class OneRound(object):
    def __init__(self, selfMd5):
        self.selfMd5 =  selfMd5

        self.roundCount = 0

        self.smallBlind = ""
        self.smallAmount = ""
        self.bigBlind = ""
        self.bigAmount = ""

        self.players = []
        self.playerIndex = {}

        self.holeCards = []
        self.boardCards = []

        self.roundName = ""

        self.actions = {}

        self.pot = 0
        self.selfBet = 0
        self.minBet = 0

        self.winMoney = 0

    def newRound(self, data):
        self.roundCount = data["table"]["roundCount"]

        self.smallBlind = data["table"]["smallBlind"]["playerName"]
        self.smallAmount = int(data["table"]["smallBlind"]["amount"])
        self.bigBlind = data["table"]["bigBlind"]["playerName"]
        self.bigAmount = int(data["table"]["bigBlind"]["amount"])

        self.roundName = data["table"]["roundName"]

        self.pot = data["table"]["totalBet"]

        tmp = []
        for player in data["players"]:
            if not player["isSurvive"]:
                continue

            if self.smallBlind == player["playerName"] or len(self.players) > 0:
                self.players.append(player)
            else:
                tmp.append(player)
        self.players += tmp

        #import pdb
        #pdb.set_trace()

        for idx in xrange(len(self.players)):
            self.playerIndex[self.players[idx]["playerName"]] = idx

        self.holeCards = [self.convertCardFormat(c) for c in self.players[self.playerIndex[self.selfMd5]]["cards"]]

    def newDeal(self, data):
        self.roundName = data["table"]["roundName"]

        self.pot = data["table"]["totalBet"]

        for player in data["players"]:
            if player["playerName"] in self.playerIndex:
                self.players[self.playerIndex[player["playerName"]]] = player

        self.boardCards = [self.convertCardFormat(c) for c in data["table"]["board"]]

    def newAction(self, data):
        self.latestAction = data["action"]

        self.pot = data["table"]["totalBet"]

        for player in data["players"]:
            if player["playerName"] in self.playerIndex:
                self.players[self.playerIndex[player["playerName"]]] = player

        if self.selfMd5 == data["action"]["playerName"]:
            if "amount" in data["action"]:
                self.selfBet += int(data["action"]["amount"])

        if self.roundName not in self.actions:
            self.actions[self.roundName] = []
        self.actions[self.roundName].append(data["action"])

    def requestAction(self, data):
        self.minBet = data["self"]["minBet"]

    def endRound(self, data):
        for player in data["players"]:
            if player["playerName"] in self.playerIndex:
                self.players[self.playerIndex[player["playerName"]]] = player

        if self.players[self.playerIndex[self.selfMd5]]["winMoney"] > 0:
            self.winMoney = self.players[self.playerIndex[self.selfMd5]]["winMoney"]
        else:
            self.winMoney = -self.selfBet

    def getSelfChips(self):
        return int(self.players[self.playerIndex[self.selfMd5]]["chips"])

    def getChipsOf(self, playerMd5):
        return int(self.players[self.playerIndex[playerMd5]]["chips"])

    def getPlayerCount(self):
        count = 0
        for player in self.players:
            if player["isSurvive"] and not player["folded"]:
                count += 1
        return count

    def getLatestAction(self):
        return self.latestAction["action"]

    def getLatestActionPlayer(self):
        return self.latestAction["playerName"]

    def outputActionHistory(self, fileName):
        #import pdb
        #pdb.set_trace()
        with open(fileName, "a") as ofile:
            for r in self.actions:
                for a in self.actions[r]:
                    msg = str(self.roundCount) + "," + r + ","
                    msg = msg + a["playerName"] + ","
                    msg = msg + a["action"] + ","
                    if "amount" in a:
                        msg = msg + str(a["amount"]) + ","
                    else:
                        msg = msg + "0,"
                    msg = msg + str(a["chips"]) + ","
                    msg = msg + ".".join(self.players[self.playerIndex[a["playerName"]]]["cards"]) + ","
                    msg = msg + ".".join(self.boardCards) + ","
                    msg = msg + self.players[self.playerIndex[a["playerName"]]]["hand"]["message"] + "\n"
                    ofile.write(msg)
            ofile.close()

    def convertCardFormat(self, card):
        """
        Convert card format so that we could use
        library to evaluate cards
        """
        if len(card) != 2:
            print "Wrong card format"
            return
        return card[0] + card[1].lower()

class IDecisionEngine(object):
    def __init__(self):
        pass

    def newRound(self, oneRound):
        pass

    def endRound(self, oneRound):
        pass

    def newDeal(self, oneRound):   # notify when new card in board
        pass

    def newAction(self, oneRound): # notify one player's action (include self)
        pass

    def evaluateDeal(self, oneRound):
        pass

    def evaluateFlop(self, oneRound):
        pass

    def evaluateTurn(self, oneRound):
        pass

    def evaluateRiver(self, oneRound):
        pass

    def neeReload(self, oneRound):
        return False