
from arbre import colonne_unique, generation_ia
from puissance3 import Puissance

import time

class Environnement:

    def __init__(self, p_grille_largeur: int, p_time_sup: int, p_time_low: int, p_nb_coup: int) -> None:
        # Choix jeu 7 ou 12 colonnes
        self.grille_7_or_12 = p_grille_largeur

        # Timer à respecter pour les 2 ia
        self.init_time_sup = p_time_sup
        self.time_sup1 = self.init_time_sup
        self.time_sup2 = self.init_time_sup

        self.init_time_lower = p_time_low
        self.time_lower1 = self.init_time_lower
        self.time_lower2 = self.init_time_lower

        # nb de coups initiales à calculer pour les 2 ia
        self.init_nb_coup = p_nb_coup
        self.nb_coup_j2 = self.init_nb_coup
        self.nb_coup_j1 = self.init_nb_coup

        # "algo", "ia" ou "joueur" en fonction de ce qu'on veut
        self.j2 = "algo"
        self.j1 = "joueur"

        # création de la grille puissance4
        self.grille = Puissance("o", "x", self.grille_7_or_12)
        self.print(self.grille)
        self.vainqueur = False
        self.done = False

        # comptage du temps
        self.t1 = 0
        self.t2 = 0

        # dictionnaire qui prend en key chaque indice de colonne et value le nb de jetons par colonne
        self.state_colonne = {i+1 : 0 for i in range(self.grille.largeur)}

    def step(self):

        if self.j1 == "joueur":
            # Tour joueur : choix de colonne
            self.tour_joueur()
        elif self.j1 == "algo":
            self.t1, self.nb_coup_j1 = self.tour_algo()

        elif self.j1 == "ia":
            ""

        self.render()
        # Contrôle si fin de partie
        self.vainqueur = self.grille.check_win()
        if self.vainqueur:
            self.done = True
            return
        
        if self.j2 == "joueur":
            self.tour_joueur()

        elif self.j2 == "algo":
            self.t2, self.nb_coup_j2 = self.tour_algo()

        elif self.j2 == "ia":
            ""

        self.render()
        self.vainqueur = self.grille.check_win()
        if self.grille.moves == 42:
            self.done = True

    def reset(self):
        self.time_sup1 = self.init_time_sup
        self.time_sup2 = self.init_time_sup

        self.time_lower1 = self.init_time_lower
        self.time_lower2 = self.init_time_lower

        self.nb_coup_j2 = self.init_nb_coup
        self.nb_coup_j1 = self.init_nb_coup

        self.t1 = 0
        self.t2 = 0

        self.grille = Puissance("o", "x", self.grille_7_or_12)
        self.vainqueur = False

        self.state_colonne = {i+1 : 0 for i in range(self.grille.largeur)}

    def render(self):
        print(self.grille)

    def tour_joueur(self):
        """Make a player move

        Args:
            grille (Puissance): Grille of 4 in a row
            state_colonne (dict): state column
        """
        colonne = int(input())
        print(f"Le joueur joue dans la colonne {colonne}")
        self.grille.add_coin(colonne, self.state_colonne)


    def tour_algo(self):
        time1 = time.time()
        # Generation de l'ia et calcul de la colonne à jouer
        ia = generation_ia(self.grille, self.nb_coup_j1, self.state_colonne, self.grille_7_or_12)
        self.grille.add_coin(ia.colonne, self.state_colonne)
        time_tour = time.time() - time1
        print(f"L'IA joue dans le colonne {ia.colonne} en un temps de {time_tour} secondes avec un calcul de {self.nb_coup_j1} coups et un poids de {ia.nodes['']}")
        self.t1 += time_tour
        # Regulation du nb de coups à calculer en fonction du temps à ce tour
        if time_tour < self.time_sup1: self.nb_coup_j1 += 1
        elif time_tour > self.time_lower1: self.nb_coup_j1 -= 1
        return self.t1, self.nb_coup_j1