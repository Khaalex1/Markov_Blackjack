from GameObjects import *
from GameSimu import *
import numpy as np
from pickle import *

"""Main qui simule un certain nombre de parties entre un joueur virtuel et le croupier. On recense les proportions des observations
obtenues avec chaque stratégie"""


#Résultats de la simulation de 20000 parties

prop_classic =  {'Cornelian choice': 0.2512311420307981, '1st Round Bust': 0.06097084343000078, "Dealer's 1st Round Blackjack": 0.02986007973110295, 'Else': 0.6579379348080983}
prop_cornelian =  {'Cornelian choice': 0.9299674267100978, '1st Round Bust': 0.0, "Dealer's 1st Round Blackjack": 0.004071661237785016, 'Else': 0.06596091205211727}
prop_busting =  {'Cornelian choice': 0.0, '1st Round Bust': 0.8711507293354943, "Dealer's 1st Round Blackjack": 0.006077795786061588, 'Else': 0.12277147487844407}
prop_blackjack =  {'Cornelian choice': 0.24441524310118265, '1st Round Bust': 0.0, "Dealer's 1st Round Blackjack": 0.668418747262374, 'Else': 0.08716600963644328}


B = np.array([[0.251, 0.061, 0.030, 0.658],
              [0.930, 0, 0.004, 0.066],
              [0, 0.871, 0.006, 0.123],
              [0.244, 0, 0.668, 0.087]])

"""
Interprétation :
En simulant un très grand nombre de parties de Blackjack entre un joueur virtuel 
et le croupier qui triche, on peut se permettre de transformer des proportions en probabilités via la Loi des grands nombres.
Ainsi à la fin de la simulation : 
- un jeu classique mène à une observation de type 1 (choix cornélien / jeu=15) avec une proba de 8%, 
une observation de type 2 (le joueur saute au 1er tour) avec une proba de 6%, une observation de type 3 (Blackjack intantanné du croupier)
 avec une proba de 4% et une observation de type 4 (autre) avec une probabilité de 82%
- une triche de type 2 (distribution cornélienne) mène à une observation de type 1 (le joueur saute au 1er tour) avec une proba de 100%
- une triche de type 3 (le croupier fait sauter le joueur au 1er tour) mène à une observation de type 2 (le joueur saute au 1er tour)
 avec une proba de 87%, une observation de type 3 (Blackjack intantanné du croupier) avec une proba de 1% et une observation de type 4 (autre)
 avec une proba de 12%
- une triche de type 3 (le croupier tire dès le début un Blackjack)  mène à une observation de type 1 (choix cornélien / jeu=15) 
avec une proba de 8%,  une observation de type 3 (Blackjack intantanné du croupier) avec une proba de 82% et 
une observation de type 4 (autre) avec une probabilité de 10%

NB : Les simulations se font avec un joueur virtuel qui tire une carte jusqu'à atteindre un jeu entre 13 et 16. 
Les proportions ci-dessus peuvent donc varier selon les joueurs, toutefois légèrement car les observations dépendent
peu de la stratégie du joueur, pourvu qu'elle soit raisonnable (peu de tirages au dessus de 17 et peu de coucher en-desous de 13).
"""

if __name__ =="__main__":
    G = GameSimulation()
    nb_games = 200
    G.complete_simugame(nb_games)
    states = G.AI_strat
    obs = G.obs
    prop_cl, prop_cor, prop_bust, prop_bl = G.proportions()
    print("prop_classic = ", prop_cl)
    print("prop_cornelian = ", prop_cor)
    print("prop_busting = ", prop_bust)
    print("prop_blackjack = ", prop_bl)
    print("Observations : ", G.obs)

    # f = open("ensemble_states.txt", "ab")
    # g = open("ensemble_obs.txt", "ab")
    #
    # dump(states, f)
    # dump(obs, g)
    #
    # f.close()
    # g.close()