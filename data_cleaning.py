"""
data_cleaning.py — Nettoyage et validation automatique.

Appelé automatiquement au démarrage de l'app (voir app.py) pour garantir
que les données importées sont propres, sans dupliquer le gros travail de
nettoyage manuel déjà fait dans le notebook Colab.
"""
import re
from database import get_connection


def normaliser_texte(valeur):
    """Retire les espaces superflus et les espaces en double."""
    if valeur is None:
        return valeur
    return re.sub(r"\s+", " ", str(valeur).strip())


def detecter_doublons_opportunites():
    """Détecte les opportunités en double sur le champ 'lien' (identifiant unique naturel)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT lien, COUNT(*) as total FROM opportunites
        WHERE lien IS NOT NULL AND lien != ''
        GROUP BY lien HAVING total > 1
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def supprimer_doublons_opportunites():
    """Garde uniquement la première occurrence de chaque lien en doublon."""
    conn = get_connection()
    conn.execute("""
        DELETE FROM opportunites
        WHERE id NOT IN (
            SELECT MIN(id) FROM opportunites GROUP BY lien
        )
    """)
    nb_supprimees = conn.total_changes
    conn.commit()
    conn.close()
    return nb_supprimees


def normaliser_champs_texte():
    """Nettoie les espaces superflus dans les champs texte principaux des deux tables."""
    conn = get_connection()

    opportunites = conn.execute("SELECT id, titre_offre, entreprise, lieu FROM opportunites").fetchall()
    for o in opportunites:
        conn.execute(
            "UPDATE opportunites SET titre_offre=?, entreprise=?, lieu=? WHERE id=?",
            (normaliser_texte(o["titre_offre"]), normaliser_texte(o["entreprise"]),
             normaliser_texte(o["lieu"]), o["id"]),
        )

    entreprises = conn.execute("SELECT id, nom, adresse FROM entreprises").fetchall()
    for e in entreprises:
        conn.execute(
            "UPDATE entreprises SET nom=?, adresse=? WHERE id=?",
            (normaliser_texte(e["nom"]), normaliser_texte(e["adresse"]), e["id"]),
        )

    conn.commit()
    conn.close()


def verifier_champs_obligatoires():
    """
    Vérifie les champs obligatoires (titre_offre pour une opportunité, nom pour une entreprise).
    Retourne la liste des lignes problématiques (n'efface rien automatiquement,
    car un champ vide sur une donnée déjà saisie manuellement doit être vérifié par l'utilisateur).
    """
    conn = get_connection()
    problemes = []

    for row in conn.execute("SELECT id, titre_offre FROM opportunites").fetchall():
        if not row["titre_offre"] or not str(row["titre_offre"]).strip():
            problemes.append({"table": "opportunites", "id": row["id"], "probleme": "titre_offre manquant"})

    for row in conn.execute("SELECT id, nom FROM entreprises").fetchall():
        if not row["nom"] or not str(row["nom"]).strip():
            problemes.append({"table": "entreprises", "id": row["id"], "probleme": "nom manquant"})

    conn.close()
    return problemes


def executer_nettoyage_complet():
    """Point d'entrée unique : appelé au démarrage de l'app pour tout nettoyer d'un coup."""
    doublons = detecter_doublons_opportunites()
    if doublons:
        nb = supprimer_doublons_opportunites()
        print(f"🧹 {len(doublons)} lien(s) en doublon détecté(s), lignes en trop supprimées.")

    normaliser_champs_texte()

    problemes = verifier_champs_obligatoires()
    if problemes:
        print(f"⚠️ {len(problemes)} ligne(s) avec un champ obligatoire manquant (non supprimées automatiquement) :")
        for p in problemes:
            print(f"   - {p['table']} #{p['id']} : {p['probleme']}")
    else:
        print("✅ Aucun champ obligatoire manquant détecté.")
