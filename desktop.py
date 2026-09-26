"""
desktop.py — Lance l'application comme un vrai programme de bureau,
dans sa propre fenêtre (sans navigateur, sans barre d'adresse).

Fonctionnement : le serveur Flask (app.py) tourne en arrière-plan,
invisible pour toi, et webview affiche son contenu dans une fenêtre native.

Exécution : python desktop.py
"""
import threading
import time
import webview

from app import app

PORT = 5000


def lancer_serveur_flask():
    # use_reloader=False est indispensable : le rechargeur automatique de Flask
    # ne fonctionne pas correctement lancé depuis un thread secondaire.
    app.run(port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    # 1. On démarre Flask en tâche de fond (thread "daemon" : se ferme avec l'appli)
    thread_serveur = threading.Thread(target=lancer_serveur_flask, daemon=True)
    thread_serveur.start()

    # 2. On attend une fraction de seconde que le serveur soit prêt
    time.sleep(1)

    # 3. On ouvre la fenêtre native, qui affiche le contenu de Flask
    webview.create_window(
        title="Suivi Opportunités — Marrakech",
        url=f"http://127.0.0.1:{PORT}",
        width=1300,
        height=850,
        min_size=(900, 600),
    )
    webview.start()
