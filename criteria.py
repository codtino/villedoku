import math
import random
import string
import unicodedata

import pandas as pd

CSV_PATH = "villes_france_20000.csv"

PARIS_LAT = 48.857
PARIS_LON = 2.352

LETTRES = list(string.ascii_uppercase)

# Villes considérées comme "au bord de la mer" (liste établie à la main, approximative)
VILLES_LITTORAL = {
    "Boulogne-sur-Mer", "Calais", "Dunkerque", "Grande-Synthe", "Le Havre",
    "Cherbourg-en-Cotentin", "Dieppe", "Saint-Malo", "Saint-Brieuc", "Brest",
    "Concarneau", "Lorient", "Vannes", "Saint-Nazaire", "La Rochelle",
    "Bayonne", "Anglet", "La Teste-de-Buch", "Gujan-Mestras", "Sète",
    "Frontignan", "Agde", "Marseille", "Martigues", "La Ciotat", "Toulon",
    "La Seyne-sur-Mer", "Hyères", "Six-Fours-les-Plages", "Fréjus",
    "Saint-Raphaël", "Mandelieu-la-Napoule", "Cannes", "Antibes",
    "Cagnes-sur-Mer", "Nice", "Menton", "Ajaccio", "Bastia",
    "Baie-Mahault", "Le Gosier", "Le Moule", "Les Abymes", "Petit-Bourg",
    "Cayenne", "Kourou", "Remire-Montjoly", "Saint-Laurent-du-Maroni",
    "Fort-de-France", "Le Robert", "Koungou", "Mamoudzou", "La Possession",
    "Le Port", "Saint-André", "Saint-Benoît", "Saint-Denis", "Saint-Joseph",
    "Saint-Louis", "Saint-Paul", "Saint-Pierre", "Sainte-Anne",
    "Sainte-Marie", "Sainte-Suzanne",
}

# Villes considérées comme ayant un aéroport (liste établie à la main, approximative)
VILLES_AEROPORT = {
    "Paris", "Orly", "Lyon", "Marseille", "Marignane", "Toulouse", "Blagnac",
    "Nice", "Nantes", "Bouguenais", "Bordeaux", "Mérignac", "Strasbourg",
    "Lille", "Rennes", "Montpellier", "Toulon", "Hyères", "Pau", "Perpignan",
    "Ajaccio", "Bastia", "Brest", "Caen", "Metz", "Poitiers", "Limoges",
    "Tours", "La Rochelle", "Béziers", "Carcassonne", "Chambéry", "Grenoble",
    "Dijon", "Nîmes", "Avignon", "Clermont-Ferrand", "Angers", "Rodez",
    "Brive-la-Gaillarde", "Calais", "Beauvais", "Angoulême", "Annecy", "Vichy",
}

# Départements considérés comme faisant partie de la "diagonale du vide"
DEPARTEMENTS_DIAGONALE_VIDE = {
    "Ardennes", "Meuse", "Haute-Marne", "Nièvre", "Cher", "Indre", "Creuse",
    "Haute-Vienne", "Corrèze", "Cantal", "Lozère", "Aveyron", "Gers", "Landes",
}


def normalize(texte):
    """Retire les accents et met en majuscule (pour comparaisons robustes)."""
    nfkd = unicodedata.normalize("NFKD", str(texte))
    sans_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sans_accents.upper()


def distance_km(lat1, lon1, lat2, lon2):
    """Distance à vol d'oiseau entre deux points GPS (formule de Haversine)."""
    r = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def charger_villes():
    """Charge le CSV et ajoute des colonnes utiles au calcul des critères."""
    df = pd.read_csv(CSV_PATH)
    df["nom_normalise"] = df["nom_standard"].apply(normalize)
    df["distance_paris_km"] = df.apply(
        lambda row: distance_km(
            row["latitude_mairie"], row["longitude_mairie"], PARIS_LAT, PARIS_LON
        ),
        axis=1,
    )
    return df


def _lettres(nom_normalise):
    return [c for c in nom_normalise if c.isalpha()]


def _double_lettre(row):
    lettres = _lettres(row["nom_normalise"])
    return any(lettres[i] == lettres[i + 1] for i in range(len(lettres) - 1))


def _lettres_uniques(row):
    lettres = _lettres(row["nom_normalise"])
    return len(lettres) == len(set(lettres))


def _meme_lettre(row):
    lettres = _lettres(row["nom_normalise"])
    return bool(lettres) and lettres[0] == lettres[-1]


def _idf(row):
    return row["reg_nom"] == "Île-de-France"


def _plus_100km_paris(row):
    return row["distance_paris_km"] > 100


def _bord_mer(row):
    return row["nom_standard"] in VILLES_LITTORAL


def _aeroport(row):
    return row["nom_standard"] in VILLES_AEROPORT


def _diagonale_vide(row):
    return row["dep_nom"] in DEPARTEMENTS_DIAGONALE_VIDE


def construire_pool_criteres(villes):
    """
    Construit la liste de tous les critères possibles : les critères fixes,
    plus un critère par lettre de l'alphabet pour chacun des 3 critères
    paramétrés (commence par / finit par / ne contient pas). Les critères
    dont l'ensemble de villes valides est vide sont écartés du pool.
    """
    pool = []

    criteres_fixes = [
        ("double_lettre", "A deux mêmes lettres qui se suivent", _double_lettre),
        ("lettres_uniques", "S'écrit en une seule fois (aucune lettre répétée)", _lettres_uniques),
        ("meme_lettre", "Commence et finit par la même lettre", _meme_lettre),
        ("idf", "Région Île-de-France", _idf),
        ("plus_100km_paris", "À plus de 100 km de Paris", _plus_100km_paris),
        ("bord_mer", "Au bord de la mer", _bord_mer),
        ("aeroport", "A un aéroport", _aeroport),
        ("diagonale_vide", "Dans la diagonale du vide", _diagonale_vide),
    ]

    for critere_id, label, test in criteres_fixes:
        mask = villes.apply(test, axis=1)
        valides = set(villes.loc[mask, "nom_standard"])
        if valides:
            pool.append({"id": critere_id, "label": label, "valides": valides})

    for lettre in LETTRES:
        mask = villes["nom_normalise"].apply(
            lambda n, l=lettre: bool(_lettres(n)) and _lettres(n)[0] == l
        )
        valides = set(villes.loc[mask, "nom_standard"])
        if valides:
            pool.append({"id": f"commence_{lettre}", "label": f"Commence par un {lettre}", "valides": valides})

    for lettre in LETTRES:
        mask = villes["nom_normalise"].apply(
            lambda n, l=lettre: bool(_lettres(n)) and _lettres(n)[-1] == l
        )
        valides = set(villes.loc[mask, "nom_standard"])
        if valides:
            pool.append({"id": f"finit_{lettre}", "label": f"Finit par un {lettre}", "valides": valides})

    for lettre in LETTRES:
        mask = villes["nom_normalise"].apply(lambda n, l=lettre: l not in n)
        valides = set(villes.loc[mask, "nom_standard"])
        if valides:
            pool.append({"id": f"sans_{lettre}", "label": f"Ne contient pas de {lettre}", "valides": valides})

    return pool


def generer_grille(villes, essais_max=3000):
    """
    Sélectionne aléatoirement 3 critères de colonnes et 3 critères de lignes
    parmi tout le pool disponible, en garantissant qu'au moins une ville
    valide existe pour chacune des 9 cases.

    Retourne (column_criteria, row_criteria, grille_reponses, grille_comptes) :
      - column_criteria / row_criteria : listes de 3 libellés affichés
      - grille_reponses[r][c] : liste des noms de villes valides pour la case
      - grille_comptes[r][c] : nombre de réponses valides pour la case
    """
    pool = construire_pool_criteres(villes)

    for _ in range(essais_max):
        selection = random.sample(pool, 6)
        colonnes = selection[:3]
        lignes = selection[3:]

        grille_reponses = []
        valide = True
        for ligne in lignes:
            rangee = []
            for colonne in colonnes:
                reponses = sorted(ligne["valides"] & colonne["valides"])
                if not reponses:
                    valide = False
                    break
                rangee.append(reponses)
            if not valide:
                break
            grille_reponses.append(rangee)

        if valide:
            column_criteria = [c["label"] for c in colonnes]
            row_criteria = [l["label"] for l in lignes]
            grille_comptes = [[len(cellule) for cellule in rangee] for rangee in grille_reponses]
            return column_criteria, row_criteria, grille_reponses, grille_comptes

    raise RuntimeError("Impossible de générer une grille valide après plusieurs essais.")
