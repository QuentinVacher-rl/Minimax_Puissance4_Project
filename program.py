from arbre import Arbre
from puissance3 import Puissance
import time


def colonne_unique(state_colonne: dict()):
    """detect if there is only one column payable

    Args:
        state_colonne (dict()): State of columns

    Returns:
        bool or int: return only false if more than one column playable, the column else
    """
    count = 0
    colonne = 0
    for keys in state_colonne:
        if state_colonne[keys] < 6:
            count+=1
            colonne = keys
    if count > 1:
        return False
    else:
        return colonne

def generation_ia(grille: Puissance, nb_coup: int, state_colonne: dict, grille_7_or_12: int) -> Arbre: 
    """Generation de l'ia et calcul de la colonne

    Args:
        grille (Puissance): grille de puissance 4
        nb_coup (int): nb de coups a calculer
        state_colonne (dict): state of columns
        grille_7_or_12 (int): puissance 4 à 7 ou 12 colonnes

    Returns:
        Arbre: instance de la classe Arbre retournée
    """
    ia = Arbre(nb_coup, state_colonne.copy(), grille_7_or_12, grille)
    ia.nvx_des((grille.position ^ grille.mask), grille.mask, "", grille, state_colonne)
    return ia

# Choix jeu 7 ou 12 colonnes
grille_7_or_12 = 7

# Timer à respecter pour les 2 ia
time_sup1 = 10
time_sup2 = 5

time_lower1 = 20
time_lower2 = 20

# nb de coups initiales à calculer pour les 2 ia
nb_coup_j2 = 10
nb_coup_j1 = 10

# "ia" ou "joueur" en fonction de ce qu'on veut
j1 = "ia"
j2 = "joueur"

# création de la grille puissance4
grille = Puissance("o", "x", grille_7_or_12)
print(grille)
vainqueur = False

# comptage du temps
t1 = 0
t2 = 0
t = time.time()

# dictionnaire qui prend en key chaque indice de colonne et value le nb de jetons par colonne
state_colonne = dict()
for i in range(grille.largeur):
    state_colonne[i+1] = 0
i = 0

while(not vainqueur and grille.moves < 42):
    if j1 == "joueur":
        # Tour joueur : choix de colonne
        colonne = int(input())
        print(f"Le joueur joue dans la colonne {colonne}")
        grille.add_coin(colonne, state_colonne)
    elif colonne_unique(state_colonne):
        colonne = colonne_unique(state_colonne)
        grille.add_coin(colonne, state_colonne)
    else:
        time1 = time.time()
        # Generation de l'ia et calcul de la colonne à jouer
        ia = generation_ia(grille, nb_coup_j1, state_colonne, grille_7_or_12)
        grille.add_coin(ia.colonne, state_colonne)
        time_tour = time.time() - time1
        print(f"L'IA joue dans la colonne {ia.colonne} en un temps de {time_tour} secondes avec un calcul de {nb_coup_j1} coups")
        t1 += time_tour
        # Regulation du nb de coups à calculer en fonction du temps à ce tour
        if time_tour < time_sup1: nb_coup_j1 += 1
        elif time_tour > time_lower1: nb_coup_j1 -= 1


    print(grille)
    # Contrôle si fin de partie
    vainqueur = grille.check_win()
    if vainqueur:
        break
    
    if j2 == "joueur":
        # Tour joueur : choix de colonne
        colonne = int(input())
        print(f"Le joueur joue dans la colonne {colonne}")
        grille.add_coin(colonne, state_colonne)
    elif colonne_unique(state_colonne):
        colonne = colonne_unique(state_colonne)
        grille.add_coin(colonne, state_colonne)
    else:
        time1 = time.time()
        # Generation de l'ia et calcul de la colonne à jouer
        ia = generation_ia(grille, nb_coup_j2, state_colonne, grille_7_or_12)
        grille.add_coin(ia.colonne, state_colonne)
        time_tour = time.time() - time1
        print(f"L'IA joue dans la colonne {ia.colonne} en un temps de {time_tour} secondes avec un calcul de {nb_coup_j2} coups")
        t2 += time_tour
        # Regulation du nb de coups à calculer en fonction du temps à ce tour
        if time_tour < time_sup2: nb_coup_j2 += 1
        elif time_tour > time_lower2: nb_coup_j2 -= 1

    print(grille)
    vainqueur = grille.check_win()

tt = time.time()
print("durée partie : " + str(tt - t), "Joueur 1: " + str(t1), "Joueur 2: " + str(t2))
if not vainqueur:
    print("match nul")
    
else:
    print(f"gg {grille.sign1}")
