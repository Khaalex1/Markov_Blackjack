from GameObjects import *
import numpy as np
import random
from itertools import product

class GameSimulation(Game):
    """
    Classe fille de Game, qui permet de simuler automatiquement des parties entre un joueur virtuel et le croupier.
    Le joueur virtuel tire des cartes jusqu'à avoir un jeu entre 13 et 16. Il ne prend pas de risques au-delà et ne compte pas.
    """

    def classical_simupick(self):
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

        player_choice = None

        ceil = random.randint(13, 16)

        while (player_value < ceil):
            card = self.all_cards.pop(0)
            new_ppick = new_ppick + [card]
            player_value = self.eval(new_ppick)
            if first_ppick == init_ppick:
                first_ppick = player_value
            if (player_value > 21):
                last_ppick = player_value
                win = False
                rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
                self.records += [rec]
                return None

        last_ppick = player_value

        while ((dealer_value < 17) and (dealer_value < player_value)):
            card = self.all_cards.pop(0)
            new_dpick = new_dpick + [card]
            dcards += 1
            dealer_value = self.eval(new_dpick)
            if (dealer_value > 21):
                win = True
                rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
                self.records += [rec]

        if player_value > dealer_value:
            win = True
            rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
            self.records += [rec]
        else:
            win = False
            rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
            self.records += [rec]

    def cornelian_simupick(self):
        init_ppick = None
        first_ppick = None
        last_ppick = None
        dcards = 2
        win = None

        new_ppick, new_dpick = self.cornelian_initial_pick()

        player_value = self.eval(new_ppick)
        dealer_value = self.eval(new_dpick)

        init_ppick = player_value
        first_ppick = player_value
        ceil = random.randint(13, 16)

        while (player_value < ceil):
            card = self.all_cards.pop(0)
            new_ppick = new_ppick + [card]
            player_value = self.eval(new_ppick)
            if first_ppick == init_ppick:
                first_pick = player_value
            if (player_value > 21):
                last_ppick = player_value
                win = False
                rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
                self.records += [rec]
                return None
        last_ppick = player_value

        while ((dealer_value < 17) and (dealer_value < player_value)):
            card = self.all_cards.pop(0)
            new_dpick = new_dpick + [card]
            dcards += 1
            dealer_value = self.eval(new_dpick)
            if (dealer_value > 21):
                win = True
                rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
                self.records += [rec]
        if player_value > dealer_value:
            win = True
            rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
            self.records += [rec]
        else:
            win = False
            rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
            self.records += [rec]

    def busting_simupick(self):
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

        ceil = random.randint(13, 16)

        while (player_value < ceil):
            shuf_cards = list(self.cards.keys())
            random.shuffle(shuf_cards)
            for key in shuf_cards:
                card = key
                if self.eval(new_ppick + [card]) > 21:
                    new_ppick = new_ppick + [card]
                    player_value = self.eval(new_ppick)
                    first_ppick = player_value
                    break

        last_ppick = player_value

        win = False
        rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
        self.records += [rec]

    def evil_simupick(self):
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
        ceil = random.randint(13, 16)

        while (player_value < ceil):
            card = self.all_cards.pop(0)
            new_ppick = new_ppick + [card]
            player_value = self.eval(new_ppick)
            if first_ppick == init_ppick:
                first_pick = player_value
            if (player_value > 21):
                last_ppick = player_value
                win = False
                rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
                self.records += [rec]
                return None

        last_ppick = player_value
        win = False
        rec = Record(init_ppick, first_ppick, last_ppick, dcards, dealer_value, win)
        self.records += [rec]

    def simuplay(self):
        if len(self.AI_strat) == 0:
            strat = random.choices(self.all_strats, weights=[0.7, 0.1, 0.1, 0.1], k=1)[0]
            self.AI_strat += [strat]
            if strat == self.strat0:
                self.classical_simupick()
            elif strat == self.strat1:
                self.cornelian_simupick()
            elif strat == self.strat2:
                self.busting_simupick()
            else:
                self.evil_simupick()
        else:
            if self.AI_strat[-1] == self.strat0:
                strat = random.choices(self.all_strats, weights=self.A[0, :], k=1)[0]
            elif self.AI_strat[-1] == self.strat1:
                strat = random.choices(self.all_strats, weights=self.A[1, :], k=1)[0]
            elif self.AI_strat[-1] == self.strat2:
                strat = random.choices(self.all_strats, weights=self.A[2, :], k=1)[0]
            else:
                strat = random.choices(self.all_strats, weights=self.A[3, :], k=1)[0]
            self.AI_strat += [strat]
            if strat == self.strat0:
                self.classical_simupick()
            elif strat == self.strat1:
                self.cornelian_simupick()
            elif strat == self.strat2:
                self.busting_simupick()
            else:
                self.evil_simupick()

    def complete_simugame(self, nb_games):
        count_games = 0
        while count_games <nb_games:
            self.simuplay()
            self.obs += [self.records[-1].observation()]
            count_games += 1
        print("END OF THE GAME")