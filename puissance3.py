# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 22:04:16 2021

@author: Quentin
"""

class Puissance:
    """3eme creation de la classe puissance qui crée le puissance 4

    Cette fois je l'ai créée en utilisant une méthode de bitboard pour enregistrer l'état de la grille très efficacement

    Voir le rapport pour l'explication du fonctionnement

    """
    def __init__(self, p_sign1: str, p_sign2: str, p_largeur:int =7):
        """Initialisation de la grille

        Args:
            p_sign1 (str): premier signe
            p_sign2 (str): deuxième signe
            p_largeur (int, optional): largeur de la grille. Defaults to 7.
        """
        self.sign1 = p_sign1
        self.sign2 = p_sign2
        self.position = 0  
        self.mask = 0
        self.hauteur = 6
        self.largeur = p_largeur
        self.moves = 0
        self.bot_mask = self.bottom()
        self.board_mask = self.bot_mask * ((1 << self.hauteur) - 1) 

    def bottom(self) -> int:
        """renvoie 1 pour les cases bottom de la grille, 0 sinon

        Returns:
            int: bottom
        """
        n = 0
        for i in range(self.largeur):
            n += 2**(i * (self.hauteur + 1))
        return n
        
    def add_coin(self, nb_column: int, state_colonne: dict()):
        """Ajout d'un jeton

        Args:
            nb_column (int): Numéro de la colonne
            state_colonne (dict): state of columns 
        """
        # Test si la colonne est jouable
        if self.test_move(int(nb_column) - 1):
            # Update du mask
            self.mask |= self.mask + self.bottom_mask(int(nb_column) - 1)
            self.moves += 1 # Incrémentation du nombre de coups
            # On inverse les signes pour que l'affichage de la grille affiche toujours le même signe au même joueur
            cur = self.sign2
            self.sign2 = self.sign1
            self.sign1 = cur
            # Update de state colonne
            state_colonne[int(nb_column)] += 1
            # On inverse position pour le joueur suivant
            self.position ^= self.mask
        else:
            # Si le joueur en input a saisi une colonne pleine:
            print("colonne pleine, jouez autre part")
            self.add_coin(int(input()), state_colonne)
    
    def test_move(self, nb_column: int) -> bool:
        """Test si une colonne est jouable

        Args:
            nb_column (int): Colonne testée

        Returns:
            bool: True si jouable
        """
        return (self.mask & self.top_mask(nb_column)) == 0

    def bottom_mask(self, col:int) -> int:
        """Renvoie 1 dans le bitboard à l'emplacement du bas de la colonne:

        Args:
            col (int): colonne cherchée

        Returns:
            int: nb binaire constitué de 0 sauf à l'emplacement du bas de la colonne cherchée
        """
        return 1 << col * (self.hauteur + 1)

    def top_mask(self, col: int) -> int:
        """Renvoie 1 dans le bitboard à l'emplacement du haut de la colonne:

        Args:
            col (int): colonne cherchée

        Returns:
            int: nb binaire constitué de 0 sauf à l'emplacement du haut de la colonne cherchée
        """
        return 1 << self.hauteur - 1 << col*(self.hauteur + 1)


    def check_win(self) -> bool:
        """Regarde si dans la grille actuelle on a un alignement

        Returns:
            bool: True si alignement, False sinon
        """
        return self.alignement(self.position)
    
    def alignement(self, pos: int) -> bool:
        """Observe si on a un alignement de 4 jetons pour le joueur donc la position est donnée

        Args:
            pos (int): position du joueur

        Returns:
            bool: True si alignement
        """
        # Horizontal
        m = pos & (pos >> self.hauteur + 1)
        if m & (m >> (2 * (self.hauteur + 1))): 
            return True

        # Diagonale 1
        m = pos & (pos >> self.hauteur + 2)
        if m & (m >> (2 * (self.hauteur + 2))): 
            return True

        # Diagonale 2
        m = pos & (pos >> self.hauteur)
        if m & (m >> (2 * (self.hauteur))): 
            return True

        # Vertical
        # Explication rapide pour le vertical (les autres fonctionnent pareil mais sont plus longs à expliquer)
        # Supposons qu'on a un alignement, on aura dans le bitboard une chaine de 0 et 1 du type ...01011110...
        # 
        #     CAS ALIGNEMENT :                 |           CAS PAS D'ALIGNEMENT : 
        # pos      : ...01011110...            |       pos      : ...011011100... 
        # pos >> 1 :  ...01011110...           |       pos >> 1 :  ...011011100...
        # donc m   :  ...00011100...           |       donc m   :  ...010011000...
        # On regarde ensuite m et m >> 2 :     |       On regarde ensuite m et m >> 2 :   
        # m        : ...00011100...            |       m        : ...010011000...
        # m >> 2   :   ...00011100...          |       m >> 2   :   ...010011000...
        # Donc on a:   ...00010000...          |       Donc on a:   ...0000000...
        # On return alors True                 |       On return alors False

        m = pos & (pos >> 1)
        if m & (m >> 2):
            return True
        return False
                    
    def possible_gagne(self, pos: int, mask: int) -> int:
        """Calcul du nombre d'alignement de 3 jetons pour le joueur dont la position est donnée

        Attention le nombre d'alignement de 3 jetons ne veut pas dire que : | x | x | x |
        Cela veut aussi dire | x | x |   | x |
        De plus il ne s'agit que d'alignement de 3 jetons où la victoire est encore possible
        | x | x | o | x | ou | x | x | x | o | ne sont pas vu comme des alignements

        Args:
            pos (int): position du joueur
            mask (int): masque de la partie

        Returns:
            int: nb d'alignements
        """

        # Vertical : Très simple a calculer car le puissance 4 est soumis à la gravité
        r = (pos << 1) & (pos << 2) & (pos << 3)

        # Horizontal
        p = (pos << (self.hauteur+1)) & (pos << 2*(self.hauteur+1))
        r |= p & (pos << 3*(self.hauteur+1))
        r |= p & (pos >> (self.hauteur+1))
        p >>= 3*(self.hauteur+1)
        r |= p & (pos << (self.hauteur+1))
        r |= p & (pos >> 3*(self.hauteur+1))

        # Diagonale 1
        p = (pos << self.hauteur) & (pos << 2*self.hauteur)
        r |= p & (pos << 3*self.hauteur)
        r |= p & (pos >> self.hauteur)
        p >>= 3*self.hauteur
        r |= p & (pos << self.hauteur)
        r |= p & (pos >> 3*self.hauteur)

        # Diagonale 2
        p = (pos << (self.hauteur+2)) & (pos << 2*(self.hauteur+2))
        r |= p & (pos << 3*(self.hauteur+2))
        r |= p & (pos >> (self.hauteur+2))
        p >>= 3*(self.hauteur+2)
        r |= p & (pos << (self.hauteur+2))
        r |= p & (pos >> 3*(self.hauteur+2))

        # On renvoie le count de 1 dans le chiffre binaire final
        return (bin(r & (self.board_mask ^ mask))).count("1")

    def __str__(self) -> str:
        """Surchage de la méthode __str__ pour print la grille

        Returns:
            str: grille à afficher
        """
        grille = ["Grille actuelle :" if x == self.hauteur else "| " for x in range(self.hauteur + 1)]
        grille.append(f"Tour : {self.moves}")
        bin_position = bin(self.position)[::-1]
        bin_mask = bin(self.mask)[::-1]
        for i in range(self.largeur):
            for j in range(self.hauteur):
                # Verification que la valeurs existe dans le masque
                if len(bin_mask) > (self.hauteur + 1) * i + j and bin_mask[(self.hauteur + 1) * i + j] == "1":
                    # Si oui on verifie qu'elle existe dans la position, si oui alors c'est le joueur actuel, sinon le joueur adverse
                    if len(bin_position) > (self.hauteur + 1) * i + j and bin_position[(self.hauteur + 1) * i + j] == "1":
                        grille[j] += self.sign1 +" | "
                    #coup nous
                    else:
                        grille[j] += self.sign2 + " | "
                    #coup adverse
                else:
                    grille[j] += "  | "
        grille.reverse()
        # Affichage grille 7 ou 12 colonnes
        if self.largeur == 12:
            grille.append(" ----------------------------------------------- ")
            grille.append("  1   2   3   4   5   6   7   8   9   10  11  12 ")
        else:
            grille.append(" --------------------------- ")
            grille.append("  1   2   3   4   5   6   7 ")    
        return "\n".join(grille)
