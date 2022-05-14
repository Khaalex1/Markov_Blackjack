import numpy as np
import random
from itertools import product
import pickle

"""
Une approche par dictionnaire pour modéliser les HMM est présentée dans ce script. A chaque état correspond un numéro que l'on peut identifier 
à partir des matrices de transition A et d'émission B, par exemple A[i,j] représente la probabilité de passer de l'état i à l'état j.
Ici on se servira toujours de cette identification, par exemple en associant "Classical" à l'état 0 et "Cornelian choice" à l'état 1 
mais on définira des dictionnaires rendant plus explicites les matrices précédentes en permettant d'identifier des strings 
à des états/transitions. Par exemple a[("Classical", "Cornelian choice")] = A[0,1]
"""

def a_str(states, A):
    """
    Fonction auxiliaire pour donner a_ij de façon explicite sous forme de dico
    :param states: les états possibles sous forme d'une liste de strings. Ex : states = ["Chaud", "Froid"]
    :return: les probabilités de passage dans le dico a, ex : a = {'C->F' : 0.2, ...}
    """
    a = {}
    for i in range(len(states)):
        for j in range(len(states)):
            a[(states[i], states[j])] = A[i, j]
    return a


def b_str(states, obs, B):
    """
    Fonction auxiliaire pour donner b_x(y) de façon explicite sous forme de dico
    :param states: les états possibles sous forme d'une liste de strings
    :param obs: les observations possibles sous forme d'une liste de strings
    :return: les probabilités b_x(y) d'avoir l'observation y en étant dans l'état x à une étape donnée, ex : b = {'C->G' : 0.8, ...}
    """
    b = {}
    for i in range(len(states)):
        for j in range(len(obs)):
            b[(states[i], obs[j])] = B[i, j]
    return b

def pi_str(states, pi_0):
    pi = {}
    for i in range(len(states)):
        pi[states[i]] = pi_0[0,i]
    return pi


def P(X, Y, pi, a, b):
    """
    Fonction donnant la proba P(X,Y) avec X une liste d'états et Y une liste d'observatons.
    C'est alors la proba d'avoir cette succession d'états et cette succession d'observation simultanément
    :param X: Succession d'états sous forme de chaîne ou liste de chaînes. Exemple : X = "CCFF"
    :param Y: Succession d'observations sous forme de chaîne ou liste de chaînes. Exemple : Y = "PPMG"
    :param pi: Distribution initiale des états
    :param a: dico a explicitant les a_ij
    :param b: dico b explicitant les b_xi(yj)
    :return: p la proba P(x,y)
    """
    p = pi[X[0]]*b[(X[0],Y[0])]
    for i in range(1, len(Y)):
        p = p*a[(X[i-1], X[i])]*b[(X[i],Y[i])]
    return p

def pstate(states, y, pi_0, a, b):
    """
    Retourne un dictionnaire p qui contient les différentes successions d'états sous forme de chaîne
     associées à leur proba simultannée avec y la succession d'observations. ex : pstate = {"PPPP" : 0.01, "PPPG": 0.001, ...}
     NB : Approche très visuelle mais sous optimale avec plus de 10 observations (nombre de combinaisons exponentiel)
    :param states:
    :param y: vecteur d'observation (chaîne). Ex : y = "PPMG"
    :param pi_0: distribution initiale (array ligne)
    :param a: dico des probas de passages a_ij
    :param b: dico des probas d'avoir y en étant à l'état x b_x(y)
    :return: dico p
    """
    p = {}
    for c in product(states, repeat=len(y)):
        s = ""
        for i in range(len(c)):
            s += c[i]
        p[s] = 0
    for key in p:
        p[key] = P(key, y, pi_0, a, b)
    return p

def pstate_norm(pstate):
    """
    Même type de fonction que pstate mais en normalisant les probas
    :param pstate: dico des associations séquence-proba
    :return: p_state normalisé
    """
    pstate_norm = {}
    p_tot = sum(list(pstate.values()))
    for key in pstate:
        pstate_norm[key] = pstate[key] / p_tot
    return pstate_norm

def alpha(Y, states, a, b, pi):
    """
    alpha du Forward Algo
    :param Y: vecteur des obs (string/liste de strings)
    :param states: les états possibles (string/liste de strings)
    :param a: dico des a_ij. Ex : a = {('Chaud', 'Froid') : 0.2, ...}
    :param b: dico des b_x(y). Ex : b = {('Chaud','Petit') : 0.1, ...}
    :param pi: distribution initiale (array ligne). Ex : p = [[0.6, 0.4]]
    :return: alpha (matrice) des alpha_i(j)
    """
    N = len(states)
    T = len(Y)
    alp = np.zeros((T, N))
    for i in range(N):
        alp[0, i] = pi[states[i]]*b[(states[i], Y[0])]
    for t in range(1, len(Y)):
        for i in range(N):
            for j in range(N):
                alp[t, i] += alp[t-1,j]*a[(states[j], states[i])]
            alp[t,i] = alp[t,i]*b[(states[i], Y[t])]
    return alp

def beta(Y, states, a, b, pi):
    """
    beta du Backward Algo
    :param Y: vecteur des obs (string/liste de strings)
    :param states: les états possibles (string/liste de strings)
    :param a: dico des a_ij. Ex : a = {'Chaud->Froid" : 0.2, ...}
    :param b: dico des b_x(y). Ex : b = {'Chaud->Petit" : 0.1, ...}
    :param pi: distribution initiale (array ligne). Ex : p = [[0.6, 0.4]]
    :return: alpha (matrice) des alpha_i(j)
    """
    N = len(states)
    T = len(Y)
    bet = np.zeros((T, N))
    for i in range(N):
        bet[T-1, i] = 1
    for t in range(T-2, -1, -1):
        for i in range(N):
            for j in range(N):
                bet[t, i] += a[(states[i], states[j])]*b[(states[j], Y[t+1])]*bet[t+1,j]
    return bet


def Py(Y, states, a, b, pi):
    """
    Retourne P(Y | modèle lambda) avec forward algo
    :param Y: vecteur des obs (string/liste de strings)
    :param states: les états possibles (string/liste de strings)
    :param a: dico des a_ij. Ex : a = {'Chaud->Froid" : 0.2, ...}
    :param b: dico des b_x(y). Ex : b = {'Chaud->Petit" : 0.1, ...}
    :param pi: distribution initiale (array ligne). Ex : p = [[0.6, 0.4]]
    :return: P(Y | modeèle lambda) (float)
    """
    N = len(states)
    T = len(Y)
    alpha0 = alpha(Y, states, a, b, pi)
    p = 0
    for i in range(N):
        p += alpha0[T-1, i]
    return p

def BA(Y, states, a, b, pi):
    """
    Retourne P(Y | modeèle lambda) avec BA
    :param Y: vecteur des obs (liste de strings)
    :param states: les états possibles (liste de strings)
    :param a: dico des a_ij. Ex : a = {'Chaud->Froid" : 0.2, ...}
    :param b: dico des b_x(y). Ex : b = {'Chaud->Petit" : 0.1, ...}
    :param pi: distribution initiale (array ligne). Ex : p = [[0.6, 0.4]]
    :return: P(Y | modeèle lambda) (float)
    """
    N = len(states)
    T = len(Y)
    beta0 = beta(Y, states, a, b, pi)
    p = 0
    for i in range(N):
        p += beta0[0, i]*b[(states[i], Y[0])]*pi[states[i]]
    return p

def digamma_t(Y, t, states, a, b, pi):
    """
    matrice des digamma_ij à l'époque t
    :param Y: vecteur d'obs (chaîne/liste de chaînes). Ex : Y = "PPMG"
    :param t: époque de l'évaluation (int)
    :param states: vecteur des état possibles (chaîne/liste de chaînes). Ex : states = ['C', 'F']
    :param a: dico des a_ij. Ex : a = {"C->F" : 0.2, ...}
    :param b: dico des b_x(y). Ex : b = {"C->P" : 0.1}
    :param pi: distribution initiale (array ligne). Ex : pi = [[0.6, 0.4]]
    :return:  matrice des digamma_ij à l'époque t (NxN)
    """
    N = len(states)
    T = len(Y)
    if t <T-1:
        dig = np.zeros((N,N))
        alpha0 = alpha(Y,states, a, b, pi)
        beta0 = beta(Y,states, a, b, pi)
        PY = Py(Y,states, a, b, pi)
        for i in range(N):
            for j in range(N):
                dig[i,j]=(alpha0[t,i]*a[(states[i], states[j])]*b[(states[j], Y[t+1])]*beta0[t+1,j])/PY
        return dig
    else :
        dig = np.zeros((N, N))
        alpha0 = alpha(Y, states, a, b, pi)
        PY = Py(Y, states, a, b, pi)
        for i in range(N):
            for j in range(N):
                dig[i, j] = (alpha0[t, i] * a[(states[i], states[j])])/ PY
        return dig


def gamma_t_i(Y, t, i, states, a, b, pi):
    """
    Somme de digamma_t(Y, t, i, states, a, b, pi) sur la ligne i
    :param Y:
    :param t:
    :param i:
    :param states:
    :param a:
    :param b:
    :param pi:
    :return: Somme de digamma_t(Y, t, i, states, a, b, pi) sur la ligne i
    """
    T = len(Y)
    N = len(states)
    dig = digamma_t(Y, t, states, a, b, pi)
    dig_i = 0
    for j in range(N):
            dig_i += dig[i,j]
    return dig_i


def HMM_ML(Y, states, obs, a, b, pi):
    """
    Trouve un nouveau modèle de Markov vraisemblable à partir des observations
    :param Y: vecteur d'obs (chaîne/liste de chaînes). Ex : Y = "PPMG"
    :param states: vecteur des état possibles (chaîne/liste de chaînes). Ex : states = ['C', 'F']
    :param obs: vecteur des obserations possibles (chaîne/liste de chaînes). Ex : obs = ['P', 'M', 'G']
    :param a: dico des a_ij. Ex : a = {"C->F" : 0.2, ...}
    :param b: dico des b_x(y). Ex : b = {"C->P" : 0.1}
    :param pi: distribution initiale (array ligne). Ex : pi = [[0.6, 0.4]]
    :return: nouvelle distribution initiale pi_new, nouvelle matrice de transition A_new, nouvelle matrice d'émission B_new
    """
    N = len(states)
    M = len(obs)
    T = len(Y)
    A = np.zeros((N,N))
    B = np.zeros((N,M))
    pi_new = np.zeros((1,N))
    for i in range(N):
        pi_new[0,i]=gamma_t_i(Y,0,i, states, a, b, pi)
        for j in range(N):
            num_a = 0
            den_a = 0
            for t in range(T-1):
                num_a += (digamma_t(Y, t, states, a, b, pi))[i,j]
                den_a += gamma_t_i(Y, t, i, states, a, b, pi)
            A[i,j] = num_a/den_a
        for k in range(M):
            num_b = 0
            den_b = 0
            for t in range(T):
                if (Y[t] == obs[k]):
                    num_b += gamma_t_i(Y, t, i, states, a, b, pi)
                den_b += gamma_t_i(Y, t, i, states, a, b, pi)
            B[i,k] = num_b/den_b

    return pi_new, A, B


def predict_HMM(states, yobs, a, b, pi):
    """
    Prédit la succession d'états la plus probable d'après le modèle HMM à partir des FA et BA
    :param states: Les états possibles (liste ou chaîne)
    :param yobs: L'observation (chaîne)
    :return: mat la matrice des probas d'avoir l'état de ligne i à l'étape de colonne j, str_predict la succession d'états la plus probable
    """
    predict_seq = []
    N = len(states)
    T = len(yobs)
    PY = Py(yobs, states, a, b, pi)
    for t in range(T):
        dig_max = 0
        imax = 0
        for i in range(N):
            dig = gamma_t_i(yobs, t, i, states, a, b, pi)
            if dig >= dig_max:
                dig_max = dig
                imax = i
        predict_seq += [states[imax]]
    return predict_seq

def viterbi(y, states, a, b, pi):
    T = len(y)
    N = len(states)
    delta = np.zeros((T,N))
    psi = np.zeros((T, N))
    Q= np.zeros((T,1), dtype = "int")
    X_star = []
    for i in range(N):
        delta[0,i] = np.log(1+pi[states[i]]*b[(states[i], y[0])])
        psi[0,i] = 0
    for t in range(1,T):
        for j in range(N):
            da = np.zeros((1,N))
            for i in range(N):
                da[0,i]=np.log(1+delta[t-1,i]) + np.log(1+a[(states[i], states[j])])
            delta[t,j]=np.amax(da) + np.log(1+b[(states[j], y[t])])
            psi[t,j] = int(np.argmax(da))
    Q[T-1,0] = int(np.argmax(delta[T-1,:]))
    X_star += [states[Q[T-1,0]]]
    for t in range(T-2,-1,-1):
        Q[t,0]=psi[t+1,Q[t+1]]
        X_star += [states[Q[t,0]]]
    X_star.reverse()
    return X_star

def re_scaling():
    pass

def compare(real_states, predict_states):
    """
    Retourne la proportion de vraisemblance entre une séquence d'états et sa prédiction via HMM
    :param real_states: La séquence d'états réelle
    :param predict_states: La séquence d'états prédite
    :return: Proportion de vraisemblance (float entre 0 et 1)
    """
    N = len(real_states)
    count = 0
    for i in range(N):
        if real_states[i]==predict_states[i]:
            count +=1
    return count/N

def mat_differences(real_states, predict_states, oseq = None):
    """
    Matrice de comparaison entre les états réels et prédits
    :param real_states: les états réels
    :param predict_states: les états prédits
    :param predict_states: éventuelle 2e séquence d'états prédite (pat exemple DP) à comparer
    :return: array à len(real_states) lignes et 2 ou 3 col
    """
    if oseq == None:
        dif = np.zeros((len(real_states), 2), dtype="<U30")
        for i in range(len(real_states)):
            dif[i, 0] = real_states[i]
            dif[i,1]=predict_states[i]
    else :
        dif = np.zeros((len(real_states), 3), dtype="<U30")
        for i in range(len(real_states)):
            dif[i, 0] = real_states[i]
            dif[i,1]=predict_states[i]
            dif[i, 2] = oseq[i]
    return dif

if __name__ == "__main__":

    #init
    #On recense les états et observations possibles

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

    #On ouvre des fichiers binaires contenant les états et les observations de 20 séquences de 200 parties.
    #On s'intéresse à la première séquence seulement

    f = open("ensemble_states.txt", "rb")
    g = open("ensemble_obs.txt", "rb")

    all_states = pickle.load(f)
    all_obs = pickle.load(g)

    f.close()
    g.close()

    T = len(all_obs)
    nb_obs = len(obs)
    N = len(states)

     #On déclare les matrices de transition et d'émission REELLES de notre MMC

    A = np.array([[0.7, 0.1, 0.1, 0.1],
                  [0.5, 0, 0.2, 0.3],
                  [0.5, 0.4, 0, 0.1],
                  [0.6, 0.1, 0.3, 0]])

    B = np.array([[0.251, 0.061, 0.030, 0.658],
                  [0.930, 0, 0.004, 0.066],
                  [0, 0.871, 0.006, 0.123],
                  [0.244, 0, 0.668, 0.087]])

    pi_0 = np.array([[0.7, 0.1, 0.1, 0.1]])

    a = a_str(states, A)
    b = b_str(states, obs, B)
    pi = pi_str(states, pi_0)

    print("a_ij = ", a)
    print("b_x(y) = ", b)
    print("pi = ", pi)
    print("\n")

    #Q1
    #On calcule P(Y|lambda) grâce à la méthode Forward

    pyl = BA(all_obs, states, a, b, pi)
    print("Q1")
    print("pY_knowing_lambda = ", pyl)
    print("\n")

    #Q2

    #On prédit les séquences d'états d'une séquence de 200 observations.
    #On prédit une séquence en MMC (algo Backward-Forward) et une séquence en PD (Viterbi)

    seq_pred2 = predict_HMM(states, all_obs, a, b, pi)
    prop_HMM = compare(all_states, seq_pred2)

    seq_DP = viterbi(all_obs, states, a, b, pi)
    prop_DP = compare(all_states, seq_DP)

    mat_dif = mat_differences(all_states, seq_pred2,seq_DP )

    print("Q2")
    print("Matrice de comparaison via HMM et DP \n", mat_dif)
    print("Proportion de vraisemblance (HMM) avec la simulation réelle : ", prop_HMM)
    print("Proportion de vraisemblance (DP) avec la simulation réelle : ", prop_DP)
    print("\n")


    #Q3

    #On déclare des matrices d'approximation pour ensuite apprendre le MMC
    #grâce aux 20 séquences de 200 observations contenues dans les fichiers texte.
    #Le modèle est appris par algorithme de Baum-Welch

    A_approx = np.array([[0.8, 0.05, 0.1, 0.05],
                  [0.6, 0, 0.2, 0.2],
                  [0.6, 0.2, 0, 0.2],
                  [0.7, 0.1, 0.2, 0]])

    B_approx = np.array([[0.15, 0.13, 0.02, 0.70],
                  [0.9, 0, 0.01, 0.09],
                  [0, 0.8, 0.1, 0.1],
                  [0.15, 0, 0.75, 0.1]])

    pi_0 = np.array([[0.8, 0.08, 0.05, 0.07]])


    e_o = []

    with open("ensemble_obs.txt", "rb") as f:
        while True:
            try:
                e_o.append(pickle.load(f))
            except EOFError:
                break
    f.close()

    for all_obs in e_o:
        a = a_str(states, A_approx)
        b = b_str(states, obs, B_approx)
        pi = pi_str(states, pi_0)

        pi_0, A_approx, B_approx = HMM_ML(all_obs, states, obs, a, b, pi)


    print("Q3")
    print("pi_new = \n", pi_0)
    print("A_new = \n", A_approx)
    print("B_new = \n", B_approx)