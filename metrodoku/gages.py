import random

# Gages "verts" : la personne qui trouve la bonne réponse les distribue à qui elle veut
GAGES_VERTS = [
    "Donne le cocktail de ton choix au participant de ton choix",
    "Distribue 3 gorgées à la personne de ton choix",
    "Échange ton verre avec quelqu'un pour le reste du tour",
    "Désigne quelqu'un qui doit finir son verre",
    "Choisis la prochaine règle du jeu",
    "Désigne ton binôme pour le prochain tour",
    "Impose une grimace à quelqu'un avant qu'il ne boive",
    "Choisis qui doit raconter une anecdote embarrassante",
]

# Gages "rouges" : la personne qui se trompe doit les faire elle-même
GAGES_ROUGES = [
    "Croque dans un citron",
    "Bois cul sec",
    "Chante le refrain d'une chanson au choix du groupe",
    "Bois avec la main non dominante pendant 2 tours",
    "Imite un animal choisi par le groupe",
    "Bois sans utiliser tes mains",
    "Raconte une histoire drôle, sinon bois deux gorgées",
    "Fais 10 secondes de gainage",
]


def generer_grille_gages(nb_lignes=3, nb_colonnes=3):
    """Génère, pour chaque case de la grille, un gage vert et un gage rouge tirés au hasard."""
    grille = []
    for _ in range(nb_lignes):
        ligne = []
        for _ in range(nb_colonnes):
            ligne.append(
                {
                    "vert": random.choice(GAGES_VERTS),
                    "rouge": random.choice(GAGES_ROUGES),
                }
            )
        grille.append(ligne)
    return grille
