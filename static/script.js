document.querySelectorAll(".cell").forEach((input) => {
    const row = input.dataset.row;
    const col = input.dataset.col;
    const suggestionsBox = document.getElementById(`suggestions-${row}-${col}`);

    input.addEventListener("input", async () => {
        if (jeuTermine) return;

        const q = input.value.trim();
        input.classList.remove("correcte");

        if (q.length < 3) {
            suggestionsBox.innerHTML = "";
            suggestionsBox.style.display = "none";
            return;
        }

        const reponse = await fetch(`/suggestions?row=${row}&col=${col}&q=${encodeURIComponent(q)}`);
        let villes = await reponse.json();

        // Exclut les villes déjà utilisées dans une autre case
        villes = villes.filter((v) => !villeDejaUtilisee(v, input));

        suggestionsBox.innerHTML = "";

        if (villes.length === 0) {
            suggestionsBox.style.display = "none";
            return;
        }

        villes.forEach((ville) => {
            const item = document.createElement("div");
            item.classList.add("suggestion-item");
            item.textContent = ville;
            item.addEventListener("click", () => choisirVille(input, suggestionsBox, row, col, ville));
            suggestionsBox.appendChild(item);
        });

        suggestionsBox.style.display = "block";
    });

    // Ferme les suggestions si on clique ailleurs
    document.addEventListener("click", (e) => {
        if (!input.parentElement.contains(e.target)) {
            suggestionsBox.style.display = "none";
        }
    });
});

let nombreErreurs = 0;
let casesResolues = 0;
let jeuTermine = false;
const NOMBRE_ERREURS_MAX = 3;
const NOMBRE_CASES_TOTAL = 9;

function villeDejaUtilisee(ville, inputActuel) {
    const autresCases = document.querySelectorAll(".cell");
    for (const autre of autresCases) {
        if (autre !== inputActuel && autre.value.trim() === ville) {
            return true;
        }
    }
    return false;
}

function enregistrerErreur() {
    if (nombreErreurs < NOMBRE_ERREURS_MAX) {
        const caseErreur = document.getElementById(`erreur-${nombreErreurs}`);
        caseErreur.classList.add("rempli");
        nombreErreurs++;
    }

    if (nombreErreurs >= NOMBRE_ERREURS_MAX) {
        terminerJeu();
    }
}

function terminerJeu() {
    jeuTermine = true;

    document.querySelectorAll(".cell").forEach((c) => {
        c.disabled = true;
    });

    document.querySelectorAll(".suggestions").forEach((s) => {
        s.style.display = "none";
    });

    const message = document.getElementById("message-fin");
    message.classList.remove("victoire");
    message.textContent = "🍻 Trois erreurs ! Cul sec !";
    message.style.display = "block";
}

function afficherVictoire() {
    jeuTermine = true;

    const message = document.getElementById("message-fin");
    message.classList.add("victoire");
    message.textContent = "💕 je t'aime Scrabletta";
    message.style.display = "block";
}

function resoudreCase(row, col, reussite) {
    const carte = document.getElementById(`carte-${row}-${col}`);
    const avant = document.getElementById(`avant-${row}-${col}`);
    const gageBox = document.getElementById(`gage-${row}-${col}`);

    const texteGage = reussite ? carte.dataset.gageVert : carte.dataset.gageRouge;
    gageBox.textContent = texteGage;
    gageBox.classList.add(reussite ? "vert" : "rouge");
    gageBox.classList.add("visible");

    avant.classList.add("masquee");

    casesResolues++;
    if (casesResolues >= NOMBRE_CASES_TOTAL && !jeuTermine) {
        afficherVictoire();
    }
}

async function choisirVille(input, suggestionsBox, row, col, ville) {
    if (jeuTermine) return;

    if (villeDejaUtilisee(ville, input)) {
        input.value = "";
        input.classList.remove("correcte");
        alert(`"${ville}" est déjà utilisée dans une autre case.`);
        suggestionsBox.innerHTML = "";
        suggestionsBox.style.display = "none";
        return;
    }

    const reponse = await fetch("/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ row: parseInt(row), col: parseInt(col), ville }),
    });
    const resultat = await reponse.json();

    suggestionsBox.innerHTML = "";
    suggestionsBox.style.display = "none";
    input.disabled = true;

    if (resultat.valid) {
        input.value = ville;
        input.classList.add("correcte");
        resoudreCase(row, col, true);
    } else {
        input.value = "";
        input.classList.remove("correcte");
        enregistrerErreur();
        resoudreCase(row, col, false);
    }
}
