## Contexte de Projet

Le relai agit comme un serveur pour le client,
et comme un client pour le serveur.
Il retransmet toutes les données dans les deux sens.

Client ⇄ [ Relai TCP ] ⇄ Serveur

## Le relai doit maintenant écouter les deux sockets :
* les messages venant du client (et les envoyer au serveur),
* les messages venant du serveur (et les renvoyer au client).

# Exercice 2
## Question 1:

# Relais HTTP avec cache persistant

**Relai_http_cache.py** :
Script qui implémente un *serveur relais HTTP* interceptant les requêtes du client, relayant la requête au serveur final, et mettant en cache les réponses HTTP GET pour améliorer les performances et réduire la charge sur le réseau.
---

**Usage** : lance le script 

> ex: python3 relai_http_cache.py 9000 127.0.0.1 8081    

**Comment** :  

1. **Relais TCP multi-threadé** :  
   - Écoute sur un port spécifique (relay_port) (par exemple, 9000), et chaque client est géré dans un thread distinct, permettant le traitement simultané des requêtes.

2. **Cache persistant** :  
   - Les réponses des requêtes GET sont stockées dans un fichier JSON permettant leur réutilisation après un redémarrage du relais. Le contenu des réponses est encodé en base64 afin de rester compatible avec le format JSON.

3. **TTL (Time-To-Live)** :  
   - Chaque entrée dans le cache a une durée de vie limitée (60 secondes par défaut). Les réponses expirées sont supprimées et une nouvelle requête est envoyée au serveur pour obtenir une réponse fraîche.

4. **Filtrage des requêtes GET** :  
   - Seules les requêtes GET sont mises en cache. Les requêtes HTTP sont simplement relayées vers le serveur.

5. **Gestion des exceptions** :  
   - Timeout sur la réception des réponses des serveurs pour éviter le blocage. Gestion des erreurs lors de la lecture ou de l’écriture du cache.