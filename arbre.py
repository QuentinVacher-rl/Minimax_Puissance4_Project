# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 22:52:09 2021

@author: Quentin
"""
from puissance3 import Puissance
import time

 # Passage en hexadécimal/décimal
CAS_SUP_10 = {
    10: "A",
    11: "B",
    12: "C"
}


CAS_SUP_10_REVERSE = {
    "A" : 10,
    "B" : 11,
    "C" : 12
}

class Arbre:
    """Class of the ia
        On ne fait qu'une instance pour l'ensemble de l'arbre, chaque noeuds-poids sera stocker dans "self.nodes"
    """
    def __init__(self, p_nb_generations: int, p_state_colonne: dict(), p_nb_descendants: int, p_grille: Puissance):
        """Init the instance

        Args:
            p_nb_generations (int): nb de generation max de l'arbre
            p_state_colonne (dict): state of columns
            p_nb_descendants (int): nb de descendants max: 12 dans le cas du puissance 4 à 12 colonnes
            p_grille (Puissance): grille de puissance 4
        """
        self.nb_generations = p_nb_generations
        self.state_colonne = p_state_colonne
        self.nb_descendants = p_nb_descendants
        self.grille = p_grille
        self.nodes = dict()
        self.colonne = None
        self.value = 0
        # Dictionnaire ou on mémorise les différentes situations pendant notre exploration pour ne pas les recalculer
        self.memories = dict()

        # Un dictionnaire et une liste qui nous permettre de trier plus efficacement la recherche en fonction de la taille de la grille
        # Le dictionnaire renvoie pour une position l'ensemble des cas dans lesquels on peut faire un alignement de 4 jetons
        if self.nb_descendants == 7:
            self.simple_order = ["4","3","5","2","6","1","7"]
            self.grille_gagne_possible = {
                1: [3,4,5,5,4,3],
                2: [4,6,8,8,6,4],
                3: [5,8,11,11,8,5],
                4: [7,10,13,13,10,7],
                5: [5,8,11,11,8,5],
                6: [4,6,8,8,6,4],
                7: [3,4,5,5,4,3]
            }
        else:
            self.simple_order = ["6","7","5","8","4","9","3","A","2","B","1","C"]
            self.grille_gagne_possible = {
            1: [3,4,5,5,4,3],
            2: [4,6,8,8,6,4],
            3: [5,8,11,11,8,5],
            4: [7,10,13,13,10,7],
            5: [8,11,14,14,11,8], # On incrémente 5, 6, 7, 8 car meme si on a autant de chances de faire un
            6: [9,12,15,15,12,9], # alignement en 4, 5, 6, 7, 8 et 9, les colonnes centrales sont plus intéressantes
            7: [9,12,15,15,12,9],
            8: [8,11,14,14,11,8],
            9: [7,10,13,13,10,7],
            10: [5,8,11,11,8,5],
            11: [4,6,8,8,6,4],
            12: [3,4,5,5,4,3]
        }


    def nvx_des(self, position: int, mask: int, valeur_node: str, grille: Puissance, state_colonne: dict()):
        """Méthode récursive pour la creation des enfants d'un noeud

        Args:
            position (int): position du noeud
            mask (int): masque du noeud
            valeur_node (str): chaine de caractère traçant le chemin de la note. Ex: "443" veut dire qu'on est au noeud qui a jouer colonne 4 puis 4 puis 3
            grille (Puissance): grille de puissance 4
            state_colonne (dict): state of colums
        """
        # L'élagage alpha;beta est extrémement efficace si on cherche tout de suite un des meilleurs scénarios
        # On ordonne donc les colonnes pour maximiser nos chances de trouver un des meilleurs scénarios
        # 1er Tri des colonnes pour les chercher dans un ordre plus efficace
        ordre_colonne = self.tri(state_colonne)
        valeur_desc_save = None
        liste_valeur_desc = dict()
        for i in ordre_colonne:
            # Ne pas oublier de passer par les convertisseur hexa/decimal si on est au dessus de 10
            valeur_desc = valeur_node + str(i) if i < 10 else valeur_node + CAS_SUP_10[i]

            # Si la colonne est jouable
            if mask & grille.top_mask(i - 1) == 0:
                # On actualise le mask et la position
                mask_desc = mask | (mask + grille.bottom_mask(i - 1))
                position_desc = position ^ mask

                # Si il y a un alignement pour un noeud enfant, on supprime tous les autres noeuds enfants et on break
                if grille.alignement(position_desc ^ mask_desc):
                    self.calcul_poids(valeur_desc, grille)
                    liste_valeur_desc.clear()
                    break
                
                # Si pas d'alignement, on ajoute l'enfant a la liste des valeurs enfants
                # On calcul dans "pos_gagne" le nombre d'alignement de 3 jetons qui pourraient nous permettre de gagner
                # On s'en serviera par la suite pour faire un dernier tri des colonnes à explorer
                # car de manière générale, plus on a d'alignements de 3 jetons, plus on a de chances d'avoir un bon scénario
                liste_valeur_desc[valeur_desc] = {"mask": mask_desc, "pos": position_desc, "pos_gagne": self.grille.possible_gagne(position_desc ^mask_desc, mask_desc)}


        if liste_valeur_desc:
            # On trie par rapport au nombre d'alignement de 3 jetons
            for valeur_desc in sorted(liste_valeur_desc, reverse=True, key=lambda x: liste_valeur_desc[x]["pos_gagne"]):
                # Initialisation du poids à 0
                self.nodes[valeur_desc] = 0
                # Si le couple position;mask est enregistré dans le dictionnaire de mémoire, on ne calcul par les enfants de cet enfant
                if (liste_valeur_desc[valeur_desc]["mask"], liste_valeur_desc[valeur_desc]["pos"]) in self.memories:
                    self.nodes[valeur_desc] = self.memories[(liste_valeur_desc[valeur_desc]["mask"], liste_valeur_desc[valeur_desc]["pos"])]

                # Sinon si n'est ni à la dernière génération, ni à 42 coups, on calul les enfants de cet enfant en relançant la fonction
                elif len(valeur_desc) < self.nb_generations and (self.grille.moves + len(valeur_node)) < 42:
                    # Copie de state_colonne pour créer une nouvelle référence
                    state_colonne_copy = state_colonne.copy()
                    state_colonne_copy[int(valeur_desc[-1]) if valeur_desc[-1].isnumeric() else CAS_SUP_10_REVERSE[valeur_desc[-1]]] += 1
                    self.nvx_des(liste_valeur_desc[valeur_desc]["pos"], liste_valeur_desc[valeur_desc]["mask"], valeur_desc, grille, state_colonne_copy)
                
                # On regarde entre l'enfant sauvegardé et l'enfant actuel lequel est le meilleur et on enlèvre l'autre
                valeur_desc_save, test = self.check_remove_nodes(valeur_desc, valeur_desc_save)

                # Si on n'a pas supprimé l'enfant actuel, on regarde si on peut faire un élagage alpha ou beta
                if test and self.elagage(valeur_desc):
                    break

        # Une fois tous les enfants calculés, on choisi notre poids parmi ceux-ci
        self.choix_poids(valeur_node)
        # On enregistre également le coupl position; mask dans le dictionnaire de mémoire
        self.memories[(mask, position)] = self.nodes[valeur_node]

    def choix_poids(self, valeur_node: str):
        """Choix du poids parmi les enfants

        Args:
            valeur_node (str): valeur de la node
        """

        valeurs_nodes = []
        # On explore tous nos enfants possibles
        for x in range(1, self.grille.largeur + 1):
            if x > 9:
                val = valeur_node + CAS_SUP_10[x]
            else:
                val = valeur_node + str(x)
            if val in self.nodes:
                # Grâce à la fonction check_remove_nodes, on sait qu'on a toujours plus qu'un seul enfant
                # Donc dès qu'on le truc, on break
                valeurs_nodes = [val, self.nodes[val]]
                break
        # Si on est à la génération 0, on enregistre la colonne
        if len(valeur_node) == 0:
            self.colonne = valeurs_nodes[0] if valeurs_nodes[0].isnumeric() else CAS_SUP_10_REVERSE[valeurs_nodes[0]]
        if valeurs_nodes:
            self.nodes[valeur_node] = valeurs_nodes[1]
        

    
    def calcul_poids(self, valeur_node: str, grille: Puissance):
        """Calcul du poids

        Args:
            valeur_node (str): valeur de la node
            grille (Puissance): grille de puissance 4
        """
        # Si on est impair, c'est le joueur actuel qui gagne donc le poids est positif
        if len(valeur_node)%2 == 1:
            self.nodes[valeur_node] = 43 - (len(valeur_node) + grille.moves)
        # Sinon le joueur adverse gagne donc le poids est négatif
        if len(valeur_node)%2 == 0:
            self.nodes[valeur_node] = (len(valeur_node) + grille.moves) - 43


            

    def elagage(self, valeur_node: str) -> bool:
        """Fonction d'elagage alpha beta

        Pour optimiser au maximum l'élagage, on réduit la fenêtre d'élagage au minimum c'est-à-dire à [-1;1]
        On va donc élaguer des qu'on trouvera un poids supérieur ou inférieur à 0 en fonction de si c'est un élagage alpha ou beta
        Ce n'est pas la meilleure idée lorsqu'on a une heuristique car on veut le meilleur poids
        Cependant ici on se permet d'élaguer car on a détecté qu'on était sûr soit de gagner soit de perdre
        Si on voulait gagner avec le moins de coups possibles on ne ferait pas ça, 
        mais l'objectif est uniquement de gagner peu importe le nombre de coups (tant que c'est inférieur à 42)
        Le temps de calcul gagné en élaguant avec cette fenêtre est considérable

        Args:
            valeur_node (str): valeur de la node

        Returns:
            [bool]: True si on elague, False sinon
        """
        parite = len(valeur_node)%2
        val_node_in_nodes = self.nodes[valeur_node]
        # Elagage si on a un poids différent de 0 en fonction de si on est en élagage alpha ou beta
        if parite == 1 and val_node_in_nodes > 0:
            return True
        if parite == 0 and val_node_in_nodes < 0:
            return True
        # Du fait de l'élagage ci-dessus et de la methode check_remove_node, 
        # Ici on ne pourra faire élaguer que les poids = 0
        # On fait ici un élagage total
        # Si on parle par langage familiale, l'élagage consiste à se comparer au poids de ses "oncles"
        # Cependant on peut aller plus loin et se comparer également à ses grands grands oncles, grands grands grands grands oncles etc
        # La première boucle permet de chercher chaque génération (avec un pas de 2)
        for i in reversed(range(parite, len(valeur_node), 2)):
            # On enregistre la valeur pour ne pas aller la chercher constamment dans le dictionnaire
            valeur_stud = valeur_node[:i]
            # On cherche intelligemment dans les différents enfant de notre grand père (donc nos oncles)
            liste_val = self.simple_order.copy() #Liste des différentes colonnes ordonnées intelligemments
            # Parmi les enfants de notre grand père, si on ne veut que les oncles il faut enlever notre parent
            liste_val.remove(valeur_node[i])
            for x in liste_val:
                # Si on trouve notre oncle, on pourra break
                # Grâce a la fonction check_remove_nodes, on ne peut avoir qu'un oncle
                if valeur_stud + x in self.nodes:
                    if val_node_in_nodes == 0:
                        # On elague si on trouve 0
                        if self.nodes[valeur_stud + x] == 0:
                            return True
                    break
        return False

    def check_remove_nodes(self, valeur_desc: int, valeur_desc_save: int) -> str and bool:
        """On compare l'enfant actuel avec l'enfant sauvegardé. On va garder en sauvegarde le plus intéressant et on supprime l'autre

        Supprimer l'ensemble de nos "frere" nous aidera beaucoup dans plein de différents cas 

        Args:
            valeur_desc (int): enfant actuel
            valeur_desc_save (int): enfant sauvegardé

        Returns:
            str: nouveau enfant sauvegarde
            bool: true si changement d'un enfant sauvegardé, false sinon
        """
        # 1st node of this gen
        if valeur_desc_save is None:
            return valeur_desc, True
        # if ia turn
        elif len(valeur_desc)%2 == 1:
            # if valeur desc > valeur desc save : remove valeur desc save else remove valeur desc 
            if self.nodes[valeur_desc_save] < self.nodes[valeur_desc]:
                self.nodes.pop(valeur_desc_save, None)
                return valeur_desc, True
            else:
                self.nodes.pop(valeur_desc, None)
                return valeur_desc_save, False
        # if player turn, do inverse
        else:
            # if valeur desc > valeur desc save : remove valeur desc save else remove valeur desc 
            if self.nodes[valeur_desc_save] > self.nodes[valeur_desc]:
                self.nodes.pop(valeur_desc_save, None)
                return valeur_desc, True
            else:

                self.nodes.pop(valeur_desc, None)
                return valeur_desc_save, False


    def tri(self, state_colonne: dict()) -> list():
        """Tri pour ordonner les colonnes en fonction de celles qui ont le plus de chance de nous faire gagner

        Args:
            state_colonne (dict()): state of columns

        Returns:
            list(): liste ordonnées
        """
        liste_current = [x for x in state_colonne if state_colonne[x] < 6]
        liste_current.sort(key=lambda val: self.grille_gagne_possible[val][state_colonne[val]], reverse = True)
        return liste_current
