# PROGRES - Mini Projet 1 

**Enseignant :** Sébastien Tixeuil  
**Email :** Sebastien.Tixeuil@lip6.fr  

**Réalisé par :** AKZOUN Hafsa et Anishka Selvanathan

**Date de rendu :** 17/10/2025 

## Contexte de Projet

Le relai agit comme un serveur pour le client, et comme un client pour le serveur.Il retransmet toutes les données dans les deux sens.

Client ⇄ [ Relai TCP ] ⇄ Serveur

## Le relai doit maintenant écouter les deux sockets :
* les messages venant du client (et les envoyer au serveur),
* les messages venant du serveur (et les renvoyer au client).

# Exercice 1


# Exercice 2

## Question 1: Relai HTTP avec cache
Le but de cette question est d’implémenter en Python un relais HTTP capable de mettre en cache les réponses aux requêtes GET. Ce relais fait le lien entre un client (un navigateur par exemple) et un serveur HTTP. Lorsqu’un client demande une ressource, le relais la renvoie au serveur la première fois, mémorise la réponse sur le disque puis renvoie dans les requêtes suivantes la réponse directement depuis le cache.

> **Usage** : lance le script 

- Le relai HTTP avec cache, ex: python3 relai_http_cache.py 9000 127.0.0.1 8081
- Le serveur HTTP, ex: python3 serveur_relai_http.py 8081  

> **Relai HTTP avec cache** :

- Le fonctionnement du relai est comme suit:  
Quand un client adresse une requête GET, le relais extrait l’URI(par exemple “/index.html”) demandée et consulte si elle est déjà présente dans son cache Si la réponse correspondante est trouvée et n’est pas expirée (c’est-à-dire si elle a une durée de vie inférieure à 60 secondes), elle est renvoyée au client sans interroger le serveur d’origine. Dans le cas d’une première requête ou si la réponse précédemment enregistrée est périmée, le relais transmet la demande au serveur HTTP et reçoit la réponse. Celle-ci est alors conservée dans le cache et renvoyée au client. Le cache est mémorisé sous forme de **dictionnaire Python**, dans lequel chaque entrée contient **la réponse HTTP complète encodée en base64** (permettant une sauvegarde en fichier JSON) ainsi que l’**horodatage** de cette entrée. Ce cache est ensuite enregistré automatiquement dans un fichier nommé *cache.json*, que le programme recharge lors de son exécution pour récupérer les données préalablement mises en cache.

>Importations:

1. socket → pour la communication réseau (client ↔ serveur).
2. threading → pour gérer plusieurs clients à la fois.
3. sys → pour lire les arguments passés au lancement.
4. re → pour reconnaître les requêtes GET avec une expression régulière.
5. time → pour mesurer l’âge d’un élément dans le cache.
6. json, base64 → pour enregistrer le cache dans un fichier.
7. os → pour vérifier si le fichier de cache existe.

>Fonctions:

**Fonction de gestion client : handle_client()**
- Connexion au vrai serveur (celui vers lequel on veut relayer) ;
- Lecture de la requête du client ;
- Si c’est une requête GET : le relai récupére l’URI demandée puis vérifie si elle est déjà dans le cache. Si oui et encore valable (moins de 60s), le fichier sera envoyer directement la réponse au client. Si expirée, la supprimer du cache ;
- Si pas dans le cache → envoyer la requête au vrai serveur ; recevoir la réponse complète ;
- Stocker cette réponse dans le cache & dans le fichier cache.json ;
- Envoyer la réponse au client ;
- Si ce n’est pas un GET → le relais se contente de faire suivre la requête et la réponse ;
- Fermeture propre des connexions à la fin.

**Fonction relai() Lance le serveur relais**
- Lancement du serveur relais multithreadé ;
- Écoute sur le port choisi.
- Chaque fois qu’un client se connecte : Crée un nouveau thread pour gérer ce client via handle_client().

**Serveur HTTP** :

Le script (serveur_relai_http.py) ci-joint implémente un petit serveur web.
Il écoute sur un certain port et attend des requêtes HTTP, qui sont le plus souvent de type GET,
puis il va analyser la ligne de la requête (par exemple “GET /index.html HTTP/1.1”) pour identifier le fichier demandé.
Les fichiers sont présents dans le dossier “files”, s’il existe, le serveur renvoie une réponse “200 OK” accompagnée du contenu chacun fichier, sinon il renvoie “404 Not Found”.
Dans le cas où le serveur reçoit une requête à la racine “/”, il envoie automatiquement le fichier “index.html”.
Chaque client est traité dans un thread différent ce qui le permet de répondre à plusieurs clients en même temps.

## Question 2: Relai HTTP avec sniffeur:
Cette question a pour but de réaliser en python un **relai HTTP sniffeur**. En effet, le relai interceptera toutes les requêtes GET des clients pour les transmettre au serveur et enregistrer dans un fichier de logs les réponses non vides. Chaque ligne du log contiendra l’IP du client, l’URI demandée, la taille de la réponse ainsi qu’un timestamp.

> **Usage** 

- Pour lancer le relai HTTP avec sniffeur : python3 relai_sniffeur.py <port_relais> <adresse_serveur> <port_serveur>
- Pour rechercher dans le log les clients ayant reçu une réponse pour une URI donnée : python3 recherche_log.py <mot_ou_URI> ex: index.html

> **Relai HTTP avec sniffeur**

- Le fonctionnement du relai avec sniffeur est comme suit: 
Le script élabore un serveur relais multithread, situé entre les clients et le serveur HTTP réel, sur un port donné. Pour chaque client connecté, un thread spécifique est créé, dont le rôle est de gérer la communication entre le client et le serveur. À la réception d’une requête GET, le serveur relais transfert la requête au serveur HTTP, récupère la réponse complète, et si celle-ci n’est pas nulle, il log au format JSON l’adresse IP du client, l’URI demandée, **la taille de la réponse** et **l’horodatage**. C’est enfin cette réponse qui est transmise au client, garantissant ainsi un relais des requêtes effectuées.
Le fichier *http_sniffer_log.json** est utilisé pour stocker toutes les informations de log et est mis à jour de manière thread-safe pour éviter les conflits lors des accès concurrents.

> fonctions :

**Fonction save_log():**
- Sauvegarde le log JSON dans le fichier http_sniffer_log.json ;
- Utilise un verrou (log_lock) pour s’assurer que plusieurs threads n’écrivent pas en même temps.

**Fonction handle_client(socketClient, serverName, serverPort, clientAddr) :**
- Gère la communication entre un client et le serveur HTTP ;
- Reçoit les requêtes du client, en particulier les GET, et transmet la requête au serveur réel ;
- Reçoit la réponse complète du serveur et vérifie si elle est non vide ;
- Si la réponse est non vide, crée une entrée de log avec l’adresse IP, l’URI, la taille de la réponse et l’horodatage ;
- Envoie la réponse au client ;
- Ferme les connexions proprement à la fin de la session.

**Fonction relai_sniffeur(relay_port, server_name, server_port) :**
- Initialise le serveur relais sur le port spécifié ;
- Accepte les connexions entrantes et crée un thread par client pour exécuter handle_client ;
- Gère la fermeture propre du relais en cas d’interruption (Ctrl+C).

**Serveur HTTP :**
Le serveur HTTP reste identique à celui de la question 1 ;

**Recherche dans le log: recherche_log.py** :

Le script lit le fichier de log JSON http_sniffer_log.json et récupère le mot clé ou l’URI passé en ligne commande. Pour chaque entrée, il extrait l’adresse IP du client, l’URI demandée et la taille de la réponse. Si l’URI contient le mot clé et que la réponse n’est pas vide, ces informations sont ajoutées aux résultats qui seront ensuite affichés sous la forme Client → URI (octets). Si aucun résultat ne correspond, cela sera signalé. Le script gère également le cas où le fichier JSON est inexistant ou mal formé.