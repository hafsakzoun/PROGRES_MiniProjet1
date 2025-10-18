# Les prompts LLM utilisés

## Exercice 1: 
1. - Mon serveur se ferme après avoir traité une seule requête. Je voudrais comprendre pourquoi et savoir comment permettre à plusieurs clients de se connecter simultanément sur le même serveur. Est-ce que l’ajout d’une boucle while dans la fonction handle_client() est la bonne solution, ou faut-il aussi adapter la logique du serveur principal ?

## Exercice 2: 
1. - Prompt: J’ai un relais TCP multithread et un serveur simple. Je voudrais gérer plusieurs clients : est-ce qu’il suffit que le relais soit multithread, ou faut-il aussi que le serveur le soit ?
    - réponse: 
    Pour gérer plusieurs clients en même temps, le serveur et le relais doivent tous les deux être capables de traiter plusieurs connexions simultanément.

2. -J’ai fait un relai HTTP multithreadé en Python avec un système de cache qui intercepte les requêtes GET, vérifie si la réponse est déjà en cache et sinon la récupère du serveur. Le code marche bien, mais je veux l’améliorer pour le rendre plus complet et plus propre. J’aimerais que le cache soit sauvegardé dans un fichier JSON pour être persistant, ajouter un TTL pour supprimer les anciennes entrées automatiquement, gérer le Content-Type des réponses et améliorer la gestion des erreurs et des connexions sans changer la logique principale

3. - J’ai fait un relai HTTP multithreadé qui joue le rôle de sniffeur et enregistre les requêtes GET dans un fichier JSON. Le code marche, mais je veux l’améliorer un peu meilleure gestion du log (thread-safe), messages plus clairs, et un code plus propre sans changer la logique principale. Peux-tu m’aider à le réorganiser ?

4.  - Comment savoir si une requête est une requête GET ou non en python? 
    -> if msg.startswith("GET")
