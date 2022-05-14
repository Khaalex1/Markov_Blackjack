import numpy as np
import random

"""Scripts recensant la modélisation matricielle du modèle de Markov associé au croupier qui triche, ainsi que des manipulations de base :
 limite du vecteur de distributions, simulations du modèle"""

def pi_star(pi_0, P):
    """
    :param pi_0: Vecteur des distributions initiales
    :param P: Matrice de passage des états
    :return: La limite du vecteur des distributions pi* (tel que pi* = pi*.P ou encore pi* = lim pi_0.P^n)
    """
    return pi_0@np.linalg.matrix_power(P, 1000)

def lim_P(P):
    """
    :param P: Matrice de passage des états
    :return: Limite de P^n (évalué en n=1000)
    """
    return np.linalg.matrix_power(P, 1000)

def eig_pi_star(P):
    """
    :param P: Matrice de passage des états
    :return: La limite du vecteur des distributions pi* par approche analytique (vecteur propre de P associé à 1)
    """
    g = None
    w, v = np.linalg.eig(P.T)
    for i in range(w.shape[0]):
        if np.abs(w[i] - 1.0) < 1e-6:
            g = v[:, i]
    if g[0] < 0:
        g = -g
    g = g / sum(g)
    return g

#Simulation

def simul(states, state_0, P, n):
    """
    Simulation d'un nombre n de transitions d'états du modèle de Markov
    :param states: le vecteur d'états
    :param state_0: l'état initial
    :param P: la matrice de passage
    :param n: le nombre de transitions d'états
    :return: l'état au bout de n transitions d'états
    """
    state = state_0
    for j in range(n+1):
        for i in range(len(states)):
            if state == states[i]:
                state = random.choices(states, weights=tuple(P[i, :]), k = 1)[0]
                break
    return state

def tirages(states, state_0, P, n, nb_tirages):
    """
    Effectue une simulation de n transitions d'états un certain nombre de fois.
    Permet de vérifier la limite de la distribution en recensant la proportion des états finaux
    :param states: le vecteur d'états
    :param state_0: l'état initial
    :param P: la matrice de passage
    :param n: le nombre de transitions d'états
    :param nb_tirages: le nombre de simulation
    :return: vecteur des proportions de chaque état final à la fin de toutes les simulations
    """
    Res = np.zeros(len(states))
    for t in range(nb_tirages):
        state = simul(states, state_0, P, n)
        for i in range(len(states)):
            if state == states[i]:
                Res[i]+=1
    return (1/nb_tirages)*Res


if __name__ == "__main__":

    states = ["Classical", "Cornelian distribution", "Busting the player", "Picking winning cards"]
    #Les états possibles du croupier

    A = np.array([[0.7, 0.1, 0.1, 0.1],
                  [0.5, 0, 0.2, 0.3],
                  [0.5, 0.4, 0, 0.1],
                  [0.6, 0.1, 0.3, 0]])
    """
    A est la matrice de passage des états :
    ligne 1 : probabilités de passer de la stratégie "Classical" aux autres 
    ligne 2 : probabilités de passer de la stratégie "Cornelian distribution" aux autres
    ligne 3 : probabilités de passer de la stratégie "Busting the player" aux autres
    ligne 4 : probabilités de passer de la stratégie "Picking winning cards" aux autres
    """

    lim_A = lim_P(A)
    print("lim A^n  = \n", lim_A)

    pi_0 = A[0] #vecteur des distributions initiales (arbitraire)

    pi_st1 = pi_star(pi_0, A)
    print("lim pi (via puissance de matrice) = \n", pi_st1)

    pi_st2 = eig_pi_star(A)
    print("lim pi (via vecteur propre) = \n", pi_st2)

    nb_simu = 10000  #nb de simulations
    nb_parties = 100   #nb de parties par simulation
    state = states[1] #état initial arbitraire
    print("Proportions en {} tirages = \n{}".format(nb_simu, tirages(states, state, A, nb_parties, nb_simu)))