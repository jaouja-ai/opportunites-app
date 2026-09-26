"""
app.py — Application principale.
Lancement : python app.py, puis ouvrir http://127.0.0.1:5000
"""
from flask import Flask, render_template, request, redirect, url_for

import database as db
import data_cleaning
from models import STATUTS_POSSIBLES

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Initialisation au démarrage : créer les tables, importer les CSV, nettoyer
# ---------------------------------------------------------------------------
db.init_db()
db.importer_donnees_initiales()
data_cleaning.executer_nettoyage_complet()


# ---------------------------------------------------------------------------
# Accueil : redirige vers l'onglet Opportunités + petites stats
# ---------------------------------------------------------------------------
@app.route("/")
def accueil():
    stats = db.obtenir_statistiques()
    return render_template("accueil.html", stats=stats)


# ---------------------------------------------------------------------------
# Onglet OPPORTUNITÉS
# ---------------------------------------------------------------------------
@app.route("/opportunites")
def opportunites():
    filtres = {
        "recherche": request.args.get("recherche", ""),
        "ville": request.args.get("ville", ""),
        "statut": request.args.get("statut", ""),
        "source": request.args.get("source", ""),
    }
    liste = db.lister_opportunites(filtres)
    cvs = db.lister_cv()
    return render_template(
        "opportunites.html", opportunites=liste, filtres=filtres,
        statuts=STATUTS_POSSIBLES, cvs=cvs,
    )


@app.route("/opportunites/ajouter", methods=["POST"])
def ajouter_opportunite():
    donnees = {champ: request.form.get(champ, "") for champ in [
        "titre_offre", "entreprise", "lieu", "lien", "source", "date_collecte",
        "date_limite", "niveau_demande", "competences_demandees", "pertinence",
        "priorite", "statut", "date_candidature", "date_relance", "reponse", "remarque",
    ]}
    donnees["cv_id"] = request.form.get("cv_id") or None
    db.ajouter_opportunite(donnees)
    return redirect(url_for("opportunites"))


@app.route("/opportunites/modifier/<int:id_>", methods=["POST"])
def modifier_opportunite(id_):
    donnees = {champ: request.form.get(champ, "") for champ in [
        "titre_offre", "entreprise", "lieu", "lien", "source",
        "date_limite", "niveau_demande", "competences_demandees", "pertinence",
        "priorite", "statut", "date_candidature", "date_relance", "reponse", "remarque",
    ]}
    donnees["cv_id"] = request.form.get("cv_id") or None
    db.modifier_opportunite(id_, donnees)
    return redirect(url_for("opportunites"))


@app.route("/opportunites/supprimer/<int:id_>", methods=["POST"])
def supprimer_opportunite(id_):
    db.supprimer_opportunite(id_)
    return redirect(url_for("opportunites"))


# ---------------------------------------------------------------------------
# Onglet ENTREPRISES
# ---------------------------------------------------------------------------
@app.route("/entreprises")
def entreprises():
    filtres = {
        "recherche": request.args.get("recherche", ""),
        "secteur": request.args.get("secteur", ""),
    }
    liste = db.lister_entreprises(filtres)
    return render_template("entreprises.html", entreprises=liste, filtres=filtres)


# ---------------------------------------------------------------------------
# Onglet CV
# ---------------------------------------------------------------------------
@app.route("/cv")
def cv():
    liste = db.lister_cv()
    return render_template("cv.html", cvs=liste)


@app.route("/cv/ajouter", methods=["POST"])
def ajouter_cv():
    donnees = {champ: request.form.get(champ, "") for champ in [
        "titre", "competences", "experiences", "formation", "chemin_fichier",
    ]}
    db.ajouter_cv(donnees)
    return redirect(url_for("cv"))


@app.route("/cv/supprimer/<int:id_>", methods=["POST"])
def supprimer_cv(id_):
    db.supprimer_cv(id_)
    return redirect(url_for("cv"))


if __name__ == "__main__":
    app.run(debug=True)
