import numpy as np
import random
from itertools import product

"""Dans ce fichier on créé les classes et les méthodes qui ont permettre de simuler des parties
entre un joueur réel et le croupier tout en générant les oservations correspondantes"""

class Record:

    obs1 = "Cornelian choice"
    obs2 = "1st Round Bust"
    obs3 = "Dealer's 1st Round Blackjack"
    obs4 = "Else"

    def __init__(self, dist, first, last, dcards, dvalue, status):
        self.player_distribution = dist
        self.first = first
        self.last = last
        self.dealer_cards = dcards
        self.dealer_value = dvalue
        self.win = status

    def __str__(self):
        return "player's distribution = " + str(self.player_distribution) + ", First card = " + str(self.first) + ", Last card = " + str(self.last) + ", Win = " + str(self.win) + "\n"

    def observation(self):
        if ((self.player_distribution >=14) and (self.player_distribution <= 16)):
            return self.obs1
        elif ((self.player_distribution <= 13) and (self.first > 21)):
            return self.obs2
        elif ((self.last <= 21) and (self.dealer_value == 21) and (self.dealer_cards == 2)):
            return self.obs3
        else :
            return self.obs4

class Game :

    cards = {
        '2':2,
        '3':3,
        '4':4,
        '5':5,
        '6':6,
        '7':7,
        '8':8,
        '9':9,
        '10':10,
        'J':10,
        'Q':10,
        'K':10,
        'A':11
    }

    A = np.array([[0.7, 0.1, 0.1, 0.1],
                  [0.5, 0, 0.2, 0.3],
                  [0.5, 0.4, 0, 0.1],
                  [0.6, 0.1, 0.3, 0]])


    strat0 = "Classical"
    strat1 = "Cornelian distribution"
    strat2 = "Busting the player"
    strat3 = "Instant Blackjack"

    all_strats = [strat0, strat1, strat2, strat3]

    def __init__(self):
        self.all_cards = random.choices(list(self.cards.keys()), weights=tuple(13*[1/13]), k=100000)
        random.shuffle(self.all_cards)
        self.AI_strat = []
        self.records = []
        self.obs = []
        self.player_gain = 0

    def classical_initial_pick(self):

        player_card1 = self.all_cards.pop(0)
        dealer_card1 = self.all_cards.pop(0)
        player_card2 = self.all_cards.pop(0)
        dealer_card2 = self.all_cards.pop(0)
        # print("Player's initial pick : ", [player_card1, player_card2])
        # print("Dealer's initial pick (hidden) : ", [dealer_card1, "face-down card"])
        return [player_card1, player_card2], [dealer_card1, dealer_card2]

    def classical_pick(self):
        init_ppick = None
        first_ppick = None
        last_ppick = None

        dcards = 2
        win = None
        new_ppick, new_dpick = self.classical_initial_pick()

        player_value = self.eval(new_ppick)
        dealer_value = self.eval(new_dpick)

        init_ppick = player_value
        first_ppick = player_value

        print("Dealer's initial pick (hidden) : ", [new_dpick[0], "face-down card"])
        print("Dealer's initial pick value (hidden) : ", self.eval([new_dpick[0]]), "\n")

        print("Player's initial pick : ", new_ppick)
        print("Player's initial pick value : ", player_value, "\n")

        print("Take (t) or Leave (l)")
        player_choice = input()
        while not ((player_choice == "t") or (player_choice == "l")):
            print("Take (t) or Leave (l)")
            player_choice = input()
        while (player_choice == "t") :
            card = self.all_cards.pop(0)
            new_ppick = new_ppick +[card]
            player_value = self.eval(new_ppick)
            if first_ppick ==init_ppick:
                first_ppick = player_value
            print("Player's new pick : ", new_ppick)
            print("Player's pick value = ", player_value)
            if (player_value > 21):
                last_ppick = player_value
                win = False
                rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
                self.records += [rec]
                return "YOU BUST. YOU LOSE"
            else :
                print("Take (t) or Leave (l)")
                player_choice = input()

        last_ppick = player_value

        print("Player's pick value : ", player_value)
        print("Player's turn ends. Dealer's turn begins \n")

        print("Dealer's initial pick (revealed) : ", new_dpick)
        print("Dealer's pick value : ", dealer_value)
        while ((dealer_value < 17) and (dealer_value<player_value)):
            card = self.all_cards.pop(0)
            new_dpick = new_dpick + [card]
            dcards +=1
            dealer_value = self.eval(new_dpick)
            print("Dealer's new pick : ", new_dpick)
            print("Dealer's pick value = ", dealer_value)
            if (dealer_value > 21):
                win = True
                rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
                self.records += [rec]
                return "DEALER BUSTS. YOU WIN"

        print("Dealer's turn ends")
        if player_value > dealer_value:
            win = True
            rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
            self.records += [rec]
            return "YOU WIN THIS GAME"
        else :
            win = False
            rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
            self.records += [rec]
            return "YOU LOSE THIS GAME"

    def cornelian_initial_pick(self):

        player_card1 = None
        player_card2 = None
        player_card1 = self.all_cards.pop(0)
        dealer_card1 = self.all_cards.pop(0)

        player_value = self.cards[player_card1]
        diff = random.randint(14, 16) - player_value

        if diff>11:
            diff = 11

        for key in self.cards:
            if ((self.cards[key]==diff)):
                player_card2 = key
                break

        dealer_card2 = self.all_cards.pop(0)
        #self.current_count += 4
        return [player_card1, player_card2], [dealer_card1, dealer_card2]

    def cornelian_pick(self):
        init_ppick = None
        first_ppick = None
        last_ppick = None
        dcards =2
        win = None

        new_ppick, new_dpick = self.cornelian_initial_pick()

        player_value = self.eval(new_ppick)
        dealer_value = self.eval(new_dpick)

        init_ppick = player_value
        first_ppick = player_value

        print("Dealer's initial pick (hidden) : ", [new_dpick[0], "face-down card"])
        print("Dealer's initial pick value (hidden) : ", self.eval([new_dpick[0]]), "\n")

        print("Player's initial pick : ", new_ppick)
        print("Player's initial pick value : ", player_value, "\n")

        print("Take (t) or Leave (l)")
        player_choice = input()
        while not ((player_choice == "t") or (player_choice == "l")):
            print("Take (t) or Leave (l)")
            player_choice = input()
        while (player_choice == "t"):
            card = self.all_cards.pop(0)
            new_ppick = new_ppick + [card]
            player_value = self.eval(new_ppick)
            if first_ppick == init_ppick:
                first_ppick = player_value
            print("Player's new pick : ", new_ppick)
            print("Player's pick value = ", player_value)
            if (player_value > 21):
                last_ppick = player_value
                win = False
                rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
                self.records += [rec]
                return "YOU BUST. YOU LOSE"
            else:
                print("Take (t) or Leave (l)")
                player_choice = input()

        last_ppick = player_value

        print("Player's pick value : ", player_value)
        print("Player's turn ends. Dealer's turn begins \n")

        print("Dealer's initial pick (revealed) : ", new_dpick)
        print("Dealer's pick value : ", dealer_value)
        while ((dealer_value < 17) and (dealer_value<player_value)):
            card = self.all_cards.pop(0)
            new_dpick = new_dpick + [card]
            dcards+=1
            dealer_value = self.eval(new_dpick)
            print("Dealer's new pick : ", new_dpick)
            print("Dealer's pick value = ", dealer_value)
            if (dealer_value > 21):
                win = True
                rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
                self.records += [rec]
                return "DEALER BUSTS. YOU WIN"

        print("Dealer's turn ends")
        if player_value > dealer_value:
            win = True
            rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
            self.records += [rec]
            return "YOU WIN THIS GAME"
        else:
            win = False
            rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
            self.records += [rec]
            return "YOU LOSE THIS GAME"

    def busting_initial_pick(self):
        player_card1 = None

        shuf_card = list(self.cards.keys())
        random.shuffle(shuf_card)
        for key in self.cards:
            if self.cards[key] >= 4 and key != 'A':
                player_card1 = key
                break

        dealer_card1 = self.all_cards.pop(0)

        player_value = self.cards[player_card1]
        diff = random.randint(12,13) - player_value
        player_card2 = 0
        for key in self.cards:
            if (self.cards[key] == diff):
                player_card2 = key
                break

        dealer_card2 = self.all_cards.pop(0)
        #self.current_count += 4
        return [player_card1, player_card2], [dealer_card1, dealer_card2]

    def busting_pick(self):
        init_ppick = None
        first_ppick = None
        last_ppick = None
        dcards = 2
        win = None

        new_ppick, new_dpick = self.busting_initial_pick()

        player_value = self.eval(new_ppick)
        dealer_value = self.eval(new_dpick)

        init_ppick = player_value
        first_ppick = player_value

        print("Dealer's initial pick (hidden) : ", [new_dpick[0], "face-down card"])
        print("Dealer's initial pick value (hidden) : ", self.eval([new_dpick[0]]), "\n")

        print("Player's initial pick : ", new_ppick)
        print("Player's initial pick value : ", player_value, "\n")

        print("Take (t) or Leave (l)")
        player_choice = input()
        while not ((player_choice == "t") or (player_choice == "l")):
            print("Take (t) or Leave (l)")
            player_choice = input()
        while (player_choice == "t"):
            shuf_cards = list(self.cards.keys())
            random.shuffle(shuf_cards)
            for key in shuf_cards:
                card = key
                if self.eval(new_ppick + [card])> 21:
                    new_ppick = new_ppick + [card]
                    player_value = self.eval(new_ppick)
                    break

            if first_ppick == init_ppick:
                first_ppick = player_value
            print("Player's new pick : ", new_ppick)
            print("Player's pick value = ", player_value)
            if (player_value > 21):
                last_ppick = player_value
                win = False
                rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
                self.records += [rec]
                return "YOU BUST. YOU LOSE"

            print("Take (t) or Leave (l)")
            player_choice = input()

        last_ppick = player_value

        print("Player's pick value : ", player_value)
        print("Player's turn ends. Dealer's turn begins \n")

        print("Dealer's initial pick (revealed) : ", new_dpick)
        print("Dealer's pick value : ", dealer_value)
        while ((dealer_value < 17) and (dealer_value<player_value)) :
            card = self.all_cards.pop(0)
            new_dpick = new_dpick + [card]
            dcards +=1
            dealer_value = self.eval(new_dpick)
            print("Dealer's new pick : ", new_dpick)
            print("Dealer's pick value = ", dealer_value)
            if (dealer_value > 21):
                win = True
                rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
                self.records += [rec]
                return "DEALER BUSTS. YOU WIN"

        print("Dealer's turn ends")
        if player_value > dealer_value:
            win = True
            rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
            self.records += [rec]
            return "YOU WIN THIS GAME"
        else:
            win = False
            rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
            self.records += [rec]
            return "YOU LOSE THIS GAME"

    def evil_initial_pick(self):
        dealer_card1 = None
        dealer_card2 = None
        diff = None

        player_card1 = self.all_cards.pop(0)
        magic1 = self.all_cards.pop(0)
        player_card2 = self.all_cards.pop(0)
        magic2 = self.all_cards.pop(0)

        shuf_cards = list(self.cards.keys())
        random.shuffle(shuf_cards)
        for key in shuf_cards:
            if self.cards[key]>=10:
                dealer_card1 = key
                diff = 21 - self.cards[key]
                break
        for key in shuf_cards:
            if self.cards[key]==diff:
                dealer_card2 = key
                break

        return [player_card1, player_card2], [dealer_card1, dealer_card2]


    def evil_pick(self):
        init_ppick = None
        first_ppick = None
        last_ppick = None
        dcards = 2
        win = None

        new_ppick, new_dpick = self.evil_initial_pick()

        player_value = self.eval(new_ppick)
        dealer_value = self.eval(new_dpick)

        init_ppick = player_value
        first_ppick = player_value

        print("Dealer's initial pick (hidden) : ", [new_dpick[0], "face-down card"])
        print("Dealer's initial pick value (hidden) : ", self.eval([new_dpick[0]]), "\n")

        print("Player's initial pick : ", new_ppick)
        print("Player's initial pick value : ", player_value, "\n")

        print("Take (t) or Leave (l)")
        player_choice = input()
        while not ((player_choice == "t") or (player_choice == "l")):
            print("Take (t) or Leave (l)")
            player_choice = input()

        while (player_choice == "t") :
            card = self.all_cards.pop(0)
            new_ppick = new_ppick +[card]
            player_value = self.eval(new_ppick)
            if first_ppick ==init_ppick:
                first_ppick = player_value
            print("Player's new pick : ", new_ppick)
            print("Player's pick value = ", player_value)
            if (player_value > 21):
                last_ppick = player_value
                win = False
                rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
                self.records += [rec]
                return "YOU BUST. YOU LOSE"
            else :
                print("Take (t) or Leave (l)")
                player_choice = input()

        last_ppick = player_value

        print("Player's pick value : ", player_value)
        print("Player's turn ends. Dealer's turn begins \n")

        print("Dealer's initial pick (revealed) : ", new_dpick)
        print("Dealer's pick value : ", dealer_value)

        win = False
        rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
        self.records += [rec]
        return "YOU LOSE THIS GAME"


    def eval(self, cards):

        sum = 0
        ace_detect= 0
        for i in range (len(cards)):
            sum += self.cards[cards[i]]
            if ((i<(len(cards)-1)) and (cards[i]=='A' and sum>21)):
                sum-=10
        if ((cards[-1] == "A") and (sum >21)):
            sum -=10
        return sum

    def rec_to_obs(self):
        self.obs = []
        for i in range(len(self.records)):
            self.obs += [self.records[i].observation()]

    def play(self):
        if len(self.AI_strat)==0:
            strat = random.choices(self.all_strats, weights = [0.7, 0.1, 0.1, 0.1], k=1)[0]
            self.AI_strat+=[strat]
            if strat == self.strat0:
                print(self.classical_pick())
            elif strat == self.strat1:
                print(self.cornelian_pick())
            elif strat == self.strat2:
                print(self.busting_pick())
            else :
                print(self.evil_pick())
        else :
            if self.AI_strat[-1]== self.strat0:
                strat = random.choices(self.all_strats, weights = self.A[0,:], k=1)[0]
            elif self.AI_strat[-1]== self.strat1:
                strat = random.choices(self.all_strats, weights = self.A[1,:], k=1)[0]
            elif self.AI_strat[-1] == self.strat2:
                strat = random.choices(self.all_strats, weights=self.A[2,:], k=1)[0]
            else:
                strat = random.choices(self.all_strats, weights=self.A[3,:], k=1)[0]

            self.AI_strat += [strat]
            if strat == self.strat0:
                print(self.classical_pick())
            elif strat == self.strat1:
                print(self.cornelian_pick())
            elif strat == self.strat2:
                print(self.busting_pick())
            else:
                print(self.evil_pick())

    def complete_game(self):
        print("Play or Quit ? (p/q)")
        play = input()
        if play == "p":
            while play != "q":
                self.play()
                self.obs += [self.records[-1].observation()]
                # print("\n", self.AI_strat[-1])
                # print(self.obs[-1], "\n")
                if self.records[-1].win:
                    self.player_gain +=2
                else:
                    self.player_gain -= 1
                print("\nPlay or Quit ? (p/q)")
                play = input()
        print("END OF THE GAME")
        return "Player's gain = {}".format(self.player_gain)

    def proportions(self):
        obs1 = "Cornelian choice"
        obs2 = "1st Round Bust"
        obs3 = "Dealer's 1st Round Blackjack"
        obs4 = "Else"
        classic = {obs1 : 0, obs2 : 0, obs3 : 0, obs4 : 0}
        cornelian = {obs1 : 0, obs2 : 0, obs3 : 0, obs4 : 0}
        buster = {obs1 : 0, obs2 : 0, obs3 : 0, obs4 : 0}
        blackjack = {obs1 : 0, obs2 : 0, obs3 : 0, obs4 : 0}
        tot_cl = 0
        tot_cor = 0
        tot_bust = 0
        tot_bl = 0
        for i in range(len(self.AI_strat)):
            if self.AI_strat[i]== self.strat0:
                tot_cl +=1
                if self.obs[i] == obs1:
                    classic[obs1]+=1
                elif self.obs[i] == obs2:
                    classic[obs2]+=1
                elif self.obs[i] == obs3:
                    classic[obs3]+=1
                else:
                    classic[obs4]+=1
            elif self.AI_strat[i]== self.strat1:
                tot_cor +=1
                if self.obs[i] == obs1:
                    cornelian[obs1]+=1
                elif self.obs[i] == obs2:
                    cornelian[obs2]+=1
                elif self.obs[i] == obs3:
                    cornelian[obs3]+=1
                else:
                    cornelian[obs4]+=1
            elif self.AI_strat[i]== self.strat2:
                tot_bust +=1
                if self.obs[i] == obs1:
                    buster[obs1]+=1
                elif self.obs[i] == obs2:
                    buster[obs2]+=1
                elif self.obs[i] == obs3:
                    buster[obs3]+=1
                else:
                    buster[obs4]+=1
            else:
                tot_bl +=1
                if self.obs[i] == obs1:
                    blackjack[obs1] += 1
                elif self.obs[i] == obs2:
                    blackjack[obs2] += 1
                elif self.obs[i] == obs3:
                    blackjack[obs3] += 1
                else:
                    blackjack[obs4] += 1

        if ((tot_cor >0) and (tot_bust>0) and (tot_cor>0) and (tot_bl>0)):
            for key in classic:
                classic[key] *= 1/tot_cl
                cornelian[key] *= 1/tot_cor
                buster[key] *= 1/tot_bust
                blackjack[key] *= 1/tot_bl

        return classic, cornelian, buster, blackjack