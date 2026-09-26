"""
database.py — Connexion et opérations SQLite.

Important : SQLite ne nécessite PAS de "CREATE DATABASE". Le fichier .db
est créé automatiquement au premier appel à sqlite3.connect(), s'il n'existe pas.
"""
import sqlite3
import os
import pandas as pd

RACINE = os.path.dirname(os.path.abspath(__file__))
CHEMIN_DB = os.path.join(RACINE, "opportunites.db")
CHEMIN_CSV_ENTREPRISES = os.path.join(RACINE, "data", "entreprises.csv")
CHEMIN_CSV_OPPORTUNITES = os.path.join(RACINE, "data", "opportunites.csv")


def get_connection():
    conn = sqlite3.connect(CHEMIN_DB)
    conn.row_factory = sqlite3.Row  # permet d'accéder aux colonnes par nom
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crée les tables si elles n'existent pas encore. Ne touche jamais des tables déjà remplies."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entreprises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_id TEXT UNIQUE,
            nom TEXT NOT NULL,
            adresse TEXT,
            latitude REAL,
            longitude REAL,
            site_web TEXT,
            linkedin TEXT,
            telephone TEXT,
            note REAL,
            nb_avis INTEGER DEFAULT 0,
            type_entreprise TEXT,
            secteur_probable TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cv (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            competences TEXT,
            experiences TEXT,
            formation TEXT,
            chemin_fichier TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS opportunites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre_offre TEXT NOT NULL,
            entreprise TEXT,
            lieu TEXT,
            lien TEXT UNIQUE,
            source TEXT,
            date_collecte TEXT,
            date_limite TEXT,
            niveau_demande TEXT,
            competences_demandees TEXT,
            pertinence TEXT,
            priorite TEXT,
            statut TEXT DEFAULT 'À examiner',
            date_candidature TEXT,
            date_relance TEXT,
            reponse TEXT,
            remarque TEXT,
            cv_id INTEGER,
            FOREIGN KEY (cv_id) REFERENCES cv(id)
        )
    """)

    conn.commit()
    conn.close()


def importer_donnees_initiales():
    """
    Importe data/entreprises.csv et data/opportunites.csv dans la base,
    UNE SEULE FOIS (si les tables sont vides). N'écrase jamais des données
    déjà saisies manuellement dans l'app.
    """
    conn = get_connection()

    nb_entreprises = conn.execute("SELECT COUNT(*) FROM entreprises").fetchone()[0]
    if nb_entreprises == 0 and os.path.exists(CHEMIN_CSV_ENTREPRISES):
        df = pd.read_csv(CHEMIN_CSV_ENTREPRISES, encoding="utf-8-sig")
        for _, row in df.iterrows():
            conn.execute("""
                INSERT OR IGNORE INTO entreprises
                (place_id, nom, adresse, latitude, longitude, site_web, telephone,
                 note, nb_avis, type_entreprise, secteur_probable)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get("place_id"), row.get("nom"), row.get("adresse"),
                row.get("latitude"), row.get("longitude"), row.get("site_web"),
                row.get("telephone"), row.get("note"), int(row.get("nb_avis") or 0),
                row.get("type_entreprise"), row.get("secteur_probable"),
            ))
        print(f"✅ {len(df)} entreprises importées depuis entreprises.csv")

    nb_opportunites = conn.execute("SELECT COUNT(*) FROM opportunites").fetchone()[0]
    if nb_opportunites == 0 and os.path.exists(CHEMIN_CSV_OPPORTUNITES):
        df = pd.read_csv(CHEMIN_CSV_OPPORTUNITES, encoding="utf-8-sig")
        for _, row in df.iterrows():
            conn.execute("""
                INSERT OR IGNORE INTO opportunites
                (titre_offre, entreprise, lieu, lien, source, date_collecte,
                 niveau_demande, competences_demandees, pertinence, priorite,
                 statut, date_candidature, date_relance, reponse, remarque)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get("titre_offre"), row.get("entreprise"), row.get("lieu"),
                row.get("lien"), row.get("source"), row.get("date_collecte"),
                row.get("niveau_demande"), row.get("competences_demandees"),
                row.get("pertinence"), row.get("priorite"),
                row.get("statut") or "À examiner", row.get("date_candidature"),
                row.get("date_relance"), row.get("reponse"), row.get("remarque"),
            ))
        print(f"✅ {len(df)} opportunités importées depuis opportunites.csv")

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# CRUD — Opportunités
# ---------------------------------------------------------------------------
def lister_opportunites(filtres=None):
    filtres = filtres or {}
    conn = get_connection()
    requete = "SELECT o.*, c.titre AS cv_titre FROM opportunites o LEFT JOIN cv c ON o.cv_id = c.id WHERE 1=1"
    params = []

    if filtres.get("recherche"):
        requete += " AND (titre_offre LIKE ? OR entreprise LIKE ?)"
        terme = f"%{filtres['recherche']}%"
        params += [terme, terme]
    if filtres.get("ville"):
        requete += " AND lieu LIKE ?"
        params.append(f"%{filtres['ville']}%")
    if filtres.get("statut"):
        requete += " AND statut = ?"
        params.append(filtres["statut"])
    if filtres.get("source"):
        requete += " AND source = ?"
        params.append(filtres["source"])

    requete += " ORDER BY id DESC"
    rows = conn.execute(requete, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtenir_opportunite(id_):
    conn = get_connection()
    row = conn.execute("SELECT * FROM opportunites WHERE id = ?", (id_,)).fetchone()
    conn.close()
    return dict(row) if row else None


def ajouter_opportunite(donnees: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO opportunites
        (titre_offre, entreprise, lieu, lien, source, date_collecte, date_limite,
         niveau_demande, competences_demandees, pertinence, priorite, statut,
         date_candidature, date_relance, reponse, remarque, cv_id)
        VALUES (:titre_offre, :entreprise, :lieu, :lien, :source, :date_collecte, :date_limite,
                :niveau_demande, :competences_demandees, :pertinence, :priorite, :statut,
                :date_candidature, :date_relance, :reponse, :remarque, :cv_id)
    """, donnees)
    conn.commit()
    conn.close()


def modifier_opportunite(id_, donnees: dict):
    donnees["id"] = id_
    conn = get_connection()
    conn.execute("""
        UPDATE opportunites SET
            titre_offre=:titre_offre, entreprise=:entreprise, lieu=:lieu, lien=:lien,
            source=:source, date_limite=:date_limite, niveau_demande=:niveau_demande,
            competences_demandees=:competences_demandees, pertinence=:pertinence,
            priorite=:priorite, statut=:statut, date_candidature=:date_candidature,
            date_relance=:date_relance, reponse=:reponse, remarque=:remarque, cv_id=:cv_id
        WHERE id=:id
    """, donnees)
    conn.commit()
    conn.close()


def supprimer_opportunite(id_):
    conn = get_connection()
    conn.execute("DELETE FROM opportunites WHERE id = ?", (id_,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# CRUD — Entreprises
# ---------------------------------------------------------------------------
def lister_entreprises(filtres=None):
    filtres = filtres or {}
    conn = get_connection()
    requete = """
        SELECT e.*,
               (SELECT COUNT(*) FROM opportunites o WHERE o.entreprise = e.nom) AS nb_opportunites
        FROM entreprises e WHERE 1=1
    """
    params = []
    if filtres.get("recherche"):
        requete += " AND nom LIKE ?"
        params.append(f"%{filtres['recherche']}%")
    if filtres.get("secteur"):
        requete += " AND secteur_probable = ?"
        params.append(filtres["secteur"])

    requete += " ORDER BY nb_avis DESC"
    rows = conn.execute(requete, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# CRUD — CV
# ---------------------------------------------------------------------------
def lister_cv():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM cv ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ajouter_cv(donnees: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO cv (titre, competences, experiences, formation, chemin_fichier)
        VALUES (:titre, :competences, :experiences, :formation, :chemin_fichier)
    """, donnees)
    conn.commit()
    conn.close()


def supprimer_cv(id_):
    conn = get_connection()
    conn.execute("DELETE FROM cv WHERE id = ?", (id_,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Statistiques
# ---------------------------------------------------------------------------
def obtenir_statistiques():
    conn = get_connection()
    stats = {
        "total_entreprises": conn.execute("SELECT COUNT(*) FROM entreprises").fetchone()[0],
        "total_opportunites": conn.execute("SELECT COUNT(*) FROM opportunites").fetchone()[0],
        "total_cv": conn.execute("SELECT COUNT(*) FROM cv").fetchone()[0],
        "par_statut": [dict(r) for r in conn.execute(
            "SELECT statut, COUNT(*) as total FROM opportunites GROUP BY statut ORDER BY total DESC"
        ).fetchall()],
        "par_secteur": [dict(r) for r in conn.execute(
            "SELECT secteur_probable, COUNT(*) as total FROM entreprises GROUP BY secteur_probable ORDER BY total DESC"
        ).fetchall()],
    }
    conn.close()
    return stats
