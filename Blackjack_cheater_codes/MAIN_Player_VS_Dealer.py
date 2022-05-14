from GameObjects import *

"""Main à but récréatif pour permettre de jouer avec le croupier diabolique. Peut permettre de générer les proportions d'observations manuellement"""

if __name__ =="__main__":
    G = Game()
    G.complete_game()
    states = G.AI_strat
    obs = G.obs
    prop_cl, prop_cor, prop_bust, prop_bl = G.proportions()