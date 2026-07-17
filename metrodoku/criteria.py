import math
import unicodedata

import pandas as pd

CSV_PATH = "villes_france_20000.csv"

PARIS_LAT = 48.857
PARIS_LON = 2.352


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


def _commence_finit_meme_lettre(row):
    lettres = [c for c in row["nom_normalise"] if c.isalpha()]
    return bool(lettres) and lettres[0] == lettres[-1]


def _finit_par_r(row):
    lettres = [c for c in row["nom_normalise"] if c.isalpha()]
    return bool(lettres) and lettres[-1] == "R"


def _double_lettre(row):
    lettres = [c for c in row["nom_normalise"] if c.isalpha()]
    return any(lettres[i] == lettres[i + 1] for i in range(len(lettres) - 1))


def _un_seul_mot(row):
    nom = row["nom_standard"]
    return (" " not in nom) and ("-" not in nom)


def _ile_de_france(row):
    return row["reg_nom"] == "Île-de-France"


def _moins_100km_paris(row):
    return row["distance_paris_km"] < 100


# Les 6 critères de test, chacun avec un identifiant, un libellé affiché,
# et une fonction de test appliquée à chaque ligne du tableau des villes.
CRITERES = [
    {"id": "meme_lettre", "label": "Commence et finit par la même lettre", "test": _commence_finit_meme_lettre},
    {"id": "finit_r", "label": "Finit par un R", "test": _finit_par_r},
    {"id": "double_lettre", "label": "A deux mêmes lettres qui se suivent", "test": _double_lettre},
    {"id": "un_mot", "label": "En un seul mot", "test": _un_seul_mot},
    {"id": "idf", "label": "Région Île-de-France", "test": _ile_de_france},
    {"id": "100km_paris", "label": "À moins de 100 km de Paris", "test": _moins_100km_paris},
]


def calculer_villes_valides(villes):
    """Pour chaque critère, calcule l'ensemble des noms de villes qui le respectent."""
    resultat = {}
    for critere in CRITERES:
        mask = villes.apply(critere["test"], axis=1)
        resultat[critere["id"]] = set(villes.loc[mask, "nom_standard"])
    return resultat


def construire_grille(villes, colonnes_ids, lignes_ids):
    """
    Construit la grille de jeu : pour chaque case (ligne, colonne), calcule
    la liste des villes qui satisfont à la fois le critère de ligne ET de colonne.
    Retourne une liste de listes (grille[r][c] = liste de noms de villes valides).
    """
    villes_valides = calculer_villes_valides(villes)

    grille = []
    for ligne_id in lignes_ids:
        ligne = []
        for colonne_id in colonnes_ids:
            reponses = sorted(villes_valides[ligne_id] & villes_valides[colonne_id])
            ligne.append(reponses)
        grille.append(ligne)

    return grille
