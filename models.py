"""
models.py — Structures de données du projet.

Les colonnes ci-dessous correspondent EXACTEMENT à celles présentes dans
Projet_Marrakech_Final.xlsx (onglets CLEAN_Entreprises et TRACKING),
pour ne pas avoir à retraiter tes données existantes.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Entreprise:
    id: Optional[int] = None
    place_id: str = ""
    nom: str = ""
    adresse: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    site_web: str = ""
    linkedin: str = ""          # non collecté à ce stade — laissé vide, à compléter manuellement
    telephone: str = ""
    note: Optional[float] = None
    nb_avis: int = 0
    type_entreprise: str = ""   # "Startup" / "Entreprise établie"
    secteur_probable: str = ""  # "IA / Data" / "Fintech" / "Autre tech"


@dataclass
class Opportunite:
    id: Optional[int] = None
    titre_offre: str = ""
    entreprise: str = ""
    lieu: str = ""
    lien: str = ""
    source: str = ""
    date_collecte: str = ""
    date_limite: str = ""              # à compléter manuellement si connue
    niveau_demande: str = ""
    competences_demandees: str = ""
    pertinence: str = ""
    priorite: str = ""
    statut: str = "À examiner"
    date_candidature: str = ""
    date_relance: str = ""
    reponse: str = ""
    remarque: str = ""
    cv_id: Optional[int] = None        # lien vers le CV utilisé pour candidater


@dataclass
class CV:
    id: Optional[int] = None
    titre: str = ""             # ex: "CV Data Analyst - v2"
    competences: str = ""
    experiences: str = ""
    formation: str = ""
    chemin_fichier: str = ""    # chemin local vers le PDF/Word, si stocké


STATUTS_POSSIBLES = [
    "À examiner", "À candidater", "Candidature préparée", "Candidature envoyée",
    "Relance à faire", "Entretien", "Accepté", "Refusé", "Archivé",
]
