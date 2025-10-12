## Contexte de Projet

Le relai agit comme un serveur pour le client,
et comme un client pour le serveur.
Il retransmet toutes les données dans les deux sens.

Client ⇄ [ Relai TCP ] ⇄ Serveur

## Le relai doit maintenant écouter les deux sockets :
* les messages venant du client (et les envoyer au serveur),
* les messages venant du serveur (et les renvoyer au client).