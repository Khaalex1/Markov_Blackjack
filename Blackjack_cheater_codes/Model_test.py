import numpy as np
import random
from itertools import product
import pickle
from Estimation_Prediction_Amelioration import *

"""Main qui va tester la vraisemblance du MMC appris dans le fichier "Estimation_Prediction_Amelioration.py"""

if __name__ == "__main__":
    # init
    strat0 = "Classical"
    strat1 = "Cornelian distribution"
    strat2 = "Busting the player"
    strat3 = "Instant Blackjack"
    states = [strat0, strat1, strat2, strat3]

    obs1 = "Cornelian choice"
    obs2 = "1st Round Bust"
    obs3 = "Dealer's 1st Round Blackjack"
    obs4 = "Else"
    obs = [obs1, obs2, obs3, obs4]

    f = open("States_temoin.txt", "rb")
    g = open("Observations_temoin.txt", "rb")

    all_states = pickle.load(f)
    all_obs = pickle.load(g)

    f.close()
    g.close()

    T = len(all_obs)
    nb_obs = len(obs)
    N = len(states)

    #modèle obtenu par Machine Learning
    pi_mod = np.array([[1, 0, 0, 0]])

    A_mod = np.array([[0.754, 0.077, 0.078, 0.091],
                      [0.442, 0, 0.230, 0.328],
                      [0.500, 0.331, 0, 0.169],
                      [0.662, 0.023, 0.315, 0]])

    B_mod = np.array([[0.238, 0.059, 0.023, 0.680],
                      [0.853, 0, 0.002, 0.145],
                      [0, 0.861, 0.023, 0.116],
                      [0.121, 0, 0.735, 0.144]])

    a = a_str(states, A_mod)
    b = b_str(states, obs, B_mod)
    pi = pi_str(states, pi_mod)

    seq_pred2 = predict_HMM(states, all_obs, a, b, pi)
    prop_HMM = compare(all_states, seq_pred2)

    seq_DP = viterbi(all_obs, states, a, b, pi)
    prop_DP = compare(all_states, seq_DP)

    mat_dif = mat_differences(all_states, seq_pred2, seq_DP)

    print("Matrice de comparaison via HMM et DP \n", mat_dif)
    print("Proportion de vraisemblance (HMM) avec la simulation réelle : ", prop_HMM)
    print("Proportion de vraisemblance (DP) avec la simulation réelle : ", prop_DP)
    print("\n")