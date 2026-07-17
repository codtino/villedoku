from flask import Flask, jsonify, render_template, request

from criteria import CRITERES, charger_villes, construire_grille, normalize
from gages import generer_grille_gages

app = Flask(__name__)

VILLES = charger_villes()

# Critères de test fixés (3 pour les colonnes, 3 pour les lignes)
COLONNES_IDS = ["meme_lettre", "finit_r", "double_lettre"]
LIGNES_IDS = ["un_mot", "idf", "100km_paris"]

CRITERES_PAR_ID = {c["id"]: c for c in CRITERES}

# Calculée une seule fois au démarrage : grille[r][c] = liste des villes valides
GRILLE_REPONSES = construire_grille(VILLES, COLONNES_IDS, LIGNES_IDS)

# Liste de toutes les villes (pour proposer des suggestions même incorrectes)
TOUTES_LES_VILLES = sorted(VILLES["nom_standard"])


@app.route("/")
def index():
    column_criteria = [CRITERES_PAR_ID[cid]["label"] for cid in COLONNES_IDS]
    row_criteria = [CRITERES_PAR_ID[rid]["label"] for rid in LIGNES_IDS]
    gage_grid = generer_grille_gages()

    return render_template(
        "index.html",
        column_criteria=column_criteria,
        row_criteria=row_criteria,
        gage_grid=gage_grid,
    )


@app.route("/suggestions")
def suggestions():
    """Retourne toutes les villes (bonnes ou mauvaises réponses) qui contiennent le texte tapé."""
    q = request.args.get("q", "").strip()

    if len(q) < 3:
        return jsonify([])

    q_normalise = normalize(q)
    resultats = []
    for v in TOUTES_LES_VILLES:
        if q_normalise in normalize(v) and v not in resultats:
            resultats.append(v)
        if len(resultats) == 8:
            break
    return jsonify(resultats)


@app.route("/validate", methods=["POST"])
def validate():
    """Vérifie qu'une ville choisie est bien valide pour la case donnée."""
    data = request.get_json()
    row, col, ville = data["row"], data["col"], data["ville"]
    valide = ville in GRILLE_REPONSES[row][col]
    return jsonify({"valid": valide})


if __name__ == "__main__":
    app.run(debug=True)
