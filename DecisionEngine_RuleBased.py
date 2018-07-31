
import sys
import hashlib

sys.path.insert(0, "holdem_calc")
import holdem_calc
import deuces

from IDecisionEngine import IDecisionEngine

class DecisionEngine_RuleBased(IDecisionEngine):
    def __init__(self, myId):
        self.myId = myId
        self.myMd5 = hashlib.md5(myId).hexdigest()

        self.pot = 0
        self.my_round_action = dict()
        self.allin_count = dict()
        self.raise_count = dict()
        self.bet_count = dict()
        self.player_count = {
            "Deal": 0,
            "Flop": 0,
            "Turn": 0,
            "River": 0
        }

    def needReload(self, oneRound):
        return oneRound.getSelfChips() < 600

    def newDeal(self, oneRound):
        """
        Update active player count of current stage
        """
        self.player_count[oneRound.roundName] = oneRound.getPlayerCount()

        self.pot = oneRound.pot

    def newRound(self, oneRound):
        self.pot = 0
        self.allin_count = dict()
        self.raise_count = dict()
        self.bet_count = dict()
        self.player_count = {
            "Deal": 0,
            "Flop": 0,
            "Turn": 0,
            "River": 0
        }

        self.pot = oneRound.pot

    def newAction(self, oneRound):
        #print data

        self.pot = oneRound.pot

        if oneRound.getLatestAction() == "allin":
            if oneRound.getLatestActionPlayer() in self.allin_count:
                self.allin_count[oneRound.getLatestActionPlayer()] += 1
            else:
                self.allin_count[oneRound.getLatestActionPlayer()] = 1
        if oneRound.getLatestAction() == "raise":
            if oneRound.getLatestActionPlayer() in self.raise_count:
                self.raise_count[oneRound.getLatestActionPlayer()] += 1
            else:
                self.raise_count[oneRound.getLatestActionPlayer()] = 1
        if oneRound.getLatestAction() == "bet":
            if oneRound.getLatestActionPlayer() in self.bet_count:
                self.bet_count[oneRound.getLatestActionPlayer()] += 1
            else:
                self.bet_count[oneRound.getLatestActionPlayer()] = 1

    def evaluateRiver(self, oneRound):
        """
        Decide action in river stage
        """
        win_all_prob = self.calc_win_prob(oneRound.holeCards, oneRound.boardCards, oneRound)
        ev = self.expected_value(win_all_prob, oneRound.minBet)

        minBet = oneRound.minBet
        chips = oneRound.getSelfChips()
        bb = oneRound.bigAmount

        if win_all_prob >= 0.9:
            return ("allin", 0)
        elif win_all_prob >= 0.6:
            amount = min(ev, 0.1 * chips + minBet)
            return ("bet", amount)
        elif win_all_prob >= 0.4:
            return ("call", 0)
        elif ev >= 0 and win_all_prob >= 0.2:
            return ("check", 0)
        elif minBet == 0:
            if bb <= 80 and win_all_prob >= 0.05:
                return ("bet", bb)
            else:
                return ("check", 0)
        elif minBet <= 160 and win_all_prob > 0.005:
            return ("call", 0)
        else:
            return ("fold", 0)

    def evaluateTurn(self, oneRound):
        """
        Decide action in turn stage
        """
        win_all_prob = self.calc_win_prob(oneRound.holeCards, oneRound.boardCards, oneRound)
        ev = self.expected_value(win_all_prob, oneRound.minBet)

        minBet = oneRound.minBet
        chips = oneRound.getSelfChips()
        bb = oneRound.bigAmount

        if win_all_prob >= 0.8:
            amount = 0.2 * chips + minBet
            return ("bet", amount)
        elif win_all_prob >= 0.5:
            amount = min(ev, 0.1 * chips + minBet)
            return ("bet", amount)
        elif win_all_prob >= 0.4:
            amount = min(ev, 0.05 * chips + minBet)
            return ("bet", amount)
        elif ev >= 0 and win_all_prob >= 0.15:
            return ("check", 0)
        elif minBet == 0:
            return ("check", 0)
        elif win_all_prob > 0 and minBet <= 2*bb:
            return ("call", 0)
        else:
            return ("fold", 0)

    def evaluateFlop(self, oneRound):
        """
        Decide action in flop stage
        """
        win_all_prob = self.calc_win_prob_by_sampling(oneRound.holeCards, oneRound.boardCards, oneRound)
        ev = self.expected_value(win_all_prob, oneRound.minBet)

        minBet = oneRound.minBet
        chips = oneRound.getSelfChips()
        bb = oneRound.bigAmount

        if win_all_prob >= 0.8:
            amount = min(ev, 0.1 * chips + minBet)
            return ("bet", amount)
        elif win_all_prob >= 0.5:
            return ("raise", 0)
        elif win_all_prob >= 0.3:
            amount = min(ev, 0.05 * chips + minBet)
            return ("bet", amount)
        elif ev >= 0 and win_all_prob >= 0.15:
            return ("check", 0)
        elif minBet == 0:
            return ("check", 0)
        elif win_all_prob > 0 and minBet <= 3*bb:
            return ("call", 0)
        else:
            return ("fold", 0)

    def evaluateDeal(self, oneRound):
        """
        Decide action in deal stage
        """
        '''v_players = self.virtual_player_count(data)
        score = self.hole_cards_score(hole_cards) * (9 / float(v_players))

        basic_win_porb = 1 / float(v_players)
        ev = self.expected_value(basic_win_porb, data["self"]["minBet"])

        if score > min(self.hole_cards_score(["As", "Js"]), self.hole_cards_score(["Qs", "Qh"])):
            print "==== Judgement is bet ==== score : " + str(score)
            amount = 2 * (data["self"]["minBet"] + 10)
            return ("bet", amount)
        elif score > min(self.hole_cards_score(["As", "9s"]), self.hole_cards_score(["7s", "7h"])):
            print "==== Judgement is bet ==== score : " + str(score)
            amount = 1.5 * (data["self"]["minBet"] + 10)
            return ("bet", amount)
        elif ev >= 0 or data["self"]["minBet"] <= 20:
            print "==== Judgement is call ==== score : %d ,EV : %d" % (score, ev)
            return ("call", 0)
        else:
            print "==== Judgement is fold ==== score : " + str(score)
            return ("fold", 0)'''

        minBet = oneRound.minBet
        chips = oneRound.getSelfChips()
        bb = oneRound.bigAmount

        hole_cards = oneRound.holeCards

        if self.card_to_score[hole_cards[0][0]] >= 12 and \
           self.card_to_score[hole_cards[1][0]] >= 12 and \
           self.card_to_score[hole_cards[0][0]] == self.card_to_score[hole_cards[1][0]]:
            return ("allin", 0)
        elif self.card_to_score[hole_cards[0][0]] >= 9 and \
           self.card_to_score[hole_cards[1][0]] >= 9 and \
           self.card_to_score[hole_cards[0][0]] == self.card_to_score[hole_cards[1][0]]:
            if minBet > 20*bb:
                return ("fold", 0)
            else:
                return ("call", 0)
        elif self.card_to_score[hole_cards[0][0]] >= 6 and \
           self.card_to_score[hole_cards[1][0]] >= 6 and \
           self.card_to_score[hole_cards[0][0]] == self.card_to_score[hole_cards[1][0]]:
            if minBet > 10*bb:
                return ("fold", 0)
            else:
                return ("call", 0)
        elif self.card_to_score[hole_cards[0][0]] == self.card_to_score[hole_cards[1][0]]:
            if minBet > 5*bb or minBet > 300:
                return ("fold", 0)
            else:
                return ("call", 0)
        elif self.card_to_score[hole_cards[0][0]] >= 10 and \
             self.card_to_score[hole_cards[1][0]] >= 10 and \
             hole_cards[0][1] == hole_cards[1][1]:
            if minBet > 20*bb:
                return ("fold", 0)
            else:
                return ("call", 0)
        elif self.card_to_score[hole_cards[0][0]] >= 10 and \
             self.card_to_score[hole_cards[1][0]] >= 10:
            if minBet > 10*bb:
                return ("fold", 0)
            else:
                return ("call", 0)
        elif self.card_to_score[hole_cards[0][0]] == 14 or \
             self.card_to_score[hole_cards[1][0]] == 14:
            if minBet > 5*bb:
                return ("fold", 0)
            else:
                return ("call", 0)
        elif (self.card_to_score[hole_cards[0][0]] == 13 or \
             self.card_to_score[hole_cards[1][0]] == 13) and \
             self.card_to_score[hole_cards[0][0]] >= 9 and \
             self.card_to_score[hole_cards[1][0]] >= 9:
            if minBet > 2*bb:
                return ("fold", 0)
            else:
                return ("call", 0)
        elif 0 == minBet:
            return ("check", 0)
        elif 0 == chips:
            return ("allin", 0)
        elif minBet <= 40:
            return ("call", 0)
        elif minBet <= 160:
            if abs(self.card_to_score[hole_cards[0][0]] - self.card_to_score[hole_cards[1][0]]) < 5 or \
               hole_cards[0][1] == hole_cards[1][1]:
                return ("call", 0)
            else:
                return ("fold", 0)
        else:
            return ("fold", 0)

    card_to_score = {
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "T": 10,
        "J": 11,
        "Q": 12,
        "K": 13,
        "A": 14
    }

    def expected_value(self, win_prob, min_bet):
        """
        Compute expacted value to attend next stage
        """
        EV = (((self.pot + min_bet) * win_prob) - min_bet)
        print "==== Expected value ==== %d" % EV
        return (((self.pot + min_bet) * win_prob) - min_bet)

    def hole_cards_score(self, hole_cards):
        """
        Calculate a score for hole cards
        Return hish score if we got high cards/pair/possible straight/possible flush
        """
        high_card = 0
        same_suit = 0
        possible_straight = 0
        pair = 0

        base_score = self.card_to_score[hole_cards[0][0]] + self.card_to_score[hole_cards[1][0]]
        if base_score > 20:
            high_card = base_score - 20

        if hole_cards[0][1] == hole_cards[1][1]:
            same_suit = 2

        value_diff = self.card_to_score[hole_cards[0][0]] - self.card_to_score[hole_cards[1][0]]
        if value_diff in [-4, 4]:
            possible_straight = 1
        if value_diff in [-3, 3]:
            possible_straight = 2
        if value_diff in [-2, -1, 1, 2]:
            possible_straight = 3
        if value_diff == 0:
            pair = 10

        return (pair + same_suit + high_card + possible_straight) * base_score

    def player_statistics(self, players):
        """
        Return the statistics of current players in this round
        """
        playing = 0
        p_stat = {}
        p_stat["v_bet"] = sum(self.bet_count.values())
        p_stat["v_raise"] = sum(self.raise_count.values())
        p_stat["v_allin"] = sum(self.allin_count.values())
        for player in players:
            if not player["playerName"] == self.myMd5 \
                    and not player["folded"]:
                playing += 1
                if player["allIn"]:
                    p_stat["v_allin"] += 2
                if player["playerName"] in self.bet_count:
                    p_stat["v_bet"] += self.bet_count[player["playerName"]]
                if player["playerName"] in self.raise_count:
                    p_stat["v_raise"] += self.raise_count[player["playerName"]]

        if self.player_count["Flop"] > 0:
            p_stat["base_line"] = max(self.player_count["Flop"] - 1, playing)
        else:
            p_stat["base_line"] = max(self.player_count["Deal"] - 1, playing)

        return p_stat

    def virtual_player_count(self, oneRound):
        """
        Return virtual player count
        Except real player count also considering the bet/raise/allin in this round
        """
        players_stat = self.player_statistics(oneRound.players)
        v_players = int(players_stat["base_line"]
                        + players_stat["v_bet"]
                        + players_stat["v_raise"]
                        + players_stat["v_allin"])
        print "==== Virtual player count ==== %d  = %d + %d + %d + %d" \
              % (v_players,
                 players_stat["base_line"],
                 players_stat["v_bet"],
                 players_stat["v_raise"],
                 players_stat["v_allin"])
        return v_players

    def calc_win_prob_by_sampling(self, hole_cards, board_cards, data):
        """
        Calculate the probability to win current players by sampling unknown cards
        Compute the probability to win one player first
        And then take the power of virtual player count
        """
        evaluator = deuces.Evaluator()
        o_hole_cards = []
        o_board_cards = []
        for card in hole_cards:
            o_hole_card = deuces.Card.new(card)
            o_hole_cards.append(o_hole_card)
        for card in board_cards:
            o_board_card = deuces.Card.new(card)
            o_board_cards.append(o_board_card)

        n = 1000
        win = 0
        succeeded_sample = 0
        for i in range(n):
            deck = deuces.Deck()
            board_cards_to_draw = 5 - len(o_board_cards)

            o_board_sample = o_board_cards + deck.draw(board_cards_to_draw)
            o_hole_sample = deck.draw(2)

            try:
                my_rank = evaluator.evaluate(o_board_sample, o_hole_cards)
                rival_rank = evaluator.evaluate(o_board_sample, o_hole_sample)
            except:
                continue
            if my_rank <= rival_rank:
                win += 1
            succeeded_sample += 1
        print "==== sampling result ==== win : %d, total : %d" % (win, succeeded_sample)
        win_one_prob = win / float(succeeded_sample)

        win_all_prob = win_one_prob ** self.virtual_player_count(data)
        print "==== Win probability ==== " + str(win_all_prob)
        return win_all_prob

    def calc_win_prob(self, hole_cards, board_cards, oneRound):
        """
        Calculate the probability to win current players.
        Compute the probability to win one player first
        And then take the power of virtual player count
        """
        cards_to_evaluate = hole_cards + ["?", "?"]
        exact_calc = True
        verbose = True
        # claculate probability to win a player
        win_one_prob = holdem_calc.calculate(board_cards, exact_calc, 1, None, cards_to_evaluate, verbose)

        win_all_prob = (win_one_prob[0] + win_one_prob[1]) ** self.virtual_player_count(oneRound)
        print "==== Win probability ==== " + str(win_all_prob)
        return win_all_prob