from flask import Flask, jsonify, render_template, request

from criteria import charger_villes, generer_grille, normalize
from gages import generer_grille_gages

app = Flask(__name__)

VILLES = charger_villes()

# Liste de toutes les villes (pour proposer des suggestions même incorrectes)
TOUTES_LES_VILLES = sorted(VILLES["nom_standard"])

# État de la partie en cours (régénéré à chaque chargement de la page d'accueil)
ETAT_JEU = {
    "grille_reponses": None,  # grille_reponses[r][c] = liste des villes valides pour cette case
}


@app.route("/")
def index():
    column_criteria, row_criteria, grille_reponses, grille_comptes = generer_grille(VILLES)
    ETAT_JEU["grille_reponses"] = grille_reponses

    gage_grid = generer_grille_gages()

    return render_template(
        "index.html",
        column_criteria=column_criteria,
        row_criteria=row_criteria,
        gage_grid=gage_grid,
        grille_comptes=grille_comptes,
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
    grille_reponses = ETAT_JEU["grille_reponses"]
    valide = grille_reponses is not None and ville in grille_reponses[row][col]
    return jsonify({"valid": valide})


if __name__ == "__main__":
    app.run(debug=True)
