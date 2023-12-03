# **BiblioTech**

## **Description générale**
Au sein de l'unité d'études Fullstack, nous avons développé une application offrant aux utilisateurs la possibilité de rechercher des livres, de les intégrer à leur liste de lecture personnelle, et d'explorer les lectures partagées par d'autres utilisateurs. Notre architecture utilise des conteneurs Docker pour garantir une mise en œuvre efficace et cohérente. Ces conteneurs contiennent les composants suivants :

* **Base de données (BDD)** : PostgreSQL, assurant une gestion robuste des données.

* **Keycloak** : Un système d'authentification sécurisé, facilitant la gestion des accès à l'application.

* **API** : FastAPI, fournissant une interface rapide et performante pour la communication avec la base de données.

* **Application Frontend** : Développée avec le framework Dash, offrant une expérience utilisateur interactive pour la recherche, l'ajout de livres à la liste de lecture, et la visualisation des lectures des autres utilisateurs.

## **Données utilisées**

Dans le cadre de notre projet Fullstack, nous avons utilisé un jeu de données provenant de Kaggle, accessible [ici](https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks). Ce fichier CSV renferme des informations détaillées sur les livres que nous explorons au sein de notre application. Il est à noter que lors de l'exploration initiale du jeu de données, nous avons rencontré des défis liés à la présence de virgules au sein de certaines lignes du fichier CSV. Afin de garantir une intégration correcte de ces données dans notre application, nous avons pris l'initiative de modifier le fichier.

La description complète de chaque colonne du dataset est disponible sur Kaggle.

## **Installation**
1. Clonez le dépôt :
```
$ git clone https://github.com/ton-utilisateur/ton-projet.git
```
2. Accédez au répertoire du projet : 
```
$ cd chemin/de/votre/projet
```
3. Construisez et lancez les conteneurs Docker de l'API, la base de données, et du front-end :
```
$ docker-compose build (si première fois)
$ docker-compose up
```

## **Utilisation**
L'utilisation de l'application se divise en trois tableaux distincts :

**1. Tableau Principal (Tous les Livres)** :
  * Affiche l'ensemble des livres disponibles.
  * Permet une recherche aisée par noms ou auteurs.
  * C'est ici que vous sélectionnez les livres que vous souhaitez ajouter à votre liste de lecture.

**2. Tableau de la liste de lecture personnelle** :
* Contient la liste des livres que vous avez ajoutés personnellement.
* Vous permet de gérer votre collection de livres choisis.

**3. Tableau avec Modal DBC (Liste de lecture des utilisateurs)** :
* Associé à un modal DBC (Dialogue Box Component) pour la sélection d'un utilisateur.
* Vous permet de visualiser la liste de lecture d'un autre utilisateur en sélectionnant son nom dans le modal.

Cette structuration en trois tableaux permet la constitution de votre liste de lecture personnelle, et l'exploration des lectures d'autres utilisateurs.


Vous pouvez accéder à l'API et au FRONT avec les liens suivants:
* API: [localhost:5000](http://localhost:5000/)
* FRONT: [localhost:8050](http://localhost:8050/)


